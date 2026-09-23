import React from 'react';

export default function OverviewTab({ executions, providers, tools, onLaunchPreset, onSelectExecution, onNavigate }) {
  const activeCount = executions.filter(e => e.status === 'running').length;
  const completedCount = executions.filter(e => e.status === 'completed').length;
  const configuredProviders = providers.filter(p => p.configured !== false).length;

  const agentNodes = [
    { name: 'SUPERVISOR', role: 'Mission Planner & Coordinator', desc: 'LangGraph state orchestrator' },
    { name: 'RECON AGENT', role: 'Surface Discovery & OSINT', desc: 'Port scanning, DNS, subdomains' },
    { name: 'VULN AGENT', role: 'Weakness Identification', desc: 'Nikto, Nuclei, CVE matching' },
    { name: 'EXPLOIT AGENT', role: 'PoC & Validation (Sandbox)', desc: 'Controlled PoC verification' },
    { name: 'REPORT AGENT', role: 'Synthesis & Documentation', desc: 'Executive & technical output' },
  ];

  const presets = [
    {
      title: 'EXTERNAL PERIMETER RECON',
      target: '192.168.1.0/24',
      objective: 'Discover live hosts, open ports, and banner services across external subnet.',
      strategy: 'hierarchical',
      tools: ['nmap', 'gobuster'],
    },
    {
      title: 'WEB APPLICATION AUDIT',
      target: 'https://example.internal',
      objective: 'Analyze web application headers, crawl endpoints, test for OWASP Top 10 vulnerabilities.',
      strategy: 'plan_and_execute',
      tools: ['nikto', 'nuclei', 'gobuster'],
    },
    {
      title: 'DEEP AUTONOMOUS VULNERABILITY AUDIT',
      target: 'target.lab.local',
      objective: 'Full autonomous security research from perimeter reconnaissance to vulnerability verification.',
      strategy: 'autonomous',
      tools: ['nmap', 'gobuster', 'nikto', 'sqlmap', 'nuclei', 'searchsploit'],
    },
  ];

  return (
    <div>
      {/* ── Top Telemetry Row ────────────────────────────────────────── */}
      <div className="metrics-row">
        <div className="metric-box">
          <div className="metric-label">// ACTIVE MISSIONS</div>
          <div className={`metric-value ${activeCount > 0 ? 'cyan' : ''}`}>{activeCount}</div>
        </div>
        <div className="metric-box">
          <div className="metric-label">// COMPLETED RUNS</div>
          <div className="metric-value green">{completedCount}</div>
        </div>
        <div className="metric-box">
          <div className="metric-label">// AI PROVIDERS READY</div>
          <div className="metric-value">{configuredProviders} / {providers.length || 10}</div>
        </div>
        <div className="metric-box">
          <div className="metric-label">// LOADED TOOLS</div>
          <div className="metric-value amber">{tools.length || 7}</div>
        </div>
      </div>

      {/* ── 10-Agent Hierarchical Architecture & Task Queue ──────────── */}
      <div className="cyber-card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div className="card-title">
            <span className="prefix">[BRAIN]</span> 10-AGENT HIERARCHICAL BRAIN TOPOLOGY
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <span className="system-tag">SYSTEM CAP: 10 AGENTS MAX (1 + 3 + 6)</span>
            <span className="badge badge-cyan">QUEUE: 3 ACTIVE SLOTS</span>
          </div>
        </div>

        {/* Level 1: Grandparent Coordinator (Ông) */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 16 }}>
          <div
            style={{
              background: 'var(--bg-input)',
              border: '1px solid var(--accent-cyan)',
              borderRadius: 'var(--radius-sm)',
              padding: '12px 24px',
              textAlign: 'center',
              minWidth: 280,
              boxShadow: '0 0 12px rgba(0, 229, 255, 0.12)',
            }}
          >
            <span className="badge badge-cyan" style={{ marginBottom: 4 }}>
              COORDINATOR [ONG] (1 ACTIVE)
            </span>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: 'var(--text-main)' }}>
              Master Security Dispatcher
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 2 }}>
              Breaks mission goals, orders parent leads, monitors JEV loop
            </div>
          </div>
        </div>

        <div style={{ textAlign: 'center', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)', fontSize: 12, marginBottom: 8 }}>
          &darr; DISPATCHES &amp; ENQUEUES (IF &gt; 3 TASKS &rarr; QUEUE) &darr;
        </div>

        {/* Level 2 & 3: 3 Parent Leads (Cha), each with up to 2 Children (Con) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
          {/* Parent 1 */}
          <div style={{ background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span className="badge badge-green">PARENT 1 [CHA]</span>
              <span className="mono" style={{ fontSize: 10, color: 'var(--text-dim)' }}>SLOT #1 ACTIVE</span>
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: 'var(--text-main)', marginBottom: 4 }}>
              Reconnaissance Lead
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 12 }}>
              Coordinates surface mapping, DNS resolution, port scanning
            </div>

            {/* Children of Parent 1 */}
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 10 }}>
              <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', marginBottom: 6 }}>
                CHILDREN [CON] (MAX 2):
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <div style={{ background: '#05080e', padding: '6px 10px', borderRadius: 4, display: 'flex', justifyContent: 'space-between', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                  <span>&bull; Port Scanner Worker</span>
                  <span className="badge badge-muted">NMAP</span>
                </div>
                <div style={{ background: '#05080e', padding: '6px 10px', borderRadius: 4, display: 'flex', justifyContent: 'space-between', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                  <span>&bull; Subdomain/URI Worker</span>
                  <span className="badge badge-muted">GOBUSTER</span>
                </div>
              </div>
            </div>
          </div>

          {/* Parent 2 */}
          <div style={{ background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span className="badge badge-green">PARENT 2 [CHA]</span>
              <span className="mono" style={{ fontSize: 10, color: 'var(--text-dim)' }}>SLOT #2 ACTIVE</span>
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: 'var(--text-main)', marginBottom: 4 }}>
              Vulnerability Lead
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 12 }}>
              Coordinates web security audits, CVE correlation, misconfigurations
            </div>

            {/* Children of Parent 2 */}
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 10 }}>
              <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', marginBottom: 6 }}>
                CHILDREN [CON] (MAX 2):
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <div style={{ background: '#05080e', padding: '6px 10px', borderRadius: 4, display: 'flex', justifyContent: 'space-between', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                  <span>&bull; Template Matcher</span>
                  <span className="badge badge-muted">NUCLEI</span>
                </div>
                <div style={{ background: '#05080e', padding: '6px 10px', borderRadius: 4, display: 'flex', justifyContent: 'space-between', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                  <span>&bull; Web Server Auditor</span>
                  <span className="badge badge-muted">NIKTO</span>
                </div>
              </div>
            </div>
          </div>

          {/* Parent 3 */}
          <div style={{ background: 'var(--bg-input)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span className="badge badge-green">PARENT 3 [CHA]</span>
              <span className="mono" style={{ fontSize: 10, color: 'var(--text-dim)' }}>SLOT #3 ACTIVE</span>
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: 'var(--text-main)', marginBottom: 4 }}>
              Exploit &amp; PoC Lead
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 12 }}>
              Coordinates proof-of-concept verification in isolated Kali sandbox
            </div>

            {/* Children of Parent 3 */}
            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 10 }}>
              <div style={{ fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-dim)', marginBottom: 6 }}>
                CHILDREN [CON] (MAX 2):
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <div style={{ background: '#05080e', padding: '6px 10px', borderRadius: 4, display: 'flex', justifyContent: 'space-between', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                  <span>&bull; PoC Verifier Worker</span>
                  <span className="badge badge-muted">SANDBOX</span>
                </div>
                <div style={{ background: '#05080e', padding: '6px 10px', borderRadius: 4, display: 'flex', justifyContent: 'space-between', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                  <span>&bull; Payload Injection Worker</span>
                  <span className="badge badge-muted">SQLMAP</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Quick Launch Presets ─────────────────────────────────────── */}
      <div className="cyber-card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div className="card-title">
            <span className="prefix">[FAST]</span> RAPID MISSION LAUNCH TEMPLATES
          </div>
          <button className="btn btn-secondary" onClick={() => onNavigate('new-task')}>
            CUSTOM MISSION &rarr;
          </button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
          {presets.map((preset) => (
            <div
              key={preset.title}
              style={{
                background: 'var(--bg-input)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: 16,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: 8 }}>
                  {preset.title}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>
                  {preset.objective}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 16 }}>
                  <span className="badge badge-muted">STRATEGY: {preset.strategy}</span>
                  {preset.tools.map((t) => (
                    <span key={t} className="badge badge-cyan">{t}</span>
                  ))}
                </div>
              </div>
              <button
                className="btn btn-primary"
                style={{ width: '100%' }}
                onClick={() => onLaunchPreset(preset)}
              >
                DEPLOY MISSION &rarr;
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* ── Recent Activity ─────────────────────────────────────────── */}
      <div className="cyber-card">
        <div className="card-header">
          <div className="card-title">
            <span className="prefix">[LOG]</span> RECENT EXECUTIONS
          </div>
          <button className="btn btn-secondary" onClick={() => onNavigate('executions')}>
            VIEW ALL ({executions.length})
          </button>
        </div>
        {executions.length === 0 ? (
          <div style={{ padding: '32px 0', textAlign: 'center', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            NO EXECUTIONS LOGGED. LAUNCH A MISSION ABOVE.
          </div>
        ) : (
          <div className="table-container">
            <table className="cyber-table">
              <thead>
                <tr>
                  <th>EXECUTION ID</th>
                  <th>TARGET</th>
                  <th>STRATEGY</th>
                  <th>STATUS</th>
                  <th>STARTED</th>
                  <th>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {executions.slice(0, 5).map((exec) => (
                  <tr key={exec.id}>
                    <td className="mono" style={{ color: 'var(--accent-cyan)' }}>{exec.id.slice(0, 12)}...</td>
                    <td>{exec.target || 'N/A'}</td>
                    <td><span className="badge badge-muted">{exec.strategy || 'react'}</span></td>
                    <td>
                      <span className={`badge ${
                        exec.status === 'completed' ? 'badge-green' :
                        exec.status === 'running' ? 'badge-cyan' :
                        exec.status === 'failed' ? 'badge-red' : 'badge-muted'
                      }`}>
                        {exec.status?.toUpperCase() || 'UNKNOWN'}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-dim)' }}>
                      {exec.created_at ? new Date(exec.created_at).toLocaleTimeString() : 'N/A'}
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '4px 10px', fontSize: 11 }}
                        onClick={() => onSelectExecution(exec.id)}
                      >
                        MONITOR &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
