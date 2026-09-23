import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import OverviewTab from './components/OverviewTab';
import NewTaskTab from './components/NewTaskTab';
import MonitorTab from './components/MonitorTab';
import ExecutionsTab from './components/ExecutionsTab';
import ProvidersTab from './components/ProvidersTab';
import ToolsTab from './components/ToolsTab';
import MemoryTab from './components/MemoryTab';
import VersionsTab from './components/VersionsTab';
import { checkHealth, fetchExecutions, fetchProviders, fetchTools } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [systemStatus, setSystemStatus] = useState({ status: 'checking' });
  const [executions, setExecutions] = useState([]);
  const [providers, setProviders] = useState([]);
  const [tools, setTools] = useState([]);
  const [selectedExecutionId, setSelectedExecutionId] = useState(null);
  const [presetData, setPresetData] = useState(null);

  const loadData = useCallback(async () => {
    try {
      const [health, execs, provs, tls] = await Promise.all([
        checkHealth(),
        fetchExecutions(),
        fetchProviders(),
        fetchTools(),
      ]);
      setSystemStatus(health);
      if (Array.isArray(execs)) setExecutions(execs);
      if (Array.isArray(provs)) setProviders(provs);
      if (Array.isArray(tls)) setTools(tls);
    } catch (err) {
      console.error('Data polling error:', err);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleLaunchPreset = (preset) => {
    setPresetData(preset);
    setActiveTab('new-task');
  };

  const handleTaskLaunched = (executionId) => {
    setSelectedExecutionId(executionId);
    setActiveTab('monitor');
    loadData();
  };

  const handleSelectExecution = (executionId) => {
    setSelectedExecutionId(executionId);
    setActiveTab('monitor');
  };

  const activeExecutionCount = executions.filter(e => e.status === 'running').length;

  return (
    <div className="app-container">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemStatus={systemStatus}
        activeExecutionCount={activeExecutionCount}
      />

      <main className="main-content">
        {activeTab === 'overview' && (
          <OverviewTab
            executions={executions}
            providers={providers}
            tools={tools}
            onLaunchPreset={handleLaunchPreset}
            onSelectExecution={handleSelectExecution}
            onNavigate={setActiveTab}
          />
        )}

        {activeTab === 'new-task' && (
          <NewTaskTab
            providers={providers}
            tools={tools}
            initialData={presetData}
            onTaskLaunched={handleTaskLaunched}
          />
        )}

        {activeTab === 'monitor' && (
          <MonitorTab
            selectedExecutionId={selectedExecutionId}
            executions={executions}
            onSelectExecution={setSelectedExecutionId}
          />
        )}

        {activeTab === 'executions' && (
          <ExecutionsTab
            executions={executions}
            onSelectExecution={handleSelectExecution}
            onRefresh={loadData}
          />
        )}

        {activeTab === 'providers' && (
          <ProvidersTab
            providers={providers}
            onRefresh={loadData}
          />
        )}

        {activeTab === 'tools' && (
          <ToolsTab
            tools={tools}
            onRefresh={loadData}
          />
        )}

        {activeTab === 'memory' && (
          <MemoryTab />
        )}

        {activeTab === 'versions' && (
          <VersionsTab />
        )}
      </main>
    </div>
  );
}
