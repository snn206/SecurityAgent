import React from 'react';

export default function ProvidersTab({ providers, onRefresh }) {
  const defaultProviderList = [
    { name: 'anthropic', type: 'cloud', default_model: 'claude-3-5-sonnet-20241022', configured: true, env_var: 'ANTHROPIC_API_KEY' },
    { name: 'openai', type: 'cloud', default_model: 'gpt-4o', configured: false, env_var: 'OPENAI_API_KEY' },
    { name: 'ollama', type: 'local', default_model: 'llama3:8b', configured: true, env_var: 'OLLAMA_BASE_URL' },
    { name: 'deepseek', type: 'compatible', default_model: 'deepseek-chat', configured: false, env_var: 'DEEPSEEK_API_KEY' },
    { name: 'mistral', type: 'cloud', default_model: 'mistral-large-latest', configured: false, env_var: 'MISTRAL_API_KEY' },
    { name: 'nvidia_nim', type: 'cloud', default_model: 'meta/llama-3.1-70b-instruct', configured: false, env_var: 'NVIDIA_API_KEY' },
    { name: 'qwen', type: 'compatible', default_model: 'qwen-2.5-72b-instruct', configured: false, env_var: 'DASHSCOPE_API_KEY' },
    { name: 'opencode', type: 'compatible', default_model: 'opencode-interpreter', configured: false, env_var: 'OPENCODE_API_KEY' },
    { name: 'kilo', type: 'compatible', default_model: 'kilo-audit-v1', configured: false, env_var: 'KILO_API_KEY' },
    { name: 'mock', type: 'testing', default_model: 'mock-cyber-agent', configured: true, env_var: 'NONE' },
  ];

  const displayList = providers && providers.length > 0 ? providers : defaultProviderList;

  return (
    <div>
      <div className="cyber-card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">
            <span className="prefix">[LLM]</span> AGENT PROVIDERS & MODEL REGISTRY
          </div>
          <button className="btn btn-secondary" onClick={onRefresh}>
            REFRESH PROVIDERS
          </button>
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 20 }}>
          SecurityAgent dynamically discovers and hot-swaps between 10+ LLM providers via standard interfaces without code recompilation.
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 16 }}>
          {displayList.map((p) => {
            const isReady = p.configured !== false;
            return (
              <div
                key={p.name}
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
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 700, color: 'var(--accent-cyan)' }}>
                      {p.name.toUpperCase()}
                    </div>
                    <span className={`badge ${isReady ? 'badge-green' : 'badge-amber'}`}>
                      {isReady ? 'READY' : 'KEY REQUIRED'}
                    </span>
                  </div>

                  <div className="form-group" style={{ marginBottom: 8 }}>
                    <span className="form-label">DEFAULT MODEL:</span>
                    <span className="mono" style={{ fontSize: 12, color: 'var(--text-main)' }}>
                      {p.default_model || p.model || 'auto'}
                    </span>
                  </div>

                  <div className="form-group" style={{ marginBottom: 8 }}>
                    <span className="form-label">PROVIDER CLASS:</span>
                    <span className="mono" style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                      {p.type ? p.type.toUpperCase() : 'OPENAI_COMPATIBLE'}
                    </span>
                  </div>

                  {p.env_var && (
                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <span className="form-label">ENVIRONMENT KEY:</span>
                      <span className="mono" style={{ fontSize: 11, color: 'var(--text-dim)' }}>
                        {p.env_var}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
