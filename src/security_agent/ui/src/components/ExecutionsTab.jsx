import React, { useState } from 'react';

export default function ExecutionsTab({ executions, onSelectExecution, onRefresh }) {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [selectedExecDetail, setSelectedExecDetail] = useState(null);

  const filtered = executions.filter((e) => {
    if (filter !== 'all' && e.status !== filter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      return (
        e.id?.toLowerCase().includes(q) ||
        e.target?.toLowerCase().includes(q) ||
        e.strategy?.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div>
      <div className="cyber-card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">
            <span className="prefix">[HIST]</span> SECURITY MISSION ARCHIVES
          </div>
          <button className="btn btn-secondary" onClick={onRefresh}>
            REFRESH
          </button>
        </div>

        {/* Filter & Search Bar */}
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center', marginBottom: 16 }}>
          <input
            type="text"
            className="form-input"
            style={{ maxWidth: 300 }}
            placeholder="Search by Target, ID or Strategy..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <div style={{ display: 'flex', gap: 4 }}>
            {['all', 'running', 'completed', 'failed', 'aborted'].map((f) => (
              <button
                key={f}
                className={`nav-tab-btn ${filter === f ? 'active' : ''}`}
                style={{ padding: '6px 12px', fontSize: 11 }}
                onClick={() => setFilter(f)}
              >
                {f.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Data Table */}
        <div className="table-container">
          <table className="cyber-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>TARGET</th>
                <th>STRATEGY</th>
                <th>STATUS</th>
                <th>FINDINGS</th>
                <th>TIMESTAMP</th>
                <th>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '36px 0', color: 'var(--text-dim)' }}>
                    NO RECORDS MATCHING QUERY
                  </td>
                </tr>
              ) : (
                filtered.map((item) => (
                  <tr key={item.id}>
                    <td className="mono" style={{ color: 'var(--accent-cyan)' }}>
                      {item.id.slice(0, 10)}...
                    </td>
                    <td style={{ fontWeight: 600 }}>{item.target || 'N/A'}</td>
                    <td>
                      <span className="badge badge-muted">{item.strategy || 'react'}</span>
                    </td>
                    <td>
                      <span className={`badge ${
                        item.status === 'completed' ? 'badge-green' :
                        item.status === 'running' ? 'badge-cyan' :
                        item.status === 'failed' ? 'badge-red' : 'badge-muted'
                      }`}>
                        {item.status?.toUpperCase() || 'UNKNOWN'}
                      </span>
                    </td>
                    <td className="mono">{item.findings_count || (item.findings ? item.findings.length : 0)}</td>
                    <td style={{ color: 'var(--text-dim)' }}>
                      {item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button
                          className="btn btn-primary"
                          style={{ padding: '4px 10px', fontSize: 11 }}
                          onClick={() => onSelectExecution(item.id)}
                        >
                          MONITOR
                        </button>
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '4px 10px', fontSize: 11 }}
                          onClick={() => setSelectedExecDetail(item)}
                        >
                          DETAILS
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail inspection modal */}
      {selectedExecDetail && (
        <div className="modal-overlay" onClick={() => setSelectedExecDetail(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="card-title">
                <span className="prefix">[META]</span> MISSION DETAILS: {selectedExecDetail.id}
              </div>
              <button className="btn btn-secondary" onClick={() => setSelectedExecDetail(null)}>
                CLOSE
              </button>
            </div>
            <div className="modal-body">
              <pre style={{
                background: '#05080e',
                padding: 16,
                borderRadius: 'var(--radius-sm)',
                color: 'var(--accent-cyan)',
                fontFamily: 'var(--font-mono)',
                fontSize: 12,
                overflowX: 'auto',
                whiteSpace: 'pre-wrap'
              }}>
                {JSON.stringify(selectedExecDetail, null, 2)}
              </pre>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-primary"
                onClick={() => {
                  const id = selectedExecDetail.id;
                  setSelectedExecDetail(null);
                  onSelectExecution(id);
                }}
              >
                OPEN IN LIVE MONITOR &rarr;
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
