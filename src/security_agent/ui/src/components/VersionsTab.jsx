import React, { useState, useEffect } from 'react';
import {
  fetchVersions,
  updateComponentVersion,
  rollbackComponentVersion,
  installComponentArtifact,
} from '../api';

export default function VersionsTab() {
  const [data, setData] = useState({ total: 0, categories: [], components: [] });
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [search, setSearch] = useState('');
  const [activeModal, setActiveModal] = useState(null); // { type: 'changelog'|'rollback'|'install', component: {} }
  const [modalInput, setModalInput] = useState('');
  const [modalInputSecondary, setModalInputSecondary] = useState('zip');
  const [actionStatus, setActionStatus] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const loadData = async () => {
    setLoading(true);
    const res = await fetchVersions();
    setData(res);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpdate = async (componentId) => {
    setIsProcessing(true);
    setActionStatus({ type: 'info', message: `Updating ${componentId}...` });
    try {
      const res = await updateComponentVersion(componentId);
      setActionStatus({ type: 'success', message: res.message || `Updated ${componentId} successfully.` });
      await loadData();
    } catch (err) {
      setActionStatus({ type: 'error', message: err.message });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUpdateAll = async () => {
    if (!window.confirm('Update all system components, providers, and tools to latest?')) return;
    setIsProcessing(true);
    setActionStatus({ type: 'info', message: 'Updating all system components to latest...' });
    try {
      const res = await updateComponentVersion('all');
      setActionStatus({ type: 'success', message: res.message || 'All components updated.' });
      await loadData();
    } catch (err) {
      setActionStatus({ type: 'error', message: err.message });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleModalSubmit = async () => {
    if (!activeModal || !modalInput.trim()) return;
    setIsProcessing(true);

    try {
      if (activeModal.type === 'rollback') {
        const res = await rollbackComponentVersion(activeModal.component.id, modalInput.trim());
        setActionStatus({ type: 'success', message: res.message || `Rollback completed for ${activeModal.component.id}.` });
      } else if (activeModal.type === 'install') {
        const res = await installComponentArtifact(
          activeModal.component.id,
          modalInput.trim(),
          modalInputSecondary
        );
        setActionStatus({ type: 'success', message: res.message || `Installed artifact for ${activeModal.component.id}.` });
      }
      setActiveModal(null);
      setModalInput('');
      await loadData();
    } catch (err) {
      setActionStatus({ type: 'error', message: err.message });
    } finally {
      setIsProcessing(false);
    }
  };

  const filteredComponents = (data.components || []).filter((comp) => {
    const matchCat = selectedCategory === 'ALL' || comp.category === selectedCategory;
    const matchSearch =
      comp.id.toLowerCase().includes(search.toLowerCase()) ||
      comp.name.toLowerCase().includes(search.toLowerCase()) ||
      comp.description.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header bar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          borderBottom: '1px solid #1f293d',
          paddingBottom: '16px',
        }}
      >
        <div>
          <div style={{ fontSize: '1.2rem', fontWeight: 600, color: '#f8fafc', letterSpacing: '0.05em' }}>
            COMPONENT & VERSION REGISTRY
          </div>
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>
            Independent, un-locked version lifecycle for Core, Providers, Tools, Agents, Packages, and Extensions.
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={loadData}
            disabled={loading || isProcessing}
            style={{
              background: '#0f172a',
              color: '#38bdf8',
              border: '1px solid #0284c7',
              padding: '8px 14px',
              fontFamily: 'monospace',
              fontSize: '0.8rem',
              cursor: 'pointer',
            }}
          >
            [REFRESH]
          </button>
          <button
            onClick={handleUpdateAll}
            disabled={loading || isProcessing}
            style={{
              background: '#047857',
              color: '#ecfdf5',
              border: '1px solid #10b981',
              padding: '8px 16px',
              fontFamily: 'monospace',
              fontSize: '0.8rem',
              fontWeight: 'bold',
              cursor: 'pointer',
            }}
          >
            [UPDATE ALL TO LATEST]
          </button>
        </div>
      </div>

      {/* Action banner feedback */}
      {actionStatus && (
        <div
          style={{
            padding: '10px 14px',
            fontSize: '0.85rem',
            fontFamily: 'monospace',
            border:
              actionStatus.type === 'error'
                ? '1px solid #ef4444'
                : actionStatus.type === 'success'
                ? '1px solid #10b981'
                : '1px solid #38bdf8',
            background:
              actionStatus.type === 'error'
                ? 'rgba(239, 68, 68, 0.1)'
                : actionStatus.type === 'success'
                ? 'rgba(16, 185, 129, 0.1)'
                : 'rgba(56, 189, 248, 0.1)',
            color:
              actionStatus.type === 'error'
                ? '#fca5a5'
                : actionStatus.type === 'success'
                ? '#6ee7b7'
                : '#7dd3fc',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>{actionStatus.message}</span>
          <button
            onClick={() => setActionStatus(null)}
            style={{ background: 'transparent', border: 'none', color: 'inherit', cursor: 'pointer', fontFamily: 'monospace' }}
          >
            [X]
          </button>
        </div>
      )}

      {/* Filter and Category Navigation */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
        <button
          onClick={() => setSelectedCategory('ALL')}
          style={{
            background: selectedCategory === 'ALL' ? '#1e293b' : 'transparent',
            color: selectedCategory === 'ALL' ? '#38bdf8' : '#64748b',
            border: '1px solid',
            borderColor: selectedCategory === 'ALL' ? '#38bdf8' : '#1e293b',
            padding: '6px 12px',
            fontSize: '0.75rem',
            fontFamily: 'monospace',
            cursor: 'pointer',
          }}
        >
          ALL ({data.components?.length || 0})
        </button>
        {(data.categories || []).map((cat) => {
          const count = (data.components || []).filter((c) => c.category === cat).length;
          const isSel = selectedCategory === cat;
          return (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              style={{
                background: isSel ? '#1e293b' : 'transparent',
                color: isSel ? '#38bdf8' : '#64748b',
                border: '1px solid',
                borderColor: isSel ? '#38bdf8' : '#1e293b',
                padding: '6px 12px',
                fontSize: '0.75rem',
                fontFamily: 'monospace',
                cursor: 'pointer',
              }}
            >
              {cat.toUpperCase()} ({count})
            </button>
          );
        })}

        <div style={{ marginLeft: 'auto' }}>
          <input
            type="text"
            placeholder="Search component..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              background: '#0f172a',
              border: '1px solid #1e293b',
              color: '#f8fafc',
              padding: '6px 12px',
              fontSize: '0.8rem',
              fontFamily: 'monospace',
              width: '220px',
            }}
          />
        </div>
      </div>

      {/* Component Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '16px' }}>
        {filteredComponents.map((comp) => {
          return (
            <div
              key={comp.id}
              style={{
                background: '#090d16',
                border: '1px solid #1a2234',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '12px',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
                  <div>
                    <span style={{ fontSize: '0.7rem', color: '#64748b', fontFamily: 'monospace' }}>
                      [{comp.category.toUpperCase()}]
                    </span>
                    <div style={{ fontSize: '1rem', fontWeight: 600, color: '#f1f5f9', marginTop: '2px' }}>
                      {comp.name}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#38bdf8', fontFamily: 'monospace' }}>
                      {comp.id}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div
                      style={{
                        display: 'inline-block',
                        background: '#064e3b',
                        color: '#34d399',
                        padding: '2px 8px',
                        fontSize: '0.75rem',
                        fontFamily: 'monospace',
                        fontWeight: 'bold',
                        border: '1px solid #059669',
                      }}
                    >
                      v{comp.version}
                    </div>
                    <div style={{ fontSize: '0.65rem', color: '#94a3b8', marginTop: '4px', fontFamily: 'monospace' }}>
                      TYPE: {comp.artifact_type.toUpperCase()}
                    </div>
                  </div>
                </div>

                <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '10px', lineHeight: '1.4' }}>
                  {comp.description}
                </div>

                <div
                  style={{
                    background: '#030712',
                    border: '1px solid #111827',
                    padding: '6px 10px',
                    fontSize: '0.7rem',
                    fontFamily: 'monospace',
                    color: '#94a3b8',
                    marginTop: '10px',
                    wordBreak: 'break-all',
                  }}
                >
                  REF / PKG: <span style={{ color: '#cbd5e1' }}>{comp.package !== '—' ? comp.package : comp.ref}</span>
                </div>
              </div>

              {/* Action buttons */}
              <div
                style={{
                  display: 'flex',
                  gap: '6px',
                  flexWrap: 'wrap',
                  borderTop: '1px solid #151d2f',
                  paddingTop: '12px',
                }}
              >
                <button
                  onClick={() => handleUpdate(comp.id)}
                  disabled={isProcessing}
                  title="Update to latest available version independently"
                  style={{
                    flex: '1',
                    background: '#0f172a',
                    border: '1px solid #0284c7',
                    color: '#38bdf8',
                    padding: '6px 8px',
                    fontSize: '0.7rem',
                    fontFamily: 'monospace',
                    cursor: 'pointer',
                  }}
                >
                  [UPDATE]
                </button>

                <button
                  onClick={() => {
                    setActiveModal({ type: 'rollback', component: comp });
                    setModalInput(comp.version);
                  }}
                  disabled={isProcessing}
                  title="Roll back to a specific version, git tag, or commit"
                  style={{
                    flex: '1',
                    background: '#0f172a',
                    border: '1px solid #d97706',
                    color: '#f59e0b',
                    padding: '6px 8px',
                    fontSize: '0.7rem',
                    fontFamily: 'monospace',
                    cursor: 'pointer',
                  }}
                >
                  [ROLLBACK]
                </button>

                <button
                  onClick={() => {
                    setActiveModal({ type: 'install', component: comp });
                    setModalInput('');
                    setModalInputSecondary(comp.artifact_type || 'zip');
                  }}
                  disabled={isProcessing}
                  title="Download and install independent artifact (.zip, git tag, pypi)"
                  style={{
                    flex: '1',
                    background: '#0f172a',
                    border: '1px solid #8b5cf6',
                    color: '#a78bfa',
                    padding: '6px 8px',
                    fontSize: '0.7rem',
                    fontFamily: 'monospace',
                    cursor: 'pointer',
                  }}
                >
                  [INSTALL ARTIFACT]
                </button>

                <button
                  onClick={() => setActiveModal({ type: 'changelog', component: comp })}
                  title="View component changelog and release notes"
                  style={{
                    background: '#0f172a',
                    border: '1px solid #334155',
                    color: '#94a3b8',
                    padding: '6px 8px',
                    fontSize: '0.7rem',
                    fontFamily: 'monospace',
                    cursor: 'pointer',
                  }}
                >
                  [NOTES]
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal Dialog */}
      {activeModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.85)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px',
          }}
        >
          <div
            style={{
              background: '#0b0f19',
              border: '1px solid #38bdf8',
              maxWidth: '600px',
              width: '100%',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.8)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#f8fafc', fontFamily: 'monospace' }}>
                {activeModal.type === 'rollback' && `[ROLLBACK] ${activeModal.component.id}`}
                {activeModal.type === 'install' && `[INSTALL ARTIFACT] ${activeModal.component.id}`}
                {activeModal.type === 'changelog' && `[CHANGELOG] ${activeModal.component.name}`}
              </div>
              <button
                onClick={() => setActiveModal(null)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '1rem', cursor: 'pointer', fontFamily: 'monospace' }}
              >
                [X]
              </button>
            </div>

            {activeModal.type === 'changelog' ? (
              <div
                style={{
                  background: '#020617',
                  border: '1px solid #1e293b',
                  padding: '16px',
                  maxHeight: '400px',
                  overflowY: 'auto',
                  fontSize: '0.85rem',
                  color: '#cbd5e1',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                }}
              >
                {activeModal.component.changelog}
              </div>
            ) : (
              <>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                  {activeModal.type === 'rollback' &&
                    'Enter target Git Release Tag (e.g. v0.1.0), Commit SHA, or package version to roll back independently:'}
                  {activeModal.type === 'install' &&
                    'Provide an artifact source (URL to a .zip archive, local .zip file path, Git tag, or package version):'}
                </div>

                <input
                  type="text"
                  placeholder={
                    activeModal.type === 'rollback'
                      ? 'e.g. v0.1.0 or 1.2.0 or e312112'
                      : 'https://example.com/component.zip or v0.1.0 or 0.2.0'
                  }
                  value={modalInput}
                  onChange={(e) => setModalInput(e.target.value)}
                  style={{
                    background: '#020617',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    padding: '10px 14px',
                    fontSize: '0.9rem',
                    fontFamily: 'monospace',
                    width: '100%',
                    boxSizing: 'border-box',
                  }}
                />

                {activeModal.type === 'install' && (
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontFamily: 'monospace' }}>ARTIFACT TYPE:</span>
                    {['zip', 'git-tag', 'git-commit', 'pypi'].map((t) => (
                      <label key={t} style={{ fontSize: '0.75rem', color: '#cbd5e1', fontFamily: 'monospace', cursor: 'pointer' }}>
                        <input
                          type="radio"
                          name="art_type"
                          value={t}
                          checked={modalInputSecondary === t}
                          onChange={() => setModalInputSecondary(t)}
                          style={{ marginRight: '4px' }}
                        />
                        {t.toUpperCase()}
                      </label>
                    ))}
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
                  <button
                    onClick={() => setActiveModal(null)}
                    style={{
                      background: 'transparent',
                      border: '1px solid #475569',
                      color: '#94a3b8',
                      padding: '8px 16px',
                      fontFamily: 'monospace',
                      cursor: 'pointer',
                    }}
                  >
                    [CANCEL]
                  </button>
                  <button
                    onClick={handleModalSubmit}
                    disabled={isProcessing || !modalInput.trim()}
                    style={{
                      background: activeModal.type === 'rollback' ? '#d97706' : '#2563eb',
                      border: 'none',
                      color: '#ffffff',
                      padding: '8px 18px',
                      fontFamily: 'monospace',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                    }}
                  >
                    {isProcessing ? '[EXECUTING...]' : '[CONFIRM & EXECUTE]'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
