/**
 * SMART CANTEEN – 2D Seat Booking Map Handler
 */

document.addEventListener('DOMContentLoaded', () => {
  const tableCards = document.querySelectorAll('.table-card.available');
  const selectedTableInput = document.getElementById('selected-table-id');
  const selectedTableDisplay = document.getElementById('selected-table-label');
  const confirmBookBtn = document.getElementById('confirm-booking-btn');

  tableCards.forEach(card => {
    card.addEventListener('click', () => {
      // Remove selected from all
      document.querySelectorAll('.table-card').forEach(c => {
        if (c.classList.contains('selected')) {
          c.classList.remove('selected');
          c.classList.add('available');
        }
      });

      // Add to clicked
      card.classList.remove('available');
      card.classList.add('selected');

      const tid = card.dataset.tableId;
      const tnum = card.dataset.tableNumber;
      const tcap = card.dataset.tableCapacity;

      if (selectedTableInput) selectedTableInput.value = tid;
      if (selectedTableDisplay) selectedTableDisplay.textContent = `Table ${tnum} (${tcap} Seats)`;
      if (confirmBookBtn) confirmBookBtn.disabled = false;
    });
  });
});
