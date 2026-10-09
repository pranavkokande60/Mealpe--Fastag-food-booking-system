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

// Real-Time Smart Food Rescue Notification & Deals Poller
class FoodRescueNotifier {
  constructor() {
    this.seenOfferIds = new Set();
    this.isFirstRun = true;
    this.init();
  }

  init() {
    this.checkOffers();
    // Poll for new food rescue offers every 5 seconds
    setInterval(() => this.checkOffers(), 5000);
  }

  checkOffers() {
    fetch('/api/rescue/active-offers')
      .then(res => res.json())
      .then(data => {
        if (!data.success || !data.offers) return;

        const currentOffers = data.offers;
        
        if (this.isFirstRun) {
          // Initialize seen offers on page load so we don't spam alerts for existing ones
          currentOffers.forEach(o => this.seenOfferIds.add(o.id));
          this.isFirstRun = false;
          return;
        }

        currentOffers.forEach(offer => {
          if (!this.seenOfferIds.has(offer.id)) {
            this.seenOfferIds.add(offer.id);
            this.triggerRescueAlert(offer);
          }
        });
      })
      .catch(() => {});
  }

  triggerRescueAlert(offer) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const alertCard = document.createElement('div');
    alertCard.className = 'card border-danger shadow-lg rounded-4 p-3 mb-2 animate__animated animate__bounceIn';
    alertCard.style.cssText = 'min-width: 320px; max-width: 400px; border-left: 6px solid #dc3545 !important; background: #ffffff;';

    const origPrice = parseFloat(offer.original_price).toFixed(2);
    const rescuePrice = parseFloat(offer.rescue_price).toFixed(2);

    alertCard.innerHTML = `
      <div class="d-flex align-items-center justify-content-between mb-2">
        <span class="badge bg-danger text-white rounded-pill px-2 py-1 fw-bold">
          <i class="fa-solid fa-bolt me-1"></i> FOOD RESCUE ALERT!
        </span>
        <button type="button" class="btn-close btn-sm" aria-label="Close"></button>
      </div>
      <div class="fw-bold text-dark small mb-2">A fresh meal is available and may go to waste!</div>
      <div class="d-flex align-items-center gap-3 bg-light p-2 rounded-3 mb-2 border">
        <img src="${offer.image_url}" width="48" height="48" class="rounded-3" style="object-fit: cover;">
        <div class="flex-grow-1">
          <div class="fw-bold small text-dark">${offer.food_name}</div>
          <div class="small">
            <del class="text-muted">₹${origPrice}</del> 
            <b class="text-danger ms-1">₹${rescuePrice}</b>
            <span class="badge bg-danger-subtle text-danger ms-1" style="font-size: 0.68rem;">Save ${offer.discount_percent}%</span>
          </div>
          <div class="small text-muted">Quantity: <b>${offer.quantity_available}</b></div>
        </div>
      </div>
      <div class="small text-muted mb-2">
        <div><i class="fa-solid fa-location-dot text-danger me-1"></i> ${offer.collection_point}</div>
        <div><i class="fa-regular fa-clock text-warning me-1"></i> Deadline: <b>${offer.time_remaining_str || '45 mins left'}</b></div>
      </div>
      <div class="d-flex gap-2">
        <a href="/student/dashboard#food-rescue" class="btn btn-danger btn-sm rounded-pill flex-fill fw-bold">⚡ Buy Now</a>
        <a href="/student/dashboard#food-rescue" class="btn btn-outline-secondary btn-sm rounded-pill flex-fill">View Details</a>
      </div>
    `;

    alertCard.querySelector('.btn-close').addEventListener('click', () => {
      alertCard.classList.replace('animate__bounceIn', 'animate__fadeOutRight');
      setTimeout(() => alertCard.remove(), 400);
    });

    toastContainer.prepend(alertCard);

    // Auto-dismiss after 12 seconds
    setTimeout(() => {
      if (alertCard.isConnected) {
        alertCard.classList.replace('animate__bounceIn', 'animate__fadeOutRight');
        setTimeout(() => alertCard.remove(), 400);
      }
    }, 12000);
  }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  window.cartManager = new CartManager();
  window.cartManager.renderCartUI();
  window.rescueNotifier = new FoodRescueNotifier();

  // Notification Polling (every 10s)
  const pollNotifications = () => {
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
  };

  pollNotifications();
  setInterval(pollNotifications, 10000);
});
