import React, { useState, useEffect, useCallback } from 'react';
import { fetchMemories, createMemory, updateMemory, deleteMemory, resetMemory } from '../api';

export default function MemoryTab() {
  const [collection, setCollection] = useState('lessons_learned');
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');
  const [memories, setMemories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  // Form states
  const [formTitle, setFormTitle] = useState('');
  const [formContent, setFormContent] = useState('');
  const [formTarget, setFormTarget] = useState('');
  const [formCategory, setFormCategory] = useState('general');
  const [formFlags, setFormFlags] = useState('');

  const loadMemories = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchMemories(collection, category, search);
      setMemories(data.items || []);
    } catch (err) {
      console.error('Failed to load memories:', err);
    } finally {
      setIsLoading(false);
    }
  }, [collection, category, search]);

  useEffect(() => {
    loadMemories();
  }, [loadMemories]);

  const handleOpenAdd = () => {
    setFormTitle('');
    setFormContent('');
    setFormTarget('');
    setFormCategory('general');
    setFormFlags('');
    setShowAddModal(true);
  };

  const handleSaveMemory = async (e) => {
    e.preventDefault();
    if (!formTitle.trim() || !formContent.trim()) {
      alert('Title and content are required.');
      return;
    }

    try {
      if (editingItem) {
        await updateMemory(collection, editingItem._id, {
          title: formTitle,
          content: formContent,
          category: formCategory,
          recommended_flags: formFlags,
        });
        setEditingItem(null);
      } else {
        await createMemory({
          collection,
          title: formTitle,
          content: formContent,
          target: formTarget || undefined,
          category: formCategory,
          recommended_flags: formFlags || undefined,
        });
        setShowAddModal(false);
      }
      loadMemories();
    } catch (err) {
      alert(`Save failed: ${err.message}`);
    }
  };

  const handleEditClick = (item) => {
    setEditingItem(item);
    setFormTitle(item.title || '');
    setFormContent(item.insight || item.rule || '');
    setFormTarget(item.target || '');
    setFormCategory(item.category || 'general');
    setFormFlags(item.recommended_flags || '');
  };

  const handleDeleteClick = async (id) => {
    if (!confirm('Are you sure you want to delete this memory entry?')) return;
    try {
      await deleteMemory(collection, id);
      loadMemories();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleResetCollection = async () => {
    if (!confirm(`Warning: Purge all entries from ${collection.toUpperCase()}?`)) return;
    try {
      await resetMemory(collection);
      loadMemories();
    } catch (err) {
      alert(`Purge failed: ${err.message}`);
    }
  };

  return (
    <div>
      {/* ── Top Bar ─────────────────────────────────────────────────── */}
      <div className="cyber-card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <div className="card-title">
            <span className="prefix">[BRAIN]</span> AGENT MEMORY & EVOLUTION REPOSITORY
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-primary" onClick={handleOpenAdd}>
              + INJECT GOLDEN RULE
            </button>
            <button className="btn btn-danger" onClick={handleResetCollection}>
              PURGE COLLECTION
            </button>
          </div>
        </div>

        {/* Collection Selector */}
        <div style={{ display: 'flex', gap: 6, marginBottom: 16, flexWrap: 'wrap' }}>
          {[
            { id: 'lessons_learned', label: 'JEV LESSONS LEARNED' },
            { id: 'golden_rules', label: 'USER GOLDEN RULES' },
            { id: 'target_knowledge', label: 'TARGET KNOWLEDGE' },
          ].map((col) => (
            <button
              key={col.id}
              className={`nav-tab-btn ${collection === col.id ? 'active' : ''}`}
              onClick={() => setCollection(col.id)}
            >
              {col.label}
            </button>
          ))}
        </div>

        {/* Search & Category Filter Bar */}
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <input
            type="text"
            className="form-input"
            style={{ maxWidth: 320 }}
            placeholder="Search distilled lessons or rules..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <select
            className="form-select"
            style={{ maxWidth: 180 }}
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="recon">Reconnaissance</option>
            <option value="vuln">Vulnerability</option>
            <option value="exploit">Exploitation</option>
            <option value="safety">Safety / Ethics</option>
            <option value="general">General</option>
          </select>

          <span className="system-tag">
            {memories.length} MEMORIES STORED
          </span>
        </div>
      </div>

      {/* ── Memory Cards Grid ────────────────────────────────────────── */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '40px 0', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
          QUERYING EMBEDDED MEMORY STORE...
        </div>
      ) : memories.length === 0 ? (
        <div className="cyber-card" style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
          // NO MEMORY RECORDS FOUND IN {collection.toUpperCase()}.
          <div style={{ marginTop: 12 }}>
            Click '+ INJECT GOLDEN RULE' above to teach the agents new guidelines.
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 16 }}>
          {memories.map((item) => (
            <div
              key={item._id}
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
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 8, gap: 8 }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 700, color: 'var(--accent-cyan)' }}>
                    {item.title}
                  </div>
                  <span className={`badge ${item.source === 'USER_INJECTED' ? 'badge-amber' : 'badge-green'}`}>
                    {item.source === 'USER_INJECTED' ? 'USER RULE' : 'JEV LEARNED'}
                  </span>
                </div>

                <div style={{ fontSize: 12, color: 'var(--text-main)', marginBottom: 12, lineHeight: 1.5 }}>
                  {item.insight || item.rule || item.description}
                </div>

                {item.recommended_flags && (
                  <div style={{ background: '#05080e', padding: '6px 10px', borderRadius: 4, fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-mono)', marginBottom: 10 }}>
                    FLAGS: {item.recommended_flags}
                  </div>
                )}

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
                  {item.target && (
                    <span className="badge badge-muted">TARGET: {item.target}</span>
                  )}
                  {item.tool_name && (
                    <span className="badge badge-cyan">TOOL: {item.tool_name}</span>
                  )}
                  {item.category && (
                    <span className="badge badge-muted">{item.category.toUpperCase()}</span>
                  )}
                  {item.score !== undefined && (
                    <span className="badge badge-muted">SCORE: {item.score}</span>
                  )}
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, paddingTop: 10, borderTop: '1px solid var(--border-subtle)' }}>
                <button
                  className="btn btn-secondary"
                  style={{ padding: '4px 10px', fontSize: 11 }}
                  onClick={() => handleEditClick(item)}
                >
                  EDIT
                </button>
                <button
                  className="btn btn-danger"
                  style={{ padding: '4px 10px', fontSize: 11 }}
                  onClick={() => handleDeleteClick(item._id)}
                >
                  DELETE
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Add / Edit Modal ─────────────────────────────────────────── */}
      {(showAddModal || editingItem) && (
        <div className="modal-overlay" onClick={() => { setShowAddModal(false); setEditingItem(null); }}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="card-title">
                <span className="prefix">[RULE]</span> {editingItem ? 'EDIT MEMORY ENTRY' : 'INJECT USER GOLDEN RULE'}
              </div>
              <button className="btn btn-secondary" onClick={() => { setShowAddModal(false); setEditingItem(null); }}>
                CLOSE
              </button>
            </div>

            <form onSubmit={handleSaveMemory}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">// RULE TITLE / SUMMARY</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Rate-limit bypass for subnet 10.0.0.0/16"
                    value={formTitle}
                    onChange={(e) => setFormTitle(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">// INSTRUCTION / LESSON BODY</label>
                  <textarea
                    className="form-textarea"
                    placeholder="Explicit directive or observation the agent should follow..."
                    value={formContent}
                    onChange={(e) => setFormContent(e.target.value)}
                    required
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div className="form-group">
                    <label className="form-label">// TARGET SCOPE (OPTIONAL)</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. 192.168.1.0/24 or all"
                      value={formTarget}
                      onChange={(e) => setFormTarget(e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">// CATEGORY</label>
                    <select
                      className="form-select"
                      value={formCategory}
                      onChange={(e) => setFormCategory(e.target.value)}
                    >
                      <option value="general">General</option>
                      <option value="recon">Reconnaissance</option>
                      <option value="vuln">Vulnerability</option>
                      <option value="exploit">Exploitation</option>
                      <option value="safety">Safety / Policy</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">// RECOMMENDED FLAGS / CLI MODIFIERS (OPTIONAL)</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. -Pn -T2 --scan-delay 100ms"
                    value={formFlags}
                    onChange={(e) => setFormFlags(e.target.value)}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => { setShowAddModal(false); setEditingItem(null); }}
                >
                  CANCEL
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingItem ? 'SAVE CHANGES' : 'INJECT RULE &rarr;'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
