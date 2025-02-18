// Configuration
const API_BASE = '';  // Empty for same host
const UPDATE_INTERVAL = 1000;  // 1 second
const CHART_UPDATE_INTERVAL = 60000;  // 1 minute
const MAX_FOOD_WEIGHT = 1000;  // 1kg max

// Chart configuration
let feedingChart = null;

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    setupEventListeners();
    startUpdates();
});

function setupEventListeners() {
    // Feed button
    document.getElementById('feed-button').addEventListener('click', async () => {
        try {
            const response = await fetch(`${API_BASE}/api/feed`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ amount: 50 })  // 50g default portion
            });
            const result = await response.json();
            
            if (!result.success) {
                alert('Feeding failed: ' + result.message);
            }
        } catch (error) {
            console.error('Error triggering feed:', error);
            alert('Error triggering feeding mechanism');
        }
    });
}

function startUpdates() {
    // Start regular updates
    updateStatus();
    updateActivityLog();
    updateChart();
    
    setInterval(updateStatus, UPDATE_INTERVAL);
    setInterval(updateActivityLog, UPDATE_INTERVAL * 5);  // Every 5 seconds
    setInterval(updateChart, CHART_UPDATE_INTERVAL);
}

async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const status = await response.json();
        
        // Update food weight
        const foodWeight = status.food_weight.toFixed(1);
        document.getElementById('food-weight').textContent = `${foodWeight} g`;
        const foodPercentage = (foodWeight / MAX_FOOD_WEIGHT * 100).toFixed(1);
        document.getElementById('food-progress').style.width = `${foodPercentage}%`;
        
        // Update water level
        const waterLevel = status.water_level.toFixed(1);
        document.getElementById('water-level').textContent = `${waterLevel} %`;
        document.getElementById('water-progress').style.width = `${waterLevel}%`;
        
        // Update hardware status
        document.getElementById('feed-button').disabled = !status.hardware_available;
        
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

async function updateActivityLog() {
    try {
        const response = await fetch(`${API_BASE}/api/feeding_logs?days=1`);
        const logs = await response.json();
        
        const tbody = document.getElementById('activity-log');
        tbody.innerHTML = '';  // Clear existing rows
        
        logs.slice(0, 10).forEach(log => {  // Show last 10 entries
            const row = document.createElement('tr');
            const time = new Date(log.timestamp).toLocaleTimeString();
            
            row.innerHTML = `
                <td>${time}</td>
                <td>${log.cat}</td>
                <td>${log.food_type}</td>
                <td>${log.amount.toFixed(1)}g</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error updating activity log:', error);
    }
}

function initializeChart() {
    const ctx = document.getElementById('feeding-chart').getContext('2d');
    feedingChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Food Consumed (g)',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amount (g)'
                    }
                }
            }
        }
    });
}

async function updateChart() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const stats = await response.json();
        
        // Update chart data
        feedingChart.data.labels = stats.map(s => s.cat);
        feedingChart.data.datasets[0].data = stats.map(s => s.total_amount);
        feedingChart.update();
    } catch (error) {
        console.error('Error updating chart:', error);
    }
}