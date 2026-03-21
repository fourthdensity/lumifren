// Chart configuration
let performanceChart;
const maxDataPoints = 30;
let logsPaused = false;

const chartData = {
    labels: [],
    datasets: [{
        label: 'Latency',
        data: [],
        borderColor: '#00ffee',
        backgroundColor: 'rgba(0, 255, 238, 0.1)',
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 5
    }]
};

function initChart() {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { 
                    beginAtZero: true, 
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#707070', font: { family: 'JetBrains Mono', size: 10 } }
                },
                x: { display: false }
            },
            plugins: { 
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleFont: { family: 'JetBrains Mono' },
                    bodyFont: { family: 'JetBrains Mono' }
                }
            }
        }
    });
}

async function fetchStats() {
    try {
        const response = await fetch('/admin/api/stats');
        const data = await response.json();
        
        document.getElementById('stat-sessions').innerText = data.sessions_count;
        const redisEl = document.getElementById('stat-redis');
        redisEl.innerText = data.redis_available ? 'SYNCHRONIZED' : 'VOLATILE';
        redisEl.style.color = data.redis_available ? '#32d74b' : '#ff0055';
        
        document.getElementById('stat-memories').innerText = data.total_memories;
        document.getElementById('stat-latency').innerText = data.avg_latency ? `${Math.round(data.avg_latency)}MS` : '--MS';
        
        if (data.last_latency) {
            updateChart(new Date().toLocaleTimeString(), data.last_latency);
        }
        updateSessionList(data.sessions);
        updateUptime(data.uptime_seconds);
    } catch (e) { console.error('Stats fetch error:', e); }
}

function updateUptime(seconds) {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    document.getElementById('uptime-val').innerText = 
        `${hrs.toString().padStart(2,'0')}:${mins.toString().padStart(2,'0')}:${secs.toString().padStart(2,'0')}`;
}

async function fetchLogs() {
    if (logsPaused) return;
    try {
        const response = await fetch('/admin/api/logs');
        const logs = await response.json();
        renderLogs(logs);
    } catch (e) { console.error('Logs fetch error:', e); }
}

function renderLogs(logs) {
    const container = document.getElementById('log-container');
    container.innerHTML = logs.map(log => `
        <div class="log-entry">
            <span class="log-time">[${log.timestamp}]</span>
            <span class="log-level level-${log.level}">${log.level}</span>
            <span class="log-msg">${log.message}</span>
        </div>
    `).join('');
    container.scrollTop = container.scrollHeight;
}

window.loadSettings = async function() {
    try {
        const res = await fetch('/api/settings');
        const data = await res.json();
        document.getElementById('settings-model').value = data.model;
        document.getElementById('settings-proxy').value = data.proxy_url;
        document.getElementById('settings-auth').checked = data.enable_auth;
    } catch (e) { console.error('Settings load error:', e); }
}

window.saveSettings = async function() {
    const data = {
        model: document.getElementById('settings-model').value,
        proxy_url: document.getElementById('settings-proxy').value,
        enable_auth: document.getElementById('settings-auth').checked
    };
    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (res.ok) {
            const modalEl = document.getElementById('settingsModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
            fetchStats();
        }
    } catch (e) { alert('Failed to save kernel config'); }
}

function updateChart(label, value) {
    if (chartData.labels.length >= maxDataPoints) {
        chartData.labels.shift();
        chartData.datasets[0].data.shift();
    }
    chartData.labels.push(label);
    chartData.datasets[0].data.push(value);
    if (performanceChart) performanceChart.update();
}

function updateSessionList(sessions) {
    const list = document.getElementById('session-list');
    if (!sessions || sessions.length === 0) {
        list.innerHTML = '<div class="p-3 text-center text-muted small">NO ACTIVE UPLINKS</div>';
        return;
    }
    list.innerHTML = sessions.reverse().map(s => `
        <div class="node-item">
            <div class="node-info">
                <span class="name">${s.session_id}</span>
                <span class="meta">CYCLES: ${s.messages} // SYNAPSES: ${s.memories}</span>
            </div>
            <div class="status-pill">Active</div>
        </div>
    `).join('');
}

// Initialize
window.onload = () => {
    initChart();
    fetchStats();
    fetchLogs();
    
    setInterval(fetchStats, 5000);
    setInterval(fetchLogs, 2000);
};
