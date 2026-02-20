/**
 * Disaster Recovery Dashboard — Real-Time Data Only
 * All region data is fetched live from the backend API (port 5000).
 * No hardcoded / simulated values are used for the region section.
 */

const API_BASE = `http://${window.location.hostname}:5000`;
const POLL_MS = 30_000;   // refresh every 30 seconds
const STATUS_MAP = {
    active: { cls: 'status-active', label: 'Active' },
    standby: { cls: 'status-standby', label: 'Standby' },
    cold: { cls: 'status-cold', label: 'Cold Standby' },
    degraded: { cls: 'status-standby', label: 'Degraded' },
    critical: { cls: 'status-active', label: 'Critical' },
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function svgIcon(path) {
    return `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">${path}</svg>`;
}
const ICON_INSTANCE = svgIcon('<rect x="2" y="3" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2"/>');
const ICON_DB = svgIcon('<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke="currentColor" stroke-width="2"/>');

function cpuColour(load) {
    if (load < 60) return 'var(--color-success)';
    if (load < 80) return 'var(--color-warning)';
    return 'var(--color-error)';
}

function timeAgo(isoString) {
    const diff = Math.floor((Date.now() - new Date(isoString + 'Z')) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return `${Math.floor(diff / 3600)}h ago`;
}

// ── Build one region card from real API data ──────────────────────────────────
function buildRegionCard(r) {
    const st = STATUS_MAP[r.status] || STATUS_MAP.standby;
    const color = cpuColour(r.cpu_load);

    return `
    <div class="region-card" data-region-id="${r.region_id}">
        <!-- top accent bar colour by load -->
        <div style="position:absolute;top:0;left:0;width:100%;height:4px;
                    background:linear-gradient(90deg,${color},var(--color-secondary));
                    border-radius:var(--radius-xl) var(--radius-xl) 0 0;"></div>

        <div class="region-header">
            <div class="region-info">
                <h3>${r.region_name}</h3>
                <span class="region-role">${r.role}</span>
            </div>
            <div class="region-status-indicator ${st.cls}">
                <span class="pulse"></span>
                ${st.label}
            </div>
        </div>

        <div class="region-metrics">
            <div class="metric">
                <span class="metric-label">Uptime</span>
                <span class="metric-value" style="color:var(--color-success)">
                    ${r.uptime.toFixed(2)}%
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">Latency</span>
                <span class="metric-value">${r.latency_ms.toFixed(0)}ms</span>
            </div>
            <div class="metric">
                <span class="metric-label">CPU Load</span>
                <span class="metric-value" style="color:${color}">
                    ${r.cpu_load.toFixed(1)}%
                </span>
            </div>
        </div>

        <!-- CPU load bar -->
        <div style="margin:0.5rem 0 1rem;">
            <div style="width:100%;height:6px;background:rgba(255,255,255,0.1);
                        border-radius:3px;overflow:hidden;">
                <div style="width:${Math.min(r.cpu_load, 100)}%;height:100%;
                            background:${color};border-radius:3px;
                            transition:width 1s ease;"></div>
            </div>
        </div>

        <div class="region-resources">
            <div class="resource-item">
                ${ICON_INSTANCE}
                <span>${r.instance_count} Instance${r.instance_count !== 1 ? 's' : ''}</span>
            </div>
            <div class="resource-item">
                ${ICON_DB}
                <span>${r.db_count} Database${r.db_count !== 1 ? 's' : ''}</span>
            </div>
            <div class="resource-item" style="margin-left:auto;opacity:0.6;font-size:0.7rem;">
                📡 ${timeAgo(r.timestamp)}
            </div>
        </div>

        <!-- Extra real metrics row -->
        <div style="display:grid;grid-template-columns:repeat(3,1fr);
                    gap:0.5rem;margin-top:1rem;padding-top:1rem;
                    border-top:1px solid var(--color-border);">
            <div style="text-align:center;">
                <div style="font-size:0.65rem;color:var(--color-text-tertiary);
                            text-transform:uppercase;letter-spacing:.05em;">Error Rate</div>
                <div style="font-size:1rem;font-weight:700;
                            color:${r.error_rate > 2 ? 'var(--color-error)' : 'var(--color-success)'}">
                    ${r.error_rate.toFixed(2)}%
                </div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:0.65rem;color:var(--color-text-tertiary);
                            text-transform:uppercase;letter-spacing:.05em;">Net In</div>
                <div style="font-size:1rem;font-weight:700;color:var(--color-primary-light)">
                    ${r.network_in.toFixed(0)} MB/s
                </div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:0.65rem;color:var(--color-text-tertiary);
                            text-transform:uppercase;letter-spacing:.05em;">Net Out</div>
                <div style="font-size:1rem;font-weight:700;color:var(--color-accent)">
                    ${r.network_out.toFixed(0)} MB/s
                </div>
            </div>
        </div>
    </div>`;
}

// ── Error card when API is unreachable ────────────────────────────────────────
function buildErrorCard(msg) {
    return `
    <div class="region-card" style="grid-column:1/-1;text-align:center;padding:3rem;
                                     border-color:var(--color-error);">
        <div style="font-size:2rem;margin-bottom:1rem;">⚠️</div>
        <p style="color:var(--color-error);font-size:1rem;font-weight:600;">
            Cannot reach API server
        </p>
        <p style="color:var(--color-text-tertiary);font-size:0.8rem;margin-top:0.5rem;">
            ${msg}
        </p>
        <p style="color:var(--color-text-tertiary);font-size:0.75rem;margin-top:1rem;">
            Make sure <code>python3 backend/api_server.py</code> is running on port 5000
        </p>
    </div>`;
}

// ── Fetch & render region cards ───────────────────────────────────────────────
async function refreshRegions() {
    const grid = document.getElementById('region-grid');
    const lastUpd = document.getElementById('region-last-updated');
    if (!grid) return;

    try {
        const res = await fetch(`${API_BASE}/api/regions`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        const regions = json.regions;

        if (!regions || regions.length === 0) {
            grid.innerHTML = buildErrorCard('API returned no region data yet — retrying…');
            return;
        }

        // Build cards from real data only
        grid.innerHTML = regions.map(buildRegionCard).join('');

        // Update timestamp
        const now = new Date().toLocaleTimeString();
        if (lastUpd) lastUpd.textContent = `Last updated: ${now}`;

        // Update system status header
        const allActive = regions.every(r => r.status === 'active');
        const anyDown = regions.some(r => r.status === 'critical');
        updateSystemStatus(anyDown ? 'outage' : allActive ? 'operational' : 'degraded');

    } catch (err) {
        console.error('Region fetch error:', err);
        grid.innerHTML = buildErrorCard(err.message);
        if (lastUpd) lastUpd.textContent = `Failed at ${new Date().toLocaleTimeString()}`;
        updateSystemStatus('degraded');
    }
}

// ── System status header ──────────────────────────────────────────────────────
function updateSystemStatus(status) {
    const el = document.querySelector('.system-status');
    const txt = document.querySelector('.status-text');
    const dot = document.querySelector('.status-indicator');
    if (!el) return;
    const cfg = {
        operational: { text: 'All Systems Operational', cls: 'status-operational', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.3)' },
        degraded: { text: 'System Degraded', cls: 'status-degraded', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.3)' },
        outage: { text: 'System Outage', cls: 'status-outage', bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.3)' },
    }[status] || cfg.operational;
    if (txt) txt.textContent = cfg.text;
    if (dot) dot.className = `status-indicator ${cfg.cls}`;
    el.style.background = cfg.bg;
    el.style.borderColor = cfg.border;
}

// ── Notification badge ────────────────────────────────────────────────────────
function setupButtons() {
    document.getElementById('notificationBtn')?.addEventListener('click', () => {
        alert('No new alerts at this time.');
    });
    document.getElementById('settingsBtn')?.addEventListener('click', () => {
        alert('Settings panel coming soon.');
    });
}

// ── Animate sections on load ──────────────────────────────────────────────────
function animateSections() {
    document.querySelectorAll('.section').forEach((s, i) => {
        s.style.opacity = '0';
        s.style.transform = 'translateY(20px)';
        setTimeout(() => {
            s.style.transition = 'all 0.6s ease-out';
            s.style.opacity = '1';
            s.style.transform = 'translateY(0)';
        }, i * 100);
    });
    // Animate progress bars
    setTimeout(() => {
        document.querySelectorAll('.component-bar-fill, .progress-fill').forEach(bar => {
            const w = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => { bar.style.width = w; }, 100);
        });
    }, 500);
}

// ── Inject CSS animations ─────────────────────────────────────────────────────
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(400px); opacity: 0; }
        to   { transform: translateX(0);     opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0);     opacity: 1; }
        to   { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// ── Boot ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    animateSections();
    setupButtons();

    // First fetch immediately, then poll
    refreshRegions();
    setInterval(refreshRegions, POLL_MS);

    console.log(`Dashboard started — polling API every ${POLL_MS / 1000}s`);
});
