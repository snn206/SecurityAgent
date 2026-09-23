/* SecurityAgent — UI JavaScript
 * Real-time execution monitoring via WebSocket/SSE
 */

const API = '/api/v1';
let currentWS = null;
let currentExecutionId = null;

// ── Panel Navigation ────────────────────────────────────────────────────────

function showPanel(name) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(`panel-${name}`).classList.add('active');
  document.getElementById(`nav-${name}`).classList.add('active');

  if (name === 'history') loadHistory();
  if (name === 'providers') loadProviders();
  if (name === 'tools') loadTools();
}

// ── Health Check ────────────────────────────────────────────────────────────

async function checkHealth() {
  const dot = document.getElementById('status-dot');
  const text = document.getElementById('status-text');
  try {
    const res = await fetch(`${API}/health`);
    if (res.ok) {
      dot.classList.add('online');
      dot.classList.remove('offline');
      text.textContent = 'API Online';
    } else {
      throw new Error('not ok');
    }
  } catch {
    dot.classList.add('offline');
    dot.classList.remove('online');
    text.textContent = 'API Offline';
  }
}

// ── Task Submission ─────────────────────────────────────────────────────────

async function submitTask(event) {
  event.preventDefault();
  const btn = document.getElementById('submit-btn');
  const request = document.getElementById('user-request').value.trim();
  const scope = document.getElementById('scope').value.trim();
  const provider = document.getElementById('provider-select').value;

  if (!request) {
    alert('Please enter a task objective.');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="btn-icon">⟳</span> Submitting…';

  try {
    const res = await fetch(`${API}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_request: request, scope, provider }),
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(err);
    }

    const data = await res.json();
    startExecution(data.execution_id, data.status);

  } catch (err) {
    alert(`Error: ${err.message}`);
    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">▶</span> Run Task';
  }
}

// ── Execution Monitoring ────────────────────────────────────────────────────

function startExecution(executionId, initialStatus = 'pending') {
  currentExecutionId = executionId;

  // Show execution view
  const view = document.getElementById('execution-view');
  view.style.display = 'block';
  document.getElementById('exec-id-display').textContent = `ID: ${executionId.substring(0, 16)}…`;
  updateStatusBadge(initialStatus);

  // Clear timeline
  clearTimeline();

  // Connect WebSocket
  connectWebSocket(executionId);

  // Reset button
  const btn = document.getElementById('submit-btn');
  btn.disabled = false;
  btn.innerHTML = '<span class="btn-icon">▶</span> Run Task';
}

function connectWebSocket(executionId) {
  if (currentWS) currentWS.close();

  const wsProtocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${wsProtocol}//${location.host}/ws/${executionId}`;

  currentWS = new WebSocket(wsUrl);

  currentWS.onopen = () => addTimelineEvent({ event_type: 'task.started', agent_id: 'system',
    timestamp: new Date().toISOString(), payload: { message: 'Connected — waiting for events…' } });

  currentWS.onmessage = (msg) => {
    try {
      const event = JSON.parse(msg.data);
      addTimelineEvent(event);
      updateStatusFromEvent(event);
    } catch {}
  };

  currentWS.onclose = () => {
    addTimelineEvent({ event_type: 'info', agent_id: 'system',
      timestamp: new Date().toISOString(), payload: { message: 'WebSocket closed.' } });
  };

  currentWS.onerror = () => {
    // Fallback to SSE polling
    pollSSE(executionId);
  };

  // Keepalive
  const ping = setInterval(() => {
    if (currentWS && currentWS.readyState === WebSocket.OPEN) {
      currentWS.send('ping');
    } else {
      clearInterval(ping);
    }
  }, 20000);
}

function pollSSE(executionId) {
  const evtSource = new EventSource(`/stream/${executionId}`);
  evtSource.onmessage = (e) => {
    try {
      const event = JSON.parse(e.data);
      addTimelineEvent(event);
      updateStatusFromEvent(event);
    } catch {}
  };
  evtSource.onerror = () => evtSource.close();
}

// ── Timeline Rendering ──────────────────────────────────────────────────────

function addTimelineEvent(event) {
  const timeline = document.getElementById('timeline');
  const el = document.createElement('div');
  el.className = 'timeline-event';

  const time = new Date(event.timestamp || Date.now());
  const timeStr = time.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const eventType = event.event_type || 'info';
  const agentId = event.agent_id || '';
  const payload = event.payload || {};

  const tagClass = getTagClass(eventType);
  const icon = getEventIcon(eventType);
  const label = formatEventLabel(eventType);
  const description = formatPayloadSummary(eventType, payload);

  el.innerHTML = `
    <div class="event-meta">
      <span class="event-type-tag ${tagClass}">${icon} ${label}</span><br/>
      <span>${timeStr}</span>
      ${agentId ? `<br/><span style="color:var(--accent-secondary)">[${agentId}]</span>` : ''}
    </div>
    <div class="event-content">
      <div>${description}</div>
      ${renderPayloadDetail(eventType, payload)}
    </div>
  `;

  timeline.appendChild(el);
  timeline.scrollTop = timeline.scrollHeight;
}

function getTagClass(eventType) {
  if (eventType.startsWith('task.')) return 'tag-task';
  if (eventType.startsWith('agent.')) return 'tag-agent';
  if (eventType.startsWith('plan.')) return 'tag-plan';
  if (eventType.startsWith('tool.')) return 'tag-tool';
  if (eventType.startsWith('sandbox.')) return 'tag-sandbox';
  if (eventType.startsWith('provider.')) return 'tag-provider';
  return 'tag-default';
}

function getEventIcon(eventType) {
  const icons = {
    'task.started': '🚀', 'task.completed': '✅', 'task.failed': '❌',
    'agent.started': '🤖', 'agent.completed': '✓', 'agent.thinking': '💭',
    'plan.created': '📋', 'plan.step.started': '▶', 'plan.step.completed': '✓',
    'tool.selected': '🔧', 'tool.started': '⚡', 'tool.completed': '✓', 'tool.failed': '✗',
    'sandbox.started': '🐳', 'sandbox.command': '💻', 'sandbox.stdout': '📤',
    'sandbox.stderr': '⚠️', 'sandbox.exit': '🔴',
    'finding': '🔍', 'report.generated': '📄',
    'provider.request': '📡', 'provider.response': '📥',
    'warning': '⚠️', 'error': '❌',
  };
  return icons[eventType] || '●';
}

function formatEventLabel(eventType) {
  return eventType.split('.').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' › ');
}

function formatPayloadSummary(eventType, payload) {
  if (payload.message) return payload.message;
  if (eventType === 'sandbox.command') return `<code style="font-family:var(--font-mono);color:var(--text-code)">${escapeHtml(payload.command || '')}</code>`;
  if (eventType === 'tool.selected') return `Selected tool: <strong>${payload.tool_id || '?'}</strong>`;
  if (eventType === 'plan.created' && payload.plan) return `Plan created: ${(payload.plan.steps || []).length} steps`;
  if (eventType === 'finding') return `Findings recorded: ${payload.findings_count || 0}`;
  if (eventType === 'sandbox.exit') return `Exit code: <strong style="color:${payload.exit_code === 0 ? 'var(--accent-success)' : 'var(--accent-danger)'}">${payload.exit_code}</strong> — Duration: ${payload.duration}s`;
  return Object.keys(payload).length > 0 ? JSON.stringify(payload).substring(0, 100) : '';
}

function renderPayloadDetail(eventType, payload) {
  if (eventType === 'sandbox.stdout' && payload.stdout) {
    const output = payload.stdout.substring(0, 1000);
    return `<div class="event-payload"><pre>${escapeHtml(output)}</pre></div>`;
  }
  if (eventType === 'sandbox.stderr' && payload.stderr) {
    return `<div class="event-payload" style="color:var(--accent-warning)"><pre>${escapeHtml(payload.stderr.substring(0, 500))}</pre></div>`;
  }
  if (eventType === 'plan.created' && payload.plan) {
    const steps = (payload.plan.steps || []).map((s, i) => `${i+1}. [${s.agent_id}] ${s.description}`).join('\n');
    return `<div class="event-payload"><pre>${escapeHtml(steps)}</pre></div>`;
  }
  return '';
}

function clearTimeline() {
  document.getElementById('timeline').innerHTML = '';
}

function clearExecution() {
  if (currentWS) currentWS.close();
  document.getElementById('execution-view').style.display = 'none';
  currentExecutionId = null;
}

function updateStatusFromEvent(event) {
  const type = event.event_type || '';
  const statusMap = {
    'task.started': 'running', 'task.completed': 'done', 'task.failed': 'failed',
    'plan.created': 'planning', 'sandbox.command': 'executing',
  };
  if (statusMap[type]) updateStatusBadge(statusMap[type]);
}

function updateStatusBadge(status) {
  const badge = document.getElementById('exec-status-badge');
  badge.textContent = status;
  badge.className = `exec-status ${status}`;
}

// ── Data Loading ────────────────────────────────────────────────────────────

async function loadHistory() {
  const tbody = document.getElementById('history-tbody');
  tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Loading…</td></tr>';
  try {
    const res = await fetch(`${API}/tasks?limit=50`);
    const data = await res.json();
    if (!data.tasks || data.tasks.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No tasks yet.</td></tr>';
      return;
    }
    tbody.innerHTML = data.tasks.map(t => `
      <tr>
        <td style="max-width:300px;word-break:break-word">${escapeHtml(t.user_request)}</td>
        <td><span class="exec-status ${t.status}">${t.status}</span></td>
        <td style="font-family:var(--font-mono);font-size:0.75rem">${escapeHtml(t.execution_id?.substring(0,8) || '—')}</td>
        <td style="font-size:0.75rem">${formatDate(t.created_at)}</td>
        <td>
          <button class="btn-ghost" onclick="viewExecution('${t.execution_id}')">View</button>
          <a class="btn-ghost" style="text-decoration:none;display:inline-block;margin-left:4px"
             href="${API}/reports/${t.execution_id}?format=html" target="_blank">Report</a>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="empty-state">Error: ${err.message}</td></tr>`;
  }
}

function viewExecution(executionId) {
  showPanel('tasks');
  startExecution(executionId, 'loading');

  // Load historical events
  fetch(`${API}/executions/${executionId}/events`)
    .then(r => r.json())
    .then(data => {
      clearTimeline();
      (data.events || []).forEach(e => addTimelineEvent({
        event_type: e.event_type, agent_id: e.agent_id,
        timestamp: e.timestamp, payload: e.payload,
      }));
    });
}

async function loadProviders() {
  const grid = document.getElementById('providers-grid');
  grid.innerHTML = '<div class="empty-state">Loading…</div>';
  try {
    const res = await fetch(`${API}/providers`);
    const data = await res.json();
    const providers = data.providers || [];
    if (providers.length === 0) {
      grid.innerHTML = '<div class="empty-state">No providers loaded.</div>';
      return;
    }
    grid.innerHTML = providers.map(p => `
      <div class="provider-card">
        <div class="card-name">${p}</div>
        <div class="card-type">provider</div>
        <span class="card-badge">enabled</span>
      </div>
    `).join('');
  } catch {
    grid.innerHTML = '<div class="empty-state">Failed to load providers.</div>';
  }

  // Populate provider select in task form
  try {
    const res = await fetch(`${API}/providers`);
    const data = await res.json();
    const sel = document.getElementById('provider-select');
    sel.innerHTML = '<option value="">Default</option>' +
      (data.providers || []).map(p => `<option value="${p}">${p}</option>`).join('');
  } catch {}
}

async function loadTools() {
  const grid = document.getElementById('tools-grid');
  grid.innerHTML = '<div class="empty-state">Loading…</div>';
  try {
    const res = await fetch(`${API}/tools`);
    const data = await res.json();
    const tools = data.tools || [];
    if (tools.length === 0) {
      grid.innerHTML = '<div class="empty-state">No tools configured.</div>';
      return;
    }
    grid.innerHTML = tools.map(t => `
      <div class="tool-card">
        <div class="card-name">${t}</div>
        <div class="card-type">security tool</div>
        <span class="card-badge">docker</span>
      </div>
    `).join('');
  } catch {
    grid.innerHTML = '<div class="empty-state">Failed to load tools.</div>';
  }
}

// ── Utilities ───────────────────────────────────────────────────────────────

function escapeHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function formatDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString();
}

// ── Init ────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  checkHealth();
  setInterval(checkHealth, 30000);
  loadProviders(); // preload provider list for the dropdown
});
