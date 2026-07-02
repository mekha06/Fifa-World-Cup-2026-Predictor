/**
 * main.js — FIFA World Cup 2026 Predictor Frontend
 * All UI logic: API calls, chart rendering, simulation control, canvas BG
 */

const API = '/api';

// ── State ────────────────────────────────────────────────────────────────────
const state = {
  mode: 'random',
  numSims: 1000,
  stage: 'Winner_prob',
  confFilter: 'ALL',
  results: [],
  teams: [],
  groups: {},
  jobId: null,
  polling: null,
};

// ── DOM refs ─────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const btnRandom    = $('btn-mode-random');
const btnScheduled = $('btn-mode-scheduled');
const slider       = $('sim-count-slider');
const sliderDisp   = $('sim-count-display');
const btnRun       = $('btn-run-sim');
const btnLabel     = $('run-btn-label');
const progressWrap = $('sim-progress-wrap');
const progressBar  = $('progress-bar');
const progressPct  = $('progress-pct');
const podiumEl     = $('podium');
const chartEl      = $('results-chart');
const groupsGrid   = $('groups-grid');
const teamsGrid    = $('teams-grid');

// ── Animated Canvas Background ───────────────────────────────────────────────
function initCanvas() {
  const canvas = $('bg-canvas');
  const ctx = canvas.getContext('2d');
  let W, H, particles = [];

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function mkParticle() {
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.5 + 0.3,
      vx: (Math.random() - 0.5) * 0.2,
      vy: -(Math.random() * 0.3 + 0.05),
      alpha: Math.random() * 0.6 + 0.1,
      color: Math.random() > 0.6
        ? `rgba(245,200,66,`
        : Math.random() > 0.5
          ? `rgba(59,130,246,`
          : `rgba(240,242,255,`,
    };
  }

  function init() {
    resize();
    particles = Array.from({ length: 120 }, mkParticle);
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    for (const p of particles) {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color + p.alpha + ')';
      ctx.fill();
      p.x += p.vx;
      p.y += p.vy;
      if (p.y < -5 || p.x < -5 || p.x > W + 5) Object.assign(p, mkParticle(), { y: H + 5 });
    }
    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  init();
  draw();
}

// ── Slider ───────────────────────────────────────────────────────────────────
function initSlider() {
  function update() {
    const v = +slider.value;
    state.numSims = v;
    sliderDisp.textContent = v >= 1000 ? `${(v/1000).toFixed(v % 1000 === 0 ? 0 : 1)}K` : v.toString();
    const pct = ((v - +slider.min) / (+slider.max - +slider.min)) * 100;
    slider.style.setProperty('--pct', pct + '%');
  }
  slider.addEventListener('input', update);
  update();
}

// ── Mode toggle ──────────────────────────────────────────────────────────────
function initModeToggle() {
  [btnRandom, btnScheduled].forEach(btn => {
    btn.addEventListener('click', () => {
      state.mode = btn.dataset.mode;
      btnRandom.classList.toggle('active', state.mode === 'random');
      btnScheduled.classList.toggle('active', state.mode === 'scheduled');
      // Load cached results for this mode
      loadCachedResults();
    });
  });
}

// ── Stage tabs ────────────────────────────────────────────────────────────────
function initStageTabs() {
  document.querySelectorAll('.stage-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.stage-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.stage = tab.dataset.stage;
      renderChart();
    });
  });
}

// ── Conf filter ───────────────────────────────────────────────────────────────
function initConfFilter() {
  document.querySelectorAll('.conf-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.conf-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.confFilter = btn.dataset.conf;
      renderChart();
    });
  });
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

// ── API helpers ───────────────────────────────────────────────────────────────
async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, opts);
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  return res.json();
}

// ── Load teams ────────────────────────────────────────────────────────────────
async function loadTeams() {
  try {
    const data = await apiFetch('/teams');
    state.teams = data.teams || [];
    renderTeamsGrid();
  } catch (e) {
    console.warn('teams fetch failed', e);
  }
}

// ── Load groups ───────────────────────────────────────────────────────────────
async function loadGroups() {
  try {
    const data = await apiFetch('/groups');
    state.groups = data.groups || {};
    renderGroupsGrid();
  } catch (e) {
    console.warn('groups fetch failed', e);
  }
}

// ── Load cached results ───────────────────────────────────────────────────────
async function loadCachedResults() {
  try {
    const endpoint = state.mode === 'scheduled' ? '/results/scheduled' : '/results/random';
    const data = await apiFetch(endpoint);
    if (data.results && data.results.length) {
      state.results = data.results;
      renderPodium();
      renderChart();
    }
  } catch (e) {
    console.warn('results fetch failed', e);
  }
}

// ── Run simulation ────────────────────────────────────────────────────────────
async function runSimulation() {
  if (state.jobId) return;

  btnRun.disabled = true;
  btnLabel.textContent = 'LAUNCHING…';
  btnRun.classList.add('running');
  progressWrap.classList.remove('hidden');
  setProgress(0);

  try {
    const data = await apiFetch('/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: state.mode, num_simulations: state.numSims }),
    });
    state.jobId = data.job_id;
    btnLabel.textContent = 'SIMULATING…';
    pollJob();
  } catch (e) {
    showToast('❌ Failed to start simulation. Is the backend running?', 'error');
    resetRunBtn();
  }
}

function setProgress(pct) {
  progressBar.style.width = pct + '%';
  progressPct.textContent = pct + '%';

  // Light up steps
  const steps = document.querySelectorAll('.step');
  steps.forEach((s, i) => {
    s.classList.toggle('active', pct >= i * 25);
  });
}

function pollJob() {
  state.polling = setInterval(async () => {
    try {
      const data = await apiFetch(`/simulate/status/${state.jobId}`);
      setProgress(data.progress || 0);

      if (data.status === 'done') {
        clearInterval(state.polling);
        state.jobId = null;
        state.results = data.result || [];
        setProgress(100);
        setTimeout(() => {
          progressWrap.classList.add('hidden');
          resetRunBtn();
          renderPodium();
          renderChart();
          showToast(`✅ Simulation complete! ${state.numSims.toLocaleString()} tournaments run.`, 'success');
        }, 600);
      } else if (data.status === 'error') {
        clearInterval(state.polling);
        state.jobId = null;
        showToast('❌ Simulation error: ' + data.error, 'error');
        resetRunBtn();
      }
    } catch (e) {
      clearInterval(state.polling);
      state.jobId = null;
      showToast('❌ Lost connection to backend.', 'error');
      resetRunBtn();
    }
  }, 800);
}

function resetRunBtn() {
  btnRun.disabled = false;
  btnRun.classList.remove('running');
  btnLabel.textContent = 'RUN SIMULATION';
}

// ── Render Podium ─────────────────────────────────────────────────────────────
function renderPodium() {
  const top3 = state.results.slice(0, 3);
  const medals = ['🥇', '🥈', '🥉'];
  const rankClass = ['rank-1', 'rank-2', 'rank-3'];

  podiumEl.innerHTML = top3.map((t, i) => `
    <div class="podium-card ${rankClass[i]} anim-fade-up" style="animation-delay:${i*0.12}s">
      <div class="podium-medal">${medals[i]}</div>
      <div class="podium-flag">${t.flag}</div>
      <div class="podium-name">${t.Team}</div>
      <div class="podium-conf">${t.confederation}</div>
      <div class="podium-prob">${(t.Winner_prob * 100).toFixed(1)}%</div>
      <div class="podium-prob-lbl">Win Probability</div>
    </div>
  `).join('');
}

// ── Render Chart ──────────────────────────────────────────────────────────────
function renderChart() {
  let data = [...state.results];

  // Confederation filter
  if (state.confFilter !== 'ALL') {
    data = data.filter(t => t.confederation === state.confFilter);
  }

  // Sort by current stage
  data.sort((a, b) => (b[state.stage] || 0) - (a[state.stage] || 0));

  if (!data.length) {
    chartEl.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <div class="empty-state-text">No teams match this filter.</div>
      </div>`;
    return;
  }

  const maxProb = data[0][state.stage] || 1;

  chartEl.innerHTML = data.map((t, idx) => {
    const prob = t[state.stage] || 0;
    const pct = maxProb > 0 ? (prob / maxProb) * 100 : 0;
    const conf = t.confederation || 'UEFA';
    return `
      <div class="chart-row">
        <span class="chart-rank">${idx + 1}</span>
        <div class="chart-team-info">
          <span class="chart-flag">${t.flag}</span>
          <div>
            <div class="chart-name">${t.Team}</div>
            <span class="chart-conf-badge conf-${conf}">${conf}</span>
          </div>
        </div>
        <div class="chart-bar-track">
          <div class="chart-bar bar-${conf}" style="width:0%" data-target="${pct}"></div>
        </div>
        <span class="chart-pct">${(prob * 100).toFixed(1)}%</span>
      </div>`;
  }).join('');

  // Animate bars in
  requestAnimationFrame(() => {
    chartEl.querySelectorAll('.chart-bar').forEach((bar, i) => {
      setTimeout(() => {
        bar.style.width = bar.dataset.target + '%';
      }, i * 25);
    });
  });
}

// ── Render Groups ─────────────────────────────────────────────────────────────
function renderGroupsGrid() {
  const entries = Object.entries(state.groups);
  groupsGrid.innerHTML = entries.map(([gname, teams]) => `
    <div class="group-card anim-fade-up glass">
      <div class="group-header">
        <span class="group-name">GROUP ${gname}</span>
        <span class="group-venue">4 nations</span>
      </div>
      ${teams.map(t => `
        <div class="group-team-row">
          <span class="group-team-flag">${t.flag}</span>
          <div class="group-team-info">
            <div class="group-team-name">${t.team}</div>
            <div class="group-team-elo">Elo ${t.elo} · <span class="chart-conf-badge conf-${t.confederation}">${t.confederation}</span></div>
          </div>
          <span class="group-team-strength">${t.strength.toFixed(0)}</span>
        </div>
      `).join('')}
    </div>
  `).join('');
}

// ── Render Teams Grid ─────────────────────────────────────────────────────────
function renderTeamsGrid() {
  teamsGrid.innerHTML = state.teams.map((t, i) => `
    <div class="team-card anim-fade-up" style="animation-delay:${(i % 12) * 0.04}s">
      <div class="team-card-flag">${t.flag}</div>
      <div class="team-card-rank">#${i + 1}</div>
      <div class="team-card-name">${t.team}</div>
      <span class="team-card-conf team-card-conf conf-${t.confederation}">${t.confederation}</span>
      <div class="team-card-stats">
        <div class="team-stat-item">
          <div class="team-stat-val">${t.elo}</div>
          <div class="team-stat-lbl">Elo</div>
        </div>
        <div class="team-stat-item">
          <div class="team-stat-val">${t.predicted_stage.toFixed(1)}</div>
          <div class="team-stat-lbl">ML Stage</div>
        </div>
      </div>
    </div>
  `).join('');
}

// ── Navbar scroll effect ──────────────────────────────────────────────────────
function initNavbar() {
  const nav = $('navbar');
  window.addEventListener('scroll', () => {
    nav.style.background = window.scrollY > 50
      ? 'rgba(5,6,15,0.97)'
      : 'rgba(5,6,15,0.85)';
  });
}

// ── Intersection observer for section animations ───────────────────────────────
function initScrollAnimations() {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.querySelectorAll('.anim-fade-up').forEach((el, i) => {
          el.style.opacity = '0';
          el.style.animationDelay = el.style.animationDelay || `${i * 0.05}s`;
          el.style.animationPlayState = 'running';
        });
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('section').forEach(s => io.observe(s));
}

// ── Empty states while loading ────────────────────────────────────────────────
function showLoadingStates() {
  chartEl.innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon">⏳</div>
      <div class="empty-state-text">Loading results… (make sure backend is running)</div>
    </div>`;
  groupsGrid.innerHTML = Array(12).fill(0).map(() =>
    `<div class="skeleton" style="height:200px;border-radius:14px;"></div>`
  ).join('');
  teamsGrid.innerHTML = Array(12).fill(0).map(() =>
    `<div class="skeleton" style="height:160px;border-radius:14px;"></div>`
  ).join('');
}

// ── Boot ──────────────────────────────────────────────────────────────────────
async function init() {
  initCanvas();
  initSlider();
  initModeToggle();
  initStageTabs();
  initConfFilter();
  initNavbar();

  btnRun.addEventListener('click', runSimulation);

  showLoadingStates();

  // Load all data in parallel
  await Promise.all([
    loadTeams(),
    loadGroups(),
    loadCachedResults(),
  ]);
}

init();
