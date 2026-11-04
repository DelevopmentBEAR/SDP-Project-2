const chatLog = document.getElementById('chat-log');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const promptButtons = document.querySelectorAll('.prompt-button');

function addMessage(role, text) {
    const messageRow = document.createElement('div');
    messageRow.className = `message ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    messageRow.appendChild(bubble);
    chatLog.appendChild(messageRow);
    chatLog.scrollTop = chatLog.scrollHeight;
}

function getHistory() {
    const rows = [...chatLog.querySelectorAll('.message')];
    return rows.map((row) => {
        const role = row.classList.contains('user') ? 'user' : 'assistant';
        const text = row.querySelector('.bubble').textContent.trim();
        return { role, content: text };
    });
}

async function sendMessage(message) {
    addMessage('user', message);
    messageInput.value = '';
    sendBtn.disabled = true;
    sendBtn.textContent = 'Thinking...';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message,
                history: getHistory().slice(-10)
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Something went wrong.');
        }

        addMessage('assistant', data.reply);
    } catch (error) {
        addMessage('assistant', `I hit a problem while helping with that: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
    }
}

chatForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;
    sendMessage(message);
});

promptButtons.forEach((button) => {
    button.addEventListener('click', () => {
        messageInput.value = button.textContent.trim();
        messageInput.focus();
    });
});
