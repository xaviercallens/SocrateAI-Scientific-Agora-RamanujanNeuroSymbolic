const API_BASE = (
    window.NAMAGIRI_API_BASE
    || document.querySelector('meta[name="api-base"]')?.getAttribute('content')
    || 'http://127.0.0.1:8081/api'
);

// State
let discoveries = [];
let currentFilter = '';
let activeDiscoveryId = null;

// DOM Elements
const elements = {
    total: document.getElementById('stat-total'),
    verified: document.getElementById('stat-verified'),
    failed: document.getElementById('stat-failed'),
    unresolved: document.getElementById('stat-unresolved'),
    feed: document.getElementById('discovery-list'),
    detail: document.getElementById('detail-content'),
    filter: document.getElementById('domain-filter')
};

function formatNumber(value, digits = 4) {
    if (value === null || value === undefined || value === '') return 'N/A';
    const num = Number(value);
    return Number.isFinite(num) ? num.toFixed(digits) : 'N/A';
}

function formatBasename(path, fallback = 'Unknown') {
    if (!path) return fallback;
    const base = String(path).split('/').pop();
    return base || fallback;
}

function safeStatusClass(status) {
    return String(status || 'unresolved')
        .toLowerCase()
        .replace(/[^a-z0-9_-]/g, '') || 'unresolved';
}

function appendHighlightedLeanCode(codeEl, rawCode) {
    const source = String(rawCode || '');
    const tokenRe = /(--[^\n]*)|\b(theorem|lemma|def|structure|import|namespace|end|by|sorry|ring|norm_num|dsimp)\b/g;
    let lastIndex = 0;
    let match;

    while ((match = tokenRe.exec(source)) !== null) {
        if (match.index > lastIndex) {
            codeEl.appendChild(document.createTextNode(source.slice(lastIndex, match.index)));
        }
        const span = document.createElement('span');
        span.className = match[1] ? 'comment' : 'keyword';
        span.textContent = match[0];
        codeEl.appendChild(span);
        lastIndex = tokenRe.lastIndex;
    }

    if (lastIndex < source.length) {
        codeEl.appendChild(document.createTextNode(source.slice(lastIndex)));
    }
}

function createDetailSection(title) {
    const section = document.createElement('div');
    section.className = 'detail-section';
    const heading = document.createElement('h3');
    heading.textContent = title;
    section.appendChild(heading);
    return section;
}

function createMetric(label, value, valueColor = '') {
    const metric = document.createElement('div');
    metric.className = 'metric';

    const labelEl = document.createElement('span');
    labelEl.className = 'metric-label';
    labelEl.textContent = label;

    const valEl = document.createElement('span');
    valEl.className = 'metric-val';
    if (valueColor) {
        valEl.style.color = valueColor;
    }
    valEl.textContent = value;

    metric.append(labelEl, valEl);
    return metric;
}

function createCodeBlock(content, highlightLean = false) {
    const pre = document.createElement('pre');
    pre.className = 'code-block';
    const code = document.createElement('code');
    if (highlightLean) {
        appendHighlightedLeanCode(code, content);
    } else {
        code.textContent = String(content || '');
    }
    pre.appendChild(code);
    return pre;
}

function createDiscoveryCard(d) {
    const card = document.createElement('div');
    card.className = 'discovery-card';
    card.dataset.discoveryId = String(d.id ?? '');
    card.id = `card-${String(d.id ?? '')}`;
    if (activeDiscoveryId === d.id) {
        card.style.borderColor = 'var(--accent)';
    }

    const header = document.createElement('div');
    header.className = 'card-header';

    const badge = document.createElement('span');
    badge.className = `badge ${safeStatusClass(d.lean_status)}`;
    badge.textContent = d.lean_status || 'UNRESOLVED';

    const domain = document.createElement('span');
    domain.className = 'card-domain';
    domain.textContent = d.domain || 'Unknown';

    header.append(badge, domain);

    const conjecture = document.createElement('div');
    conjecture.className = 'card-conjecture';
    conjecture.textContent = d.conjecture || 'Structural Geometry';

    const source = document.createElement('div');
    source.style.fontSize = '0.75rem';
    source.style.color = '#666';
    source.style.marginTop = '0.5rem';
    source.style.textAlign = 'right';
    source.textContent = `Source: ${formatBasename(d.image_path)}`;

    card.append(header, conjecture, source);
    return card;
}

// Polling interval
setInterval(fetchStats, 5000);
setInterval(() => fetchDiscoveries(false), 5000);

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    fetchDiscoveries(true);

    elements.filter.addEventListener('change', (e) => {
        currentFilter = e.target.value;
        fetchDiscoveries(true);
    });

    elements.feed.addEventListener('click', (e) => {
        const card = e.target.closest('.discovery-card');
        if (!card) return;
        const discId = card.dataset.discoveryId;
        if (discId) {
            loadDetail(discId);
        }
    });
});

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        elements.total.textContent = data.total ?? '--';
        elements.verified.textContent = data.verified ?? '--';
        if (elements.failed) {
            elements.failed.textContent = data.failed ?? '--';
        }
        elements.unresolved.textContent = data.unresolved ?? '--';
    } catch (e) {
        console.error('Failed to fetch stats', e);
    }
}

async function fetchDiscoveries(force = false) {
    try {
        const url = new URL(`${API_BASE}/discoveries`, window.location.origin);
        if (currentFilter) url.searchParams.append('domain', currentFilter);

        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        const topChanged = data.length > 0 && discoveries[0]?.id !== data[0].id;
        if (force || discoveries.length !== data.length || topChanged) {
            discoveries = data;
            renderFeed();
        }
    } catch (e) {
        console.error('Failed to fetch discoveries', e);
    }
}

function renderFeed() {
    if (!Array.isArray(discoveries) || discoveries.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'loading-pulse';
        empty.textContent = 'No discoveries found. The engine is working...';
        elements.feed.replaceChildren(empty);
        return;
    }

    const cards = discoveries.map((d) => createDiscoveryCard(d));
    elements.feed.replaceChildren(...cards);
}

async function loadDetail(id) {
    try {
        const res = await fetch(`${API_BASE}/discoveries/${encodeURIComponent(id)}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        if (!data) return;
        activeDiscoveryId = id;

        // Update active state in list
        document.querySelectorAll('.discovery-card').forEach((c) => {
            c.style.borderColor = c.dataset.discoveryId === id
                ? 'var(--accent)'
                : 'rgba(255,255,255,0.05)';
        });

        const sections = [];

        // Provenance & Identity
        const provSection = createDetailSection('Provenance & Identity');
        const provRow = document.createElement('div');
        provRow.style.display = 'flex';
        provRow.style.gap = '2rem';

        const nbBlock = document.createElement('div');
        const nbLabel = document.createElement('div');
        nbLabel.className = 'metric-label';
        nbLabel.textContent = 'Notebook';
        const nbVal = document.createElement('div');
        nbVal.style.color = 'var(--text-main)';
        nbVal.style.fontWeight = '500';
        nbVal.textContent = `${data.notebook || 'Unknown'} / ${formatBasename(data.image_path)}`;
        nbBlock.append(nbLabel, nbVal);

        const archBlock = document.createElement('div');
        const archLabel = document.createElement('div');
        archLabel.className = 'metric-label';
        archLabel.textContent = 'Archetype';
        const archVal = document.createElement('div');
        archVal.style.color = 'var(--text-main)';
        archVal.style.fontWeight = '500';
        archVal.textContent = data.archetype || 'Unknown';
        archBlock.append(archLabel, archVal);

        provRow.append(nbBlock, archBlock);
        provSection.appendChild(provRow);
        sections.push(provSection);

        // RAMA Energy Profile
        const energySection = createDetailSection('RAMA Energy Profile');
        const metricsRow = document.createElement('div');
        metricsRow.className = 'energy-metrics';
        metricsRow.append(
            createMetric('Total Energy', formatNumber(data.rama_energy), 'var(--success)'),
            createMetric('Complexity (C)', formatNumber(data.rama_C)),
            createMetric('Fit Error (I)', formatNumber(data.rama_I))
        );
        energySection.appendChild(metricsRow);
        sections.push(energySection);

        // Lean 4 Auto-Formalization
        const leanSection = createDetailSection('Lean 4 Auto-Formalization');
        leanSection.appendChild(createCodeBlock(data.lean_code, true));
        sections.push(leanSection);

        // Optional Lean Output
        if (data.lean_error) {
            const errSection = createDetailSection('Lean Output');
            errSection.appendChild(createCodeBlock(data.lean_error, false));
            sections.push(errSection);
        }

        // Physics Mapping
        const physicsSection = createDetailSection('Physics Mapping');
        const physicsMap = document.createElement('div');
        physicsMap.className = 'physics-map';
        const lines = String(data.physics_mapping || 'None').split('\n');
        lines.forEach((line, idx) => {
            if (idx > 0) {
                physicsMap.appendChild(document.createElement('br'));
            }
            physicsMap.appendChild(document.createTextNode(line));
        });
        physicsSection.appendChild(physicsMap);
        sections.push(physicsSection);

        elements.detail.replaceChildren(...sections);
    } catch (e) {
        console.error('Failed to load detail', e);
    }
}
