import React, { useState } from 'react';
import { submitTask } from '../api';

export default function NewTaskTab({ providers, tools, initialData, onTaskLaunched }) {
  const [target, setTarget] = useState(initialData?.target || '');
  const [objective, setObjective] = useState(
    initialData?.objective || 'Perform full reconnaissance, discover network services, and identify potential high-risk vulnerabilities.'
  );
  const [strategy, setStrategy] = useState(initialData?.strategy || 'plan_and_execute');
  const [provider, setProvider] = useState('anthropic');
  const [model, setModel] = useState('');
  const [maxIterations, setMaxIterations] = useState(15);
  const [timeout, setTimeoutSec] = useState(300);
  const [sandboxIsolated, setSandboxIsolated] = useState(true);
  const [selectedTools, setSelectedTools] = useState(
    initialData?.tools || ['nmap', 'gobuster', 'nikto', 'nuclei']
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const availableToolList = tools.length > 0 ? tools : [
    { name: 'nmap', description: 'Port scanning and OS detection' },
    { name: 'gobuster', description: 'Web directory and DNS brute forcing' },
    { name: 'nikto', description: 'Web server vulnerability scanner' },
    { name: 'sqlmap', description: 'Automatic SQL injection tool' },
    { name: 'nuclei', description: 'Fast vulnerability scanner based on templates' },
    { name: 'searchsploit', description: 'Exploit database offline lookup' },
    { name: 'metasploit', description: 'Exploit execution and payload verification' },
  ];

  const toggleTool = (toolName) => {
    setSelectedTools(prev =>
      prev.includes(toolName)
        ? prev.filter(t => t !== toolName)
        : [...prev, toolName]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!target.trim()) {
      setErrorMessage('Target host/IP/domain is required.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const payload = {
        target: target.trim(),
        objective: objective.trim(),
        strategy,
        provider,
        model: model.trim() || undefined,
        max_iterations: Number(maxIterations),
        timeout_seconds: Number(timeout),
        sandbox_enabled: sandboxIsolated,
        tools: selectedTools,
      };

      const res = await submitTask(payload);
      onTaskLaunched(res.execution_id || res.id);
    } catch (err) {
      setErrorMessage(err.message || 'Submission failed');
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 840, margin: '0 auto' }}>
      <div className="cyber-card">
        <div className="card-header">
          <div className="card-title">
            <span className="prefix">[INIT]</span> LAUNCH NEW SECURITY MISSION
          </div>
          <span className="system-tag">AUTONOMOUS MULTI-AGENT</span>
        </div>

        {errorMessage && (
          <div style={{
            background: 'var(--accent-red-dim)',
            border: '1px solid var(--accent-red)',
            color: 'var(--accent-red)',
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            fontFamily: 'var(--font-mono)',
            fontSize: 12,
            marginBottom: 20
          }}>
            [ERR] {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Target input */}
          <div className="form-group">
            <label className="form-label">// MISSION TARGET (HOST / IP / CIDR / URL)</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. 10.0.2.15, example.com, 192.168.1.0/24"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              required
            />
          </div>

          {/* Objective textarea */}
          <div className="form-group">
            <label className="form-label">// RESEARCH OBJECTIVE & SCOPE</label>
            <textarea
              className="form-textarea"
              placeholder="Specify mission goals, constraints, and target rules of engagement..."
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              required
            />
          </div>

          {/* Strategy & Provider row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">// ORCHESTRATION STRATEGY</label>
              <select
                className="form-select"
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
              >
                <option value="react">ReAct (Single Agent Dynamic)</option>
                <option value="plan_and_execute">Plan-and-Execute (Sequential Review)</option>
                <option value="hierarchical">Hierarchical (Multi-Agent Supervisor)</option>
                <option value="autonomous">Full Autonomous (Self-Reflective Loop)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">// PRIMARY AI PROVIDER</label>
              <select
                className="form-select"
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
              >
                <option value="anthropic">Anthropic Claude (Recommended)</option>
                <option value="openai">OpenAI GPT-4o</option>
                <option value="ollama">Ollama (Local / Offline)</option>
                <option value="deepseek">DeepSeek (OpenAI-compatible)</option>
                <option value="mistral">Mistral AI</option>
                <option value="nvidia_nim">NVIDIA NIM</option>
                <option value="mock">Mock / Simulation Provider</option>
              </select>
            </div>
          </div>

          {/* Model override and Limits */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 16 }}>
            <div className="form-group">
              <label className="form-label">// MODEL OVERRIDE (OPTIONAL)</label>
              <input
                type="text"
                className="form-input"
                placeholder="Default provider model"
                value={model}
                onChange={(e) => setModel(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">// MAX STEPS</label>
              <input
                type="number"
                className="form-input"
                min="1"
                max="50"
                value={maxIterations}
                onChange={(e) => setMaxIterations(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">// TIMEOUT (SEC)</label>
              <input
                type="number"
                className="form-input"
                min="30"
                max="3600"
                value={timeout}
                onChange={(e) => setTimeoutSec(e.target.value)}
              />
            </div>
          </div>

          {/* Sandbox toggle */}
          <div className="form-group" style={{ margin: '14px 0 20px 0' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: 12 }}>
              <input
                type="checkbox"
                checked={sandboxIsolated}
                onChange={(e) => setSandboxIsolated(e.target.checked)}
                style={{ accentColor: 'var(--accent-cyan)' }}
              />
              <span>RUN IN DOCKER KALI SANDBOX (Zero host execution danger)</span>
            </label>
          </div>

          {/* Tools Selection Checklist */}
          <div className="form-group">
            <label className="form-label">// ENABLED TOOL INVENTORY</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 10 }}>
              {availableToolList.map((t) => {
                const name = typeof t === 'string' ? t : t.name;
                const isChecked = selectedTools.includes(name);
                return (
                  <div
                    key={name}
                    onClick={() => toggleTool(name)}
                    style={{
                      background: isChecked ? 'var(--accent-cyan-dim)' : 'var(--bg-input)',
                      border: `1px solid ${isChecked ? 'var(--accent-cyan)' : 'var(--border-subtle)'}`,
                      borderRadius: 'var(--radius-sm)',
                      padding: '8px 12px',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      fontFamily: 'var(--font-mono)',
                      fontSize: 12,
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: 600, color: isChecked ? 'var(--accent-cyan)' : 'var(--text-main)' }}>
                        {name}
                      </span>
                      <span style={{ fontSize: 10, color: isChecked ? 'var(--accent-cyan)' : 'var(--text-dim)' }}>
                        {isChecked ? '[ON]' : '[OFF]'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div style={{ marginTop: 24, display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
              style={{ minWidth: 180 }}
            >
              {isSubmitting ? 'INITIALIZING MISSION...' : 'LAUNCH MISSION &rarr;'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
