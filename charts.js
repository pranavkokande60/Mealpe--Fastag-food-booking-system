/**
 * SMART CANTEEN – Dynamic Chart.js Analytics
 */

function initAdminRevenueChart(canvasId, labels, dataPoints) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Daily Revenue (₹)',
        data: dataPoints,
        borderColor: '#E23744',
        backgroundColor: 'rgba(226, 55, 68, 0.08)',
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointBackgroundColor: '#E23744',
        pointRadius: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { callback: v => `₹${v}` }
        }
      }
    }
  });
}

function initCategoryDoughnutChart(canvasId, labels, dataPoints) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: dataPoints,
        backgroundColor: [
          '#E23744', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}
