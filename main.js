/**
 * SMART CANTEEN – Core Client Script
 * LocalStorage Cart Management, Dynamic UI Updates, Toast Alerts, and Notification Center
 */

class CartManager {
  constructor() {
    this.storageKey = 'smart_canteen_cart';
    this.cart = this.loadCart();
    this.initEventListeners();
    this.updateCartBadge();
  }

  loadCart() {
    try {
      return JSON.parse(localStorage.getItem(this.storageKey)) || [];
    } catch (e) {
      return [];
    }
  }

  saveCart() {
    localStorage.setItem(this.storageKey, JSON.stringify(this.cart));
    this.updateCartBadge();
    this.renderCartUI();
  }

  addItem(item) {
    const existing = this.cart.find(i => i.id === item.id);
    if (existing) {
      existing.quantity += 1;
    } else {
      this.cart.push({
        id: item.id,
        name: item.name,
        price: parseFloat(item.price),
        image_url: item.image_url,
        is_veg: item.is_veg,
        quantity: 1
      });
    }
    this.saveCart();
    this.showToast(`Added ${item.name} to cart!`, 'success');
  }

  updateQuantity(id, delta) {
    const item = this.cart.find(i => i.id === id);
    if (!item) return;

    item.quantity += delta;
    if (item.quantity <= 0) {
      this.cart = this.cart.filter(i => i.id !== id);
    }
    this.saveCart();
  }

  clearCart() {
    this.cart = [];
    this.saveCart();
  }

  getSubtotal() {
    return this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  }

  getTotalCount() {
    return this.cart.reduce((sum, item) => sum + item.quantity, 0);
  }

  updateCartBadge() {
    const badge = document.getElementById('nav-cart-badge');
    if (badge) {
      const count = this.getTotalCount();
      badge.textContent = count;
      badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }
  }

  showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `alert alert-${type} shadow-lg rounded-3 mb-2 animate__animated animate__fadeInRight`;
    toast.style.minWidth = '250px';
    toast.innerHTML = `<i class="fa-solid fa-bell me-2"></i> ${message}`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.classList.replace('animate__fadeInRight', 'animate__fadeOutRight');
      setTimeout(() => toast.remove(), 400);
    }, 3000);
  }

  renderCartUI() {
    // Render Cart Page if on /student/cart
    const cartContainer = document.getElementById('cart-items-container');
    if (cartContainer) {
      if (this.cart.length === 0) {
        cartContainer.innerHTML = `
          <div class="text-center py-5">
            <i class="fa-solid fa-bowl-rice fa-3x text-muted mb-3"></i>
            <h5 class="fw-bold">Your cart is empty</h5>
            <p class="text-muted">Explore our tasty campus menu and add something delicious!</p>
            <a href="/student/menu" class="btn btn-brand mt-2">Explore Menu</a>
          </div>
        `;
        document.getElementById('cart-summary-section')?.classList.add('d-none');
        return;
      }

      document.getElementById('cart-summary-section')?.classList.remove('d-none');
      let html = '';
      this.cart.forEach(item => {
        html += `
          <div class="d-flex align-items-center justify-content-between p-3 bg-white rounded-3 border mb-2">
            <div class="d-flex align-items-center gap-3">
              <span class="${item.is_veg ? 'indicator-veg' : 'indicator-nonveg'}"></span>
              <img src="${item.image_url}" class="rounded-3" width="60" height="60" style="object-fit: cover;">
              <div>
                <h6 class="fw-bold mb-1">${item.name}</h6>
                <div class="text-muted small">₹${item.price.toFixed(2)} each</div>
              </div>
            </div>
            <div class="d-flex align-items-center gap-3">
              <div class="qty-control">
                <button type="button" class="qty-btn" onclick="window.cartManager.updateQuantity(${item.id}, -1)">-</button>
                <span class="qty-count">${item.quantity}</span>
                <button type="button" class="qty-btn" onclick="window.cartManager.updateQuantity(${item.id}, 1)">+</button>
              </div>
              <div class="fw-bold text-dark" style="min-width: 70px; text-align: right;">
                ₹${(item.price * item.quantity).toFixed(2)}
              </div>
            </div>
          </div>
        `;
      });
      cartContainer.innerHTML = html;

      // Update Summary Numbers
      const subtotal = this.getSubtotal();
      const tax = subtotal * 0.05;
      const discount = window.appliedDiscount || 0;
      const total = Math.max(0, subtotal - discount + tax);

      document.getElementById('cart-subtotal')?.replaceChildren(document.createTextNode(`₹${subtotal.toFixed(2)}`));
      document.getElementById('cart-tax')?.replaceChildren(document.createTextNode(`₹${tax.toFixed(2)}`));
      document.getElementById('cart-total')?.replaceChildren(document.createTextNode(`₹${total.toFixed(2)}`));

      // Fetch dynamic prep time
      fetch('/api/cart/prep-time', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_ids: this.cart.map(i => i.id) })
      })
      .then(res => res.json())
      .then(data => {
        const prepEl = document.getElementById('cart-estimated-prep');
        if (prepEl) {
          prepEl.innerHTML = `⚡ Estimated Prep Time: <b>${data.prep_minutes} mins</b> (Pickup at <b>${data.pickup_time_str}</b>)`;
        }
      });
    }

    // Pass cart data to checkout hidden input if present
    const checkoutCartInput = document.getElementById('checkout-cart-data');
    if (checkoutCartInput) {
      checkoutCartInput.value = JSON.stringify(this.cart);
    }
  }

  initEventListeners() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-add-to-cart');
      if (btn) {
        const item = {
          id: parseInt(btn.dataset.id),
          name: btn.dataset.name,
          price: parseFloat(btn.dataset.price),
          image_url: btn.dataset.image,
          is_veg: parseInt(btn.dataset.veg)
        };
        this.addItem(item);
      }
    });
  }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  window.cartManager = new CartManager();
  window.cartManager.renderCartUI();

  // Notification Polling (every 30s)
  setInterval(() => {
    fetch('/api/notifications/unread-count')
      .then(r => r.json())
      .then(data => {
        const badge = document.getElementById('nav-notif-badge');
        if (badge) {
          badge.textContent = data.count;
          badge.style.display = data.count > 0 ? 'inline-flex' : 'none';
        }
      })
      .catch(() => {});
  }, 30000);
});
