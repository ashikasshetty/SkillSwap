// In-App Chat Real-time Poller & AJAX Handler

document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.getElementById('chat-messages');
  const swapId = document.getElementById('chat-swap-id')?.value;

  if (!chatMessages || !swapId) return;

  // Auto-scroll to latest message
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  scrollToBottom();

  // Send message via AJAX
  if (chatForm && chatInput) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const content = chatInput.value.trim();
      if (!content) return;

      chatInput.value = '';

      try {
        const response = await fetch(`/chat/${swapId}/send`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify({ content })
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.message) {
            appendMessage(data.message.content, data.message.timestamp, true);
            scrollToBottom();
          }
        }
      } catch (err) {
        console.error('Failed to send message:', err);
      }
    });
  }

  // Append new bubble helper
  function appendMessage(content, time, isMine) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${isMine ? 'bubble-mine' : 'bubble-theirs'}`;
    bubble.innerHTML = `
      <div>${escapeHtml(content)}</div>
      <div class="bubble-time">${time}</div>
    `;
    chatMessages.appendChild(bubble);
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
  }

  // Poll for new messages every 3.5 seconds
  let lastCount = chatMessages.children.length;
  setInterval(async () => {
    try {
      const res = await fetch(`/chat/${swapId}/api/messages`);
      if (res.ok) {
        const data = await res.json();
        if (data.messages && data.messages.length > lastCount) {
          chatMessages.innerHTML = '';
          data.messages.forEach(m => {
            appendMessage(m.content, m.timestamp, m.is_me);
          });
          lastCount = data.messages.length;
          scrollToBottom();
        }
      }
    } catch (e) {
      // Quiet fail on network flutter
    }
  }, 3500);
});
