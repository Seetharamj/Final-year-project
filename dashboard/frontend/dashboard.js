/**
 * Disaster Recovery Dashboard - Interactive JavaScript
 * Real-time updates, WebSocket connections, and dynamic visualizations
 */

class DisasterRecoveryDashboard {
    constructor() {
        this.ws = null;
        this.updateInterval = null;
        this.init();
    }

    init() {
        console.log('Initializing Disaster Recovery Dashboard...');
        this.setupWebSocket();
        this.setupEventListeners();
        this.startRealTimeUpdates();
        this.animateOnLoad();
    }

    setupWebSocket() {
        // Connect to backend WebSocket for real-time updates
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = window.location.hostname;
        const wsUrl = `${wsProtocol}//${wsHost}:5000/ws`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected to backend');
                this.updateSystemStatus('operational');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealtimeUpdate(data);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateSystemStatus('degraded');
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected. Reconnecting...');
                setTimeout(() => this.setupWebSocket(), 5000);
            };
        } catch (error) {
            console.warn('WebSocket not available, using polling fallback');
            this.startPolling();
        }
    }

    handleRealtimeUpdate(data) {
        switch (data.type) {
            case 'metrics':
                this.updateMetrics(data.payload);
                break;
            case 'anomaly':
                this.handleAnomaly(data.payload);
                break;
            case 'prediction':
                this.updatePredictions(data.payload);
                break;
            case 'region_status':
                this.updateRegionStatus(data.payload);
                break;
            case 'activity':
                this.addActivity(data.payload);
                break;
            default:
                console.log('Unknown update type:', data.type);
        }
    }

    startPolling() {
        // Fallback polling if WebSocket is not available
        this.updateInterval = setInterval(() => {
            this.fetchLatestData();
        }, 5000); // Poll every 5 seconds
    }

    async fetchLatestData() {
        try {
            const apiUrl = `http://${window.location.hostname}:5000/api/dashboard/latest`;
            const response = await fetch(apiUrl);
            const data = await response.json();
            this.handleRealtimeUpdate(data);
        } catch (error) {
            console.error('Error fetching latest data:', error);
        }
    }

    updateMetrics(metrics) {
        // Update various metrics on the dashboard
        if (metrics.riskScore !== undefined) {
            this.updateRiskScore(metrics.riskScore);
        }

        if (metrics.regions) {
            metrics.regions.forEach(region => {
                this.updateRegionMetrics(region);
            });
        }

        if (metrics.ai) {
            this.updateAIInsights(metrics.ai);
        }
    }

    updateRiskScore(score) {
        const scoreElement = document.querySelector('.score-number');
        const ringElement = document.querySelector('.score-ring-fill');
        const badgeElement = document.querySelector('.risk-badge');

        if (scoreElement) {
            this.animateNumber(scoreElement, parseInt(scoreElement.textContent), score);
        }

        if (ringElement) {
            ringElement.style.setProperty('--progress', score / 100);
        }

        if (badgeElement) {
            const level = this.getRiskLevel(score);
            badgeElement.textContent = level;
            badgeElement.className = `risk-badge risk-${level.toLowerCase()}`;
        }
    }

    getRiskLevel(score) {
        if (score < 20) return 'LOW';
        if (score < 40) return 'MODERATE';
        if (score < 70) return 'HIGH';
        return 'EXTREME';
    }

    updateRegionMetrics(region) {
        const regionCard = document.querySelector(`[data-region="${region.id}"]`);
        if (!regionCard) return;

        // Update metrics
        const metrics = {
            uptime: region.uptime,
            latency: region.latency,
            load: region.load
        };

        Object.entries(metrics).forEach(([key, value]) => {
            const element = regionCard.querySelector(`[data-metric="${key}"]`);
            if (element) {
                element.textContent = this.formatMetricValue(key, value);
            }
        });

        // Update status
        const statusElement = regionCard.querySelector('.region-status-indicator');
        if (statusElement && region.status) {
            statusElement.className = `region-status-indicator status-${region.status}`;
            statusElement.querySelector('span:last-child').textContent =
                region.status.charAt(0).toUpperCase() + region.status.slice(1);
        }
    }

    formatMetricValue(metric, value) {
        switch (metric) {
            case 'uptime':
                return `${value.toFixed(2)}%`;
            case 'latency':
                return `${value}ms`;
            case 'load':
                return `${value}%`;
            default:
                return value;
        }
    }

    updateAIInsights(ai) {
        // Update anomaly detection
        if (ai.anomalies !== undefined) {
            const anomalyElement = document.querySelector('.insight-card .stat-value');
            if (anomalyElement) {
                this.animateNumber(anomalyElement,
                    parseInt(anomalyElement.textContent),
                    ai.anomalies);
            }
        }

        // Update degradation prediction
        if (ai.degradationProbability !== undefined) {
            const predElement = document.querySelector('.insight-card:nth-child(2) .stat-value');
            if (predElement) {
                predElement.textContent = `${(ai.degradationProbability * 100).toFixed(1)}%`;
            }
        }

        // Update RTO/RPO
        if (ai.rto || ai.rpo) {
            this.updateRTORPO(ai.rto, ai.rpo);
        }
    }

    updateRTORPO(rto, rpo) {
        if (rto) {
            const rtoElement = document.querySelector('[data-metric="current-rto"]');
            if (rtoElement) {
                rtoElement.textContent = `${rto.toFixed(1)}min`;
            }
        }

        if (rpo) {
            const rpoElement = document.querySelector('[data-metric="current-rpo"]');
            if (rpoElement) {
                rpoElement.textContent = `${rpo.toFixed(1)}min`;
            }
        }
    }

    handleAnomaly(anomaly) {
        // Show notification
        this.showNotification({
            type: 'warning',
            title: 'Anomaly Detected',
            message: `${anomaly.severity} anomaly in ${anomaly.affected_metrics.join(', ')}`,
            timestamp: anomaly.timestamp
        });

        // Update notification badge
        this.incrementNotificationBadge();

        // Add to activity feed
        this.addActivity({
            type: 'anomaly',
            title: 'Anomaly Detected',
            description: `${anomaly.severity} severity - ${anomaly.affected_metrics.join(', ')}`,
            timestamp: anomaly.timestamp,
            icon: 'warning'
        });
    }

    addActivity(activity) {
        const activityList = document.querySelector('.activity-list');
        if (!activityList) return;

        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.style.animation = 'fadeIn 0.5s ease-out';

        const iconClass = this.getActivityIconClass(activity.icon || activity.type);

        activityItem.innerHTML = `
            <div class="activity-icon ${iconClass}">
                ${this.getActivityIcon(activity.icon || activity.type)}
            </div>
            <div class="activity-content">
                <h4>${activity.title}</h4>
                <p>${activity.description}</p>
                <span class="activity-time">${this.formatTimestamp(activity.timestamp)}</span>
            </div>
        `;

        // Insert at the beginning
        activityList.insertBefore(activityItem, activityList.firstChild);

        // Keep only last 10 activities
        while (activityList.children.length > 10) {
            activityList.removeChild(activityList.lastChild);
        }
    }

    getActivityIconClass(type) {
        const iconMap = {
            success: 'success',
            warning: 'warning',
            error: 'error',
            info: 'info',
            anomaly: 'warning'
        };
        return iconMap[type] || 'info';
    }

    getActivityIcon(type) {
        const icons = {
            success: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><polyline points="20 6 9 17 4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            warning: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" stroke="currentColor" stroke-width="2"/><line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2"/></svg>',
            info: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><line x1="12" y1="16" x2="12" y2="12" stroke="currentColor" stroke-width="2"/></svg>'
        };
        return icons[type] || icons.info;
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000); // seconds

        if (diff < 60) return `${diff} seconds ago`;
        if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
        return date.toLocaleDateString();
    }

    showNotification(notification) {
        // Create notification element
        const notif = document.createElement('div');
        notif.className = `notification notification-${notification.type}`;
        notif.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: var(--color-bg-card);
            backdrop-filter: blur(20px);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            box-shadow: var(--shadow-xl);
            max-width: 400px;
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
        `;

        notif.innerHTML = `
            <h4 style="margin-bottom: 0.5rem; font-weight: 600;">${notification.title}</h4>
            <p style="color: var(--color-text-secondary); font-size: 0.875rem;">${notification.message}</p>
        `;

        document.body.appendChild(notif);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notif.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => notif.remove(), 300);
        }, 5000);
    }

    incrementNotificationBadge() {
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            const current = parseInt(badge.textContent) || 0;
            badge.textContent = current + 1;
        }
    }

    animateNumber(element, start, end, duration = 1000) {
        const range = end - start;
        const increment = range / (duration / 16); // 60fps
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.round(current);
        }, 16);
    }

    setupEventListeners() {
        // Notification button
        const notifBtn = document.getElementById('notificationBtn');
        if (notifBtn) {
            notifBtn.addEventListener('click', () => {
                this.showNotificationPanel();
            });
        }

        // Settings button
        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                this.showSettingsPanel();
            });
        }

        // Add hover effects to cards
        this.addCardInteractions();
    }

    addCardInteractions() {
        const cards = document.querySelectorAll('.risk-card, .region-card, .insight-card, .metric-card');

        cards.forEach(card => {
            card.addEventListener('mouseenter', (e) => {
                card.style.transform = 'translateY(-4px)';
            });

            card.addEventListener('mouseleave', (e) => {
                card.style.transform = 'translateY(0)';
            });
        });
    }

    showNotificationPanel() {
        console.log('Show notifications panel');
        // Implementation for notification panel
    }

    showSettingsPanel() {
        console.log('Show settings panel');
        // Implementation for settings panel
    }

    startRealTimeUpdates() {
        // Simulate real-time updates for demo purposes
        setInterval(() => {
            this.simulateMetricUpdate();
        }, 3000);
    }

    simulateMetricUpdate() {
        // Simulate random metric fluctuations
        const regions = ['us-east-1', 'us-west-2', 'eu-west-1'];
        const randomRegion = regions[Math.floor(Math.random() * regions.length)];

        const mockData = {
            type: 'metrics',
            payload: {
                regions: [{
                    id: randomRegion,
                    uptime: 99.98 + Math.random() * 0.02,
                    latency: 40 + Math.random() * 20,
                    load: 50 + Math.random() * 30
                }]
            }
        };

        // Uncomment to see live updates
        // this.handleRealtimeUpdate(mockData);
    }

    animateOnLoad() {
        // Animate elements on page load
        const sections = document.querySelectorAll('.section');
        sections.forEach((section, index) => {
            section.style.opacity = '0';
            section.style.transform = 'translateY(20px)';

            setTimeout(() => {
                section.style.transition = 'all 0.6s ease-out';
                section.style.opacity = '1';
                section.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Animate progress bars
        setTimeout(() => {
            this.animateProgressBars();
        }, 500);
    }

    animateProgressBars() {
        const bars = document.querySelectorAll('.component-bar-fill, .progress-fill');
        bars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.width = width;
            }, 100);
        });
    }

    updateSystemStatus(status) {
        const statusElement = document.querySelector('.system-status');
        const statusText = document.querySelector('.status-text');
        const statusIndicator = document.querySelector('.status-indicator');

        if (!statusElement) return;

        const statusConfig = {
            operational: {
                text: 'All Systems Operational',
                class: 'status-operational',
                color: 'var(--color-success)'
            },
            degraded: {
                text: 'System Degraded',
                class: 'status-degraded',
                color: 'var(--color-warning)'
            },
            outage: {
                text: 'System Outage',
                class: 'status-outage',
                color: 'var(--color-error)'
            }
        };

        const config = statusConfig[status] || statusConfig.operational;

        if (statusText) statusText.textContent = config.text;
        if (statusIndicator) {
            statusIndicator.className = `status-indicator ${config.class}`;
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DisasterRecoveryDashboard();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
