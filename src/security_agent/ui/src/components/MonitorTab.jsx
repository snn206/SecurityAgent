import React, { useState, useEffect, useRef } from 'react';
import { fetchExecution, abortExecution, fetchReport } from '../api';

export default function MonitorTab({ selectedExecutionId, executions, onSelectExecution }) {
  const [execution, setExecution] = useState(null);
  const [logs, setLogs] = useState([]);
  const [findings, setFindings] = useState([]);
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [activeTabSub, setActiveTabSub] = useState('events'); // events | terminal | findings | report
  const [rawReport, setRawReport] = useState(null);
  const [isAborting, setIsAborting] = useState(false);

  const wsRef = useRef(null);
  const terminalBottomRef = useRef(null);

  // Load initial execution details
  useEffect(() => {
    if (!selectedExecutionId) return;

    let isMounted = true;
    fetchExecution(selectedExecutionId)
      .then((data) => {
        if (!isMounted) return;
        setExecution(data);
        if (data.findings) setFindings(data.findings);
        if (data.events) {
          setLogs(data.events.map(ev => ({
            time: ev.timestamp || new Date().toISOString(),
            source: ev.agent_name || ev.agent || 'SYSTEM',
            type: ev.event_type || 'info',
            message: ev.message || JSON.stringify(ev.data || ev),
          })));
        }
      })
      .catch((err) => {
        console.error('Failed to load execution:', err);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedExecutionId]);

  // Connect WebSocket / fallback to stream
  useEffect(() => {
    if (!selectedExecutionId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${selectedExecutionId}`;

    setWsStatus('connecting');
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsStatus('connected');
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const newLog = {
          time: payload.timestamp || new Date().toISOString(),
          source: payload.agent_name || payload.agent || 'AGENT',
          type: payload.event_type || 'event',
          message: payload.message || (typeof payload.data === 'string' ? payload.data : JSON.stringify(payload.data)),
        };

        setLogs(prev => [...prev, newLog]);

        if (payload.event_type === 'finding_discovered' && payload.finding) {
          setFindings(prev => [...prev, payload.finding]);
        }

        if (payload.status) {
          setExecution(prev => prev ? { ...prev, status: payload.status } : null);
        }
      } catch (err) {
        setLogs(prev => [
          ...prev,
          { time: new Date().toISOString(), source: 'RAW', type: 'text', message: event.data },
        ]);
      }
    };

    ws.onerror = () => {
      setWsStatus('error');
    };

    ws.onclose = () => {
      setWsStatus('closed');
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
  }, [selectedExecutionId]);

  // Auto-scroll terminal
  useEffect(() => {
    terminalBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleAbort = async () => {
    if (!selectedExecutionId) return;
    setIsAborting(true);
    try {
      await abortExecution(selectedExecutionId);
      setExecution(prev => prev ? { ...prev, status: 'aborted' } : null);
    } catch (err) {
      alert(`Abort failed: ${err.message}`);
    } finally {
      setIsAborting(false);
    }
  };

  const handleLoadReport = async (format) => {
    if (!selectedExecutionId) return;
    try {
      const data = await fetchReport(selectedExecutionId, format);
      setRawReport({ format, content: typeof data === 'object' ? JSON.stringify(data, null, 2) : data });
      setActiveTabSub('report');
    } catch (err) {
      alert(`Could not fetch report: ${err.message}`);
    }
  };

  if (!selectedExecutionId) {
    return (
      <div className="cyber-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, color: 'var(--text-dim)', marginBottom: 16 }}>
          // NO EXECUTION SELECTED FOR LIVE MONITORING
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 10 }}>
          {executions.length > 0 ? (
            <select
              className="form-select"
              style={{ maxWidth: 360 }}
              onChange={(e) => onSelectExecution(e.target.value)}
              defaultValue=""
            >
              <option value="" disabled>-- Select Execution to Inspect --</option>
              {executions.map(e => (
                <option key={e.id} value={e.id}>
                  {e.id.slice(0, 8)} - {e.target} ({e.status})
                </option>
              ))}
            </select>
          ) : (
            <span className="badge badge-muted">NO PAST EXECUTIONS AVAILABLE</span>
          )}
        </div>
      </div>
    );
  }

  const status = execution?.status || 'running';

  return (
    <div>
      {/* ── Top Bar: Execution Status & Controls ─────────────────────── */}
      <div className="cyber-card" style={{ marginBottom: 16, padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <span className="mono" style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-main)' }}>
                TARGET: {execution?.target || '127.0.0.1'}
              </span>
              <span className={`badge ${
                status === 'completed' ? 'badge-green' :
                status === 'running' ? 'badge-cyan' :
                status === 'failed' ? 'badge-red' : 'badge-muted'
              }`}>
                {status.toUpperCase()}
              </span>
              <span className="badge badge-muted">
                WS: {wsStatus.toUpperCase()}
              </span>
            </div>
            <div className="mono" style={{ fontSize: 11, color: 'var(--text-dim)' }}>
              EXECUTION_ID: {selectedExecutionId} | STRATEGY: {execution?.strategy || 'plan_and_execute'}
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <button
              className="btn btn-secondary"
              onClick={() => handleLoadReport('markdown')}
            >
              EXPORT REPORT [MD]
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => handleLoadReport('json')}
            >
              EXPORT [JSON]
            </button>
            {status === 'running' && (
              <button
                className="btn btn-danger"
                disabled={isAborting}
                onClick={handleAbort}
              >
                {isAborting ? 'ABORTING...' : 'ABORT MISSION'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── View Subtabs ────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 16 }}>
        <button
          className={`nav-tab-btn ${activeTabSub === 'events' ? 'active' : ''}`}
          onClick={() => setActiveTabSub('events')}
        >
          MISSION LOG ({logs.length})
        </button>
        <button
          className={`nav-tab-btn ${activeTabSub === 'findings' ? 'active' : ''}`}
          onClick={() => setActiveTabSub('findings')}
        >
          FINDINGS ({findings.length})
        </button>
        {rawReport && (
          <button
            className={`nav-tab-btn ${activeTabSub === 'report' ? 'active' : ''}`}
            onClick={() => setActiveTabSub('report')}
          >
            REPORT VIEWER [{rawReport.format.toUpperCase()}]
          </button>
        )}
      </div>

      {/* ── Tab Content: Live Logs / Events ─────────────────────────── */}
      {activeTabSub === 'events' && (
        <div className="terminal-window">
          <div className="terminal-header">
            <span>LIVE AGENT STREAM // {selectedExecutionId}</span>
            <span className="mono">{logs.length} EVENTS RECORDED</span>
          </div>
          <div className="terminal-body">
            {logs.length === 0 ? (
              <div style={{ color: 'var(--text-dim)', textAlign: 'center', padding: '30px 0' }}>
                WAITING FOR INCOMING TELEMETRY STREAM...
              </div>
            ) : (
              logs.map((log, idx) => (
                <div key={idx} className="log-entry">
                  <span className="log-time">{log.time.slice(11, 19)}</span>
                  <span className="log-source">[{log.source.toUpperCase()}]</span>
                  <span className="log-msg">{log.message}</span>
                </div>
              ))
            )}
            <div ref={terminalBottomRef} />
          </div>
        </div>
      )}

      {/* ── Tab Content: Findings List ──────────────────────────────── */}
      {activeTabSub === 'findings' && (
        <div className="cyber-card">
          <div className="card-header">
            <div className="card-title">
              <span className="prefix">[THREAT]</span> DISCOVERED SECURITY FINDINGS
            </div>
            <span className="system-tag">{findings.length} TOTAL DETECTED</span>
          </div>
          {findings.length === 0 ? (
            <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
              NO VULNERABILITIES OR FINDINGS REPORTED YET.
            </div>
          ) : (
            findings.map((f, idx) => {
              const sev = (f.severity || 'info').toLowerCase();
              return (
                <div key={idx} className={`finding-card ${sev}`}>
                  <div className="finding-header">
                    <div className="finding-title">{f.title || f.name || `Finding #${idx + 1}`}</div>
                    <span className={`badge ${
                      sev === 'critical' ? 'badge-red' :
                      sev === 'high' ? 'badge-amber' :
                      sev === 'medium' ? 'badge-muted' : 'badge-green'
                    }`}>
                      {sev.toUpperCase()}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', margin: '6px 0' }}>
                    {f.description || 'No description provided.'}
                  </div>
                  {f.proof && (
                    <div style={{ background: '#05080e', padding: '6px 10px', borderRadius: 4, fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-mono)' }}>
                      PROOF: {f.proof}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}

      {/* ── Tab Content: Report Viewer ──────────────────────────────── */}
      {activeTabSub === 'report' && rawReport && (
        <div className="cyber-card">
          <div className="card-header">
            <div className="card-title">
              <span className="prefix">[DOC]</span> GENERATED SECURITY ASSESSMENT REPORT
            </div>
            <button className="btn btn-secondary" onClick={() => setActiveTabSub('events')}>
              CLOSE REPORT
            </button>
          </div>
          <pre style={{
            background: '#05080e',
            padding: 16,
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-mono)',
            fontSize: 12,
            overflowX: 'auto',
            maxHeight: 500,
            whiteSpace: 'pre-wrap'
          }}>
            {rawReport.content}
          </pre>
        </div>
      )}
    </div>
  );
}
