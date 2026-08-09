const API_BASE = 'http://localhost:8081/api';

// State
let discoveries = [];
let currentFilter = '';
let activeDiscoveryId = null;

// DOM Elements
const elements = {
    total: document.getElementById('stat-total'),
    verified: document.getElementById('stat-verified'),
    unresolved: document.getElementById('stat-unresolved'),
    feed: document.getElementById('discovery-list'),
    detail: document.getElementById('detail-content'),
    filter: document.getElementById('domain-filter')
};

// Polling interval
setInterval(fetchStats, 5000);
setInterval(fetchDiscoveries, 5000);

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    fetchDiscoveries();
    
    elements.filter.addEventListener('change', (e) => {
        currentFilter = e.target.value;
        renderFeed();
    });
});

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const data = await res.json();
        
        elements.total.textContent = data.total;
        elements.verified.textContent = data.verified;
        elements.unresolved.textContent = data.unresolved;
    } catch (e) {
        console.error("Failed to fetch stats", e);
    }
}

async function fetchDiscoveries() {
    try {
        const url = new URL(`${API_BASE}/discoveries`);
        if (currentFilter) url.searchParams.append('domain', currentFilter);
        
        const res = await fetch(url);
        const data = await res.json();
        
        // Only re-render if data length changed or top item changed (simple check)
        if (discoveries.length !== data.length || (data.length > 0 && discoveries[0]?.id !== data[0].id)) {
            discoveries = data;
            renderFeed();
        }
    } catch (e) {
        console.error("Failed to fetch discoveries", e);
    }
}

function renderFeed() {
    if (discoveries.length === 0) {
        elements.feed.innerHTML = '<div class="loading-pulse">No discoveries found. The engine is working...</div>';
        return;
    }
    
    elements.feed.innerHTML = discoveries.map(d => `
        <div class="discovery-card" onclick="loadDetail('${d.id}')" id="card-${d.id}">
            <div class="card-header">
                <span class="badge ${d.lean_status.toLowerCase()}">${d.lean_status}</span>
                <span class="card-domain">${d.domain}</span>
            </div>
            <div class="card-conjecture">${d.conjecture || 'Structural Geometry'}</div>
            <div style="font-size: 0.75rem; color: #666; margin-top: 0.5rem; text-align: right;">
                Source: ${d.image_path.split('/').pop()}
            </div>
        </div>
    `).join('');
}

async function loadDetail(id) {
    try {
        const res = await fetch(`${API_BASE}/discoveries/${id}`);
        const data = await res.json();
        
        if (!data) return;
        
        // Update active state in list
        document.querySelectorAll('.discovery-card').forEach(c => c.style.borderColor = 'rgba(255,255,255,0.05)');
        const activeCard = document.getElementById(`card-${id}`);
        if(activeCard) activeCard.style.borderColor = 'var(--accent)';
        
        // Simple syntax highlighting for Lean 4
        let highlightedCode = data.lean_code
            .replace(/(--.*)/g, '<span class="comment">$1</span>')
            .replace(/\b(theorem|lemma|def|import|namespace|end|by|trivial|sorry|ring|norm_num)\b/g, '<span class="keyword">$1</span>');

        elements.detail.innerHTML = `
            <div class="detail-section">
                <h3>Provenance & Identity</h3>
                <div style="display: flex; gap: 2rem;">
                    <div>
                        <div class="metric-label">Notebook</div>
                        <div style="color: var(--text-main); font-weight: 500;">${data.notebook || 'Unknown'} / ${data.image_path.split('/').pop()}</div>
                    </div>
                    <div>
                        <div class="metric-label">Archetype</div>
                        <div style="color: var(--text-main); font-weight: 500;">${data.archetype}</div>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h3>RAMA Energy Profile</h3>
                <div class="energy-metrics">
                    <div class="metric">
                        <span class="metric-label">Total Energy</span>
                        <span class="metric-val" style="color: var(--success)">${data.rama_energy.toFixed(4)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Complexity (C)</span>
                        <span class="metric-val">${data.rama_C.toFixed(4)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Fit Error (I)</span>
                        <span class="metric-val">${data.rama_I.toFixed(4)}</span>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h3>Lean 4 Auto-Formalization</h3>
                <pre class="code-block"><code>${highlightedCode}</code></pre>
            </div>

            <div class="detail-section">
                <h3>Physics Mapping</h3>
                <div class="physics-map">
                    ${data.physics_mapping.replace(/\n/g, '<br>')}
                </div>
            </div>
        `;
    } catch (e) {
        console.error("Failed to load detail", e);
    }
}
