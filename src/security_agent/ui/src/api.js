/**
 * API client for SecurityAgent FastAPI backend.
 */

const BASE_URL = '';

export async function checkHealth() {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

export async function fetchProviders() {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/providers`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch providers:', err);
    return [];
  }
}

export async function fetchTools() {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/tools`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch tools:', err);
    return [];
  }
}

export async function fetchExecutions(limit = 50) {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/executions?limit=${limit}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch executions:', err);
    return [];
  }
}

export async function fetchExecution(id) {
  const res = await fetch(`${BASE_URL}/api/v1/executions/${id}`);
  if (!res.ok) throw new Error(`Failed to load execution ${id}`);
  return await res.json();
}

export async function submitTask(taskPayload) {
  const res = await fetch(`${BASE_URL}/api/v1/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(taskPayload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Failed to submit task');
  }
  return await res.json();
}

export async function abortExecution(id) {
  const res = await fetch(`${BASE_URL}/api/v1/executions/${id}/abort`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to abort execution');
  return await res.json();
}

export async function fetchReport(id, format = 'json') {
  const res = await fetch(`${BASE_URL}/api/v1/reports/${id}?format=${format}`);
  if (!res.ok) throw new Error('Report not found');
  if (format === 'json') return await res.json();
  return await res.text();
}

// ── Memory & Brain API ───────────────────────────────────────────────────────

export async function fetchMemories(collection = 'lessons_learned', category = '', search = '') {
  try {
    const params = new URLSearchParams({ collection });
    if (category) params.append('category', category);
    if (search) params.append('search', search);

    const res = await fetch(`${BASE_URL}/api/v1/memory?${params.toString()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch memories:', err);
    return { collection, count: 0, items: [] };
  }
}

export async function createMemory(payload) {
  const res = await fetch(`${BASE_URL}/api/v1/memory`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to create memory item');
  return await res.json();
}

export async function updateMemory(collection, id, updates) {
  const res = await fetch(`${BASE_URL}/api/v1/memory/${collection}/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  if (!res.ok) throw new Error('Failed to update memory item');
  return await res.json();
}

export async function deleteMemory(collection, id) {
  const res = await fetch(`${BASE_URL}/api/v1/memory/${collection}/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete memory item');
  return await res.json();
}

export async function resetMemory(collection = null) {
  const res = await fetch(`${BASE_URL}/api/v1/memory/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ collection }),
  });
  if (!res.ok) throw new Error('Failed to reset memory');
  return await res.json();
}

// ── Hierarchy & Task Queue API ───────────────────────────────────────────────

export async function fetchHierarchy() {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/hierarchy`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch hierarchy:', err);
    return null;
  }
}

export async function fetchQueueStatus() {
  try {
    const res = await fetch(`${BASE_URL}/api/v1/hierarchy/queue`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch queue:', err);
    return { max_parent_slots: 3, active_count: 0, queued_count: 0, active_tasks: [], queued_tasks: [] };
  }
}

