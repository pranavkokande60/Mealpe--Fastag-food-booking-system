/**
 * SMART CANTEEN – Floating AI Assistant Chatbot
 */

class CanteenBotWidget {
  constructor() {
    this.modal = document.getElementById('chatbot-modal');
    this.triggerBtn = document.getElementById('chatbot-trigger-btn');
    this.closeBtn = document.getElementById('chatbot-close-btn');
    this.chatBody = document.getElementById('chat-body-messages');
    this.chatInput = document.getElementById('chat-input-field');
    this.sendBtn = document.getElementById('chat-send-btn');

    if (this.triggerBtn && this.modal) {
      this.initEvents();
    }
  }

  initEvents() {
    this.triggerBtn.addEventListener('click', () => this.toggleModal());
    this.closeBtn.addEventListener('click', () => this.toggleModal());

    this.sendBtn.addEventListener('click', () => this.handleSend());
    this.chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.handleSend();
    });

    // Delegate quick replies click
    this.chatBody.addEventListener('click', (e) => {
      const chip = e.target.closest('.chat-quick-chip');
      if (chip) {
        const query = chip.dataset.query;
        this.chatInput.value = query;
        this.handleSend();
      }
    });
  }

  toggleModal() {
    this.modal.classList.toggle('hidden');
    if (!this.modal.classList.contains('hidden')) {
      this.chatInput.focus();
    }
  }

  appendMessage(text, sender = 'bot', actionLink = null, actionText = null, quickReplies = []) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${sender}`;

    // Format simple markdown (bold **text**, bullet points)
    let formattedText = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/_(.*?)_/g, '<em>$1</em>')
      .replace(/\n/g, '<br/>');

    msgDiv.innerHTML = formattedText;

    if (actionLink && actionText) {
      const btn = document.createElement('a');
      btn.href = actionLink;
      btn.className = 'btn btn-sm btn-brand mt-2 d-inline-block text-white text-decoration-none';
      btn.innerHTML = `<i class="fa-solid fa-arrow-right me-1"></i> ${actionText}`;
      msgDiv.appendChild(document.createElement('br'));
      msgDiv.appendChild(btn);
    }

    this.chatBody.appendChild(msgDiv);

    // Quick replies chips
    if (quickReplies && quickReplies.length > 0) {
      const chipsContainer = document.createElement('div');
      chipsContainer.className = 'd-flex flex-wrap gap-1 mt-1 mb-2';
      quickReplies.forEach(qr => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'btn btn-outline-secondary btn-sm rounded-pill chat-quick-chip py-0 px-2 small';
        chip.style.fontSize = '0.75rem';
        chip.dataset.query = qr;
        chip.textContent = qr;
        chipsContainer.appendChild(chip);
      });
      this.chatBody.appendChild(chipsContainer);
    }

    this.chatBody.scrollTop = this.chatBody.scrollHeight;
  }

  handleSend() {
    const text = this.chatInput.value.trim();
    if (!text) return;

    this.appendMessage(text, 'user');
    this.chatInput.value = '';

    // Show typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'chat-msg bot text-muted small typing-ind';
    typingIndicator.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin me-1"></i> AI is thinking...';
    this.chatBody.appendChild(typingIndicator);
    this.chatBody.scrollTop = this.chatBody.scrollHeight;

    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    })
    .then(r => r.json())
    .then(data => {
      typingIndicator.remove();
      this.appendMessage(data.reply, 'bot', data.action_link, data.action_text, data.quick_replies);
    })
    .catch(() => {
      typingIndicator.remove();
      this.appendMessage("Sorry, I encountered a hiccup. Please ask again!", 'bot');
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new CanteenBotWidget();
});
