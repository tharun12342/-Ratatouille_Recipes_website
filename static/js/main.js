// ═══ PANTRY STATE ══════════════════════════════════════════════════════════
let pantryItems = [];

async function loadPantry() {
  const r = await fetch('/api/pantry/');
  const d = await r.json();
  pantryItems = d.ingredients;
  updatePantryUI();
}

function updatePantryUI() {
  const count = pantryItems.length;
  document.getElementById('pantry-count').textContent = count;
  const container = document.getElementById('pantry-items-container');
  const findBtn = document.getElementById('find-recipes-btn');

  if (!count) {
    container.innerHTML = `<div class="empty-pantry"><div class="big-icon">🧺</div><p>Your pantry is empty.<br>Add ingredients from the home page.</p></div>`;
    findBtn.style.display = 'none';
    return;
  }

  findBtn.style.display = 'flex';

  const grouped = {};
  for (const item of pantryItems) {
    if (!grouped[item.category]) grouped[item.category] = [];
    grouped[item.category].push(item);
  }

  let html = '';
  for (const [cat, items] of Object.entries(grouped)) {
    html += `<div style="margin-bottom:20px;"><div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;letter-spacing:0.15em;color:var(--gold);margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--border);">${cat}</div><div>`;
    for (const item of items) {
      html += `<span class="pantry-tag">${item.name}<button onclick="removeFromPantry(${item.id},'${item.name}')">×</button></span>`;
    }
    html += '</div></div>';
  }
  container.innerHTML = html;

  document.querySelectorAll('[data-ing-id]').forEach(btn => {
    const id = parseInt(btn.dataset.ingId);
    const inPantry = pantryItems.some(p => p.id === id);
    btn.classList.toggle('in-pantry', inPantry);
    btn.title = inPantry ? 'Remove from pantry' : 'Add to pantry';
  });
}

async function togglePantry(ingId, action = 'toggle') {
  const r = await fetch('/api/pantry/toggle/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
    body: JSON.stringify({ ingredient_id: ingId, action })
  });
  const d = await r.json();
  if (d.success) {
    await loadPantry();
    showToast(d.in_pantry ? `✦ ${d.name} added to pantry` : `Removed ${d.name}`, d.in_pantry ? 'success' : '');
  }
}

async function removeFromPantry(id, name) { await togglePantry(id, 'remove'); }

async function clearPantry() {
  if (!confirm('Clear all items from your pantry?')) return;
  await fetch('/api/pantry/clear/', { method: 'POST', headers: { 'X-CSRFToken': getCsrf() } });
  await loadPantry();
  showToast('Pantry cleared');
}

function openDrawer() {
  document.getElementById('pantry-drawer').classList.add('open');
  document.getElementById('drawer-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeDrawer() {
  document.getElementById('pantry-drawer').classList.remove('open');
  document.getElementById('drawer-overlay').classList.remove('open');
  document.body.style.overflow = '';
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDrawer(); });

// ─── Toast ──────────────────────────────────────────────────────────────
function showToast(msg, type = '') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

function getCsrf() {
  // Primary: read from meta tag (always present due to context processor)
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta && meta.content) return meta.content;
  // Fallback: read from cookie
  return document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1] || '';
}

/* ─── 3D Noto Emoji Image Renderer ─────────────────────────────────── */
function emojiToNotoUrl(emoji) {
  const codepoints = [...emoji]
    .map(c => c.codePointAt(0).toString(16))
    .filter(cp => parseInt(cp, 16) > 0xfe)
    .join('-');
  return `https://fonts.gstatic.com/s/e/notoemoji/latest/${codepoints}/512.webp`;
}

function renderEmojiImages() {
  document.querySelectorAll('[data-emoji]').forEach(el => {
    const emoji = el.dataset.emoji;
    if (!emoji || emoji.trim() === '') return;

    // If already rendered, skip
    if (el.querySelector('img')) return;

    const img = document.createElement('img');
    img.src = emojiToNotoUrl(emoji);
    img.alt = emoji;
    img.onerror = () => {
      img.remove();
      el.textContent = emoji;
      el.style.fontSize = 'inherit';
      // Disable filters on text fallback so it looks normal
      if (el.parentElement.classList.contains('emoji-3d-wrap')) {
        el.parentElement.style.filter = 'none';
        el.parentElement.style.animation = 'none';
      }
    };
    el.innerHTML = '';
    el.appendChild(img);
  });
}

document.addEventListener('DOMContentLoaded', renderEmojiImages);

loadPantry();
