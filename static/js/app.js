// JavaScript for Provision-it application

// API base URL
const API_BASE = 'http://127.0.0.1:5001/api/v1';

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Login functionality
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const resultDiv = document.getElementById('loginResult');
            
            try {
                const response = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            Login successful! Welcome, ${data.data.username}
                        </div>
                    `;
                    // Store user info in localStorage
                    localStorage.setItem('user', JSON.stringify(data.data));
                    // Redirect to assets page after 2 seconds
                    setTimeout(() => {
                        window.location.href = '/assets';
                    }, 2000);
                } else {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            ${data.error}
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        Login failed: ${error.message}
                    </div>
                `;
            }
        });
    }
    
    // Asset history functionality
    loadAssets();
});

// Load assets for dropdown
async function loadAssets() {
    try {
        const response = await fetch(`${API_BASE}/assets/`);
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById('assetSelect');
            if (select) {
                select.innerHTML = '<option value="">Select an asset...</option>';
                data.data.assets.forEach(asset => {
                    const option = document.createElement('option');
                    option.value = asset.asset_id;
                    option.textContent = `${asset.name} (ID: ${asset.asset_id})`;
                    select.appendChild(option);
                });
                
                select.addEventListener('change', function() {
                    if (this.value) {
                        loadAssetHistory(this.value);
                    }
                });
            }
        }
    } catch (error) {
        console.error('Failed to load assets:', error);
    }
}

// Load asset history
async function loadAssetHistory(assetId) {
    try {
        // Show loading state
        document.getElementById('historyChart').innerHTML = '<div class="loading">Loading history...</div>';
        document.getElementById('assetInfo').innerHTML = '<div class="loading">Loading asset info...</div>';
        
        // Load asset info and history in parallel
        const [assetResponse, historyResponse] = await Promise.all([
            fetch(`${API_BASE}/assets/${assetId}`),
            fetch(`${API_BASE}/assets/${assetId}/history?per_page=100`)
        ]);
        
        const assetData = await assetResponse.json();
        const historyData = await historyResponse.json();
        
        if (assetResponse.ok && historyResponse.ok) {
            displayAssetInfo(assetData.data);
            displayAssetHistory(historyData.data.history);
        } else {
            throw new Error('Failed to load asset data');
        }
    } catch (error) {
        console.error('Failed to load asset history:', error);
        document.getElementById('historyChart').innerHTML = `
            <div class="error">Failed to load asset history: ${error.message}</div>
        `;
    }
}

// Display asset information
function displayAssetInfo(asset) {
    const assetInfoDiv = document.getElementById('assetInfo');
    assetInfoDiv.innerHTML = `
        <h6>${asset.name}</h6>
        <p class="text-muted">${asset.description}</p>
        <hr>
        <div class="row">
            <div class="col-6">
                <small class="text-muted">Current Value</small>
                <div class="h5 text-primary">${formatCurrency(asset.current_value)}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Fraction Value</small>
                <div class="h6">${formatCurrency(asset.fraction_value)}</div>
            </div>
        </div>
        <div class="row mt-2">
            <div class="col-6">
                <small class="text-muted">Total Fractions</small>
                <div>${asset.available_fractions.toLocaleString()}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Status</small>
                <div><span class="badge bg-${asset.status === 'approved' ? 'success' : 'warning'}">${asset.status}</span></div>
            </div>
        </div>
    `;
}

// Display asset history
function displayAssetHistory(history) {
    if (!history || history.length === 0) {
        document.getElementById('historyChart').innerHTML = '<div class="text-muted">No history data available</div>';
        return;
    }
    
    // Sort by date (oldest first for chart)
    const sortedHistory = history.sort((a, b) => new Date(a.update_time) - new Date(b.update_time));
    
    // Create simple chart using HTML/CSS
    const chartDiv = document.getElementById('historyChart');
    const maxValue = Math.max(...sortedHistory.map(h => h.asset_value));
    const minValue = Math.min(...sortedHistory.map(h => h.asset_value));
    const range = maxValue - minValue;
    
    let chartHTML = '<div class="chart-container">';
    chartHTML += '<div class="d-flex align-items-end" style="height: 300px; border-bottom: 1px solid #dee2e6; border-left: 1px solid #dee2e6;">';
    
    sortedHistory.forEach((point, index) => {
        const height = range > 0 ? ((point.asset_value - minValue) / range) * 280 : 140;
        const width = 100 / sortedHistory.length;
        chartHTML += `
            <div class="d-flex flex-column align-items-center" style="width: ${width}%; height: 100%;">
                <div class="bg-primary" style="width: 4px; height: ${height}px; margin-bottom: 5px;" 
                     title="${formatDate(point.update_time)}: ${formatCurrency(point.asset_value)}"></div>
            </div>
        `;
    });
    
    chartHTML += '</div>';
    chartHTML += '<div class="d-flex justify-content-between mt-2 text-muted small">';
    chartHTML += `<span>${formatDate(sortedHistory[0].update_time)}</span>`;
    chartHTML += `<span>${formatDate(sortedHistory[sortedHistory.length - 1].update_time)}</span>`;
    chartHTML += '</div>';
    chartHTML += '</div>';
    
    chartDiv.innerHTML = chartHTML;
    
    // Update history table
    updateHistoryTable(sortedHistory.reverse()); // Show newest first in table
}

// Update history table
function updateHistoryTable(history) {
    const tbody = document.querySelector('#historyTable tbody');
    tbody.innerHTML = '';
    
    history.forEach((point, index) => {
        const row = document.createElement('tr');
        
        // Calculate change from previous point
        let change = '';
        let changeClass = '';
        if (index < history.length - 1) {
            const prevValue = history[index + 1].asset_value;
            const currentValue = point.asset_value;
            const diff = currentValue - prevValue;
            const percentChange = (diff / prevValue) * 100;
            
            if (diff > 0) {
                change = `+${formatCurrency(diff)} (+${percentChange.toFixed(2)}%)`;
                changeClass = 'value-positive';
            } else if (diff < 0) {
                change = `${formatCurrency(diff)} (${percentChange.toFixed(2)}%)`;
                changeClass = 'value-negative';
            } else {
                change = 'No change';
            }
        } else {
            change = 'N/A';
        }
        
        row.innerHTML = `
            <td>${formatDate(point.update_time)}</td>
            <td>${formatCurrency(point.asset_value)}</td>
            <td class="${changeClass}">${change}</td>
        `;
        tbody.appendChild(row);
    });
}