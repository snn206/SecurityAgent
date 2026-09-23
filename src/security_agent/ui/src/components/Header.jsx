import React from 'react';

export default function Header({ activeTab, setActiveTab, systemStatus, activeExecutionCount }) {
  const tabs = [
    { id: 'overview', label: 'OVERVIEW' },
    { id: 'new-task', label: 'NEW MISSION' },
    { id: 'monitor', label: 'LIVE MONITOR' },
    { id: 'executions', label: 'EXECUTIONS' },
    { id: 'providers', label: 'PROVIDERS' },
    { id: 'tools', label: 'TOOL REGISTRY' },
    { id: 'memory', label: 'MEMORY & BRAIN' },
  ];

  const isOnline = systemStatus?.status === 'ok' || systemStatus?.status === 'healthy';

  return (
    <header className="top-bar">
      <div className="brand-section">
        <div className="brand-title">
          <span className="accent">//</span> SECURITY_AGENT
          <span className="system-tag">v0.1.0</span>
        </div>
      </div>

      <nav className="nav-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <div className="telemetry-status">
        <span className={`status-dot ${isOnline ? 'online' : 'error'}`} />
        <span>{isOnline ? 'API ONLINE' : 'API OFFLINE'}</span>
        {activeExecutionCount > 0 && (
          <span className="badge badge-cyan" style={{ marginLeft: 8 }}>
            {activeExecutionCount} ACTIVE
          </span>
        )}
      </div>
    </header>
  );
}
