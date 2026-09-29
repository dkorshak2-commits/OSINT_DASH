const $ = (selector) => document.querySelector(selector);
let selected = null;

async function api(path, options = {}) {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) throw new Error((await response.json()).detail || 'Request failed');
  return response.status === 204 ? null : response.json();
}

function renderTargets(targets) {
  $('#target-count').textContent = `${targets.length} ACTIVE`;
  $('#targets').innerHTML = targets.length ? targets.map(t => `
    <article class="target ${selected?.id === t.id ? 'selected' : ''}" data-id="${t.id}">
      <div class="target-icon">${t.target_type === 'website' ? '◎' : t.target_type === 'business' ? '□' : '◇'}</div>
      <div class="target-copy"><strong>${escapeHtml(t.name)}</strong><small>${t.target_type.toUpperCase()} · ${new Date(t.created_at).toLocaleDateString()}</small></div>
      <button class="scan" title="Run passive scan">SCAN ↗</button><button class="delete" title="Delete target">×</button>
    </article>`).join('') : '<div class="empty">No targets yet.<br><small>Add one to begin your workspace.</small></div>';
  document.querySelectorAll('.target').forEach(card => {
    card.onclick = (event) => { if (event.target.closest('.delete') || event.target.closest('.scan')) return; selected = targets.find(t => t.id == card.dataset.id); renderTargets(targets); loadFindings(selected.id); };
    card.querySelector('.scan').onclick = () => scan(card.dataset.id);
    card.querySelector('.delete').onclick = async () => { if (confirm('Delete this target and its findings?')) { await api(`/api/targets/${card.dataset.id}`, { method: 'DELETE' }); if (selected?.id == card.dataset.id) { selected = null; $('#findings').innerHTML = '<div class="empty">Select a target and run a passive scan to see results here.</div>'; } loadTargets(); } };
  });
}

async function loadTargets() { renderTargets(await api('/api/targets')); }
async function loadFindings(id) {
  $('#findings-title').textContent = `Findings · ${selected.name}`;
  const findings = await api(`/api/targets/${id}/findings`);
  renderFindings(findings.flatMap(f => f.data));
}
async function scan(id) {
  $('#scan-state').textContent = 'SCANNING…'; $('#findings').innerHTML = '<div class="empty loader">Collecting passive DNS and HTTP context…</div>';
  try { const result = await api(`/api/targets/${id}/scan`, { method: 'POST' }); selected = result.target; renderFindings(result.findings); $('#scan-state').textContent = 'SCAN COMPLETE'; }
  catch (error) { $('#findings').innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`; $('#scan-state').textContent = 'SCAN FAILED'; }
}
function renderFindings(items) { $('#findings').innerHTML = items.length ? items.map(item => `<div class="finding"><span class="finding-dot"></span><pre>${escapeHtml(JSON.stringify(item, null, 2))}</pre></div>`).join('') : '<div class="empty">No passive findings returned.</div>'; }
function escapeHtml(value) { return String(value).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
$('#target-form').onsubmit = async (event) => { event.preventDefault(); try { await api('/api/targets', { method: 'POST', body: JSON.stringify({ name: $('#name').value, target_type: $('#type').value, notes: $('#notes').value }) }); event.target.reset(); await loadTargets(); } catch (error) { alert(error.message); } };
loadTargets();