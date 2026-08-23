/**
 * SMART CANTEEN – Live Kitchen Display System (KDS) Auto-polling
 */

function pollKitchenOrders() {
  fetch('/api/kitchen/live-orders')
    .then(r => r.json())
    .then(data => {
      // If needed, refresh scoreboard numbers dynamically
      const countEl = document.getElementById('kds-live-count');
      if (countEl && data.orders) {
        countEl.textContent = data.orders.length;
      }
    })
    .catch(() => {});
}

document.addEventListener('DOMContentLoaded', () => {
  // Poll every 8 seconds
  setInterval(pollKitchenOrders, 8000);
});
