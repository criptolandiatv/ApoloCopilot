/**
 * ApoloCopilot AI Chatbox Widget
 * Discrete chatbox powered by OpenEvidence.com
 */

class ApoloCopilotChat {
    constructor(options = {}) {
        this.isOpen = false;
        this.messages = [];
        this.apiEndpoint = options.apiEndpoint || '/api/chat/send';
        this.position = options.position || 'bottom-right';
        this.primaryColor = options.primaryColor || '#FF4500';
        this.init();
    }

    init() {
        this.injectStyles();
        this.createChatbox();
        this.attachEventListeners();
        this.loadChatHistory();
    }

    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .apolo-chat-widget {
                position: fixed;
                ${this.position === 'bottom-right' ? 'bottom: 20px; right: 20px;' : 'bottom: 20px; left: 20px;'}
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }

            .apolo-chat-button {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, ${this.primaryColor}, #FF6B35);
                border: none;
                box-shadow: 0 4px 20px rgba(255, 69, 0, 0.3);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }

            .apolo-chat-button:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 30px rgba(255, 69, 0, 0.4);
            }

            .apolo-chat-button::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                transform: translate(-50%, -50%) scale(0);
                transition: transform 0.6s ease;
            }

            .apolo-chat-button:active::before {
                transform: translate(-50%, -50%) scale(2);
                opacity: 0;
            }

            .apolo-chat-icon {
                font-size: 28px;
                color: white;
                transition: transform 0.3s ease;
            }

            .apolo-chat-button.open .apolo-chat-icon {
                transform: rotate(180deg);
            }

            .apolo-chat-badge {
                position: absolute;
                top: -5px;
                right: -5px;
                background: #46D160;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            }

            .apolo-chat-container {
                position: absolute;
                bottom: 80px;
                ${this.position === 'bottom-right' ? 'right: 0;' : 'left: 0;'}
                width: 380px;
                max-width: calc(100vw - 40px);
                height: 600px;
                max-height: calc(100vh - 120px);
                background: #1A1F2E;
                border-radius: 20px;
                box-shadow: 0 10px 50px rgba(0, 0, 0, 0.5);
                display: none;
                flex-direction: column;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.1);
                animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px) scale(0.95);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            .apolo-chat-container.open {
                display: flex;
            }

            .apolo-chat-header {
                background: linear-gradient(135deg, ${this.primaryColor}, #FF6B35);
                padding: 20px;
                color: white;
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .apolo-chat-avatar {
                width: 40px;
                height: 40px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
            }

            .apolo-chat-title {
                flex: 1;
            }

            .apolo-chat-title h3 {
                margin: 0;
                font-size: 16px;
                font-weight: 600;
            }

            .apolo-chat-title p {
                margin: 4px 0 0 0;
                font-size: 12px;
                opacity: 0.9;
            }

            .apolo-chat-status {
                width: 8px;
                height: 8px;
                background: #46D160;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            .apolo-chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #0B0F19;
            }

            .apolo-chat-messages::-webkit-scrollbar {
                width: 6px;
            }

            .apolo-chat-messages::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.05);
            }

            .apolo-chat-messages::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }

            .apolo-message {
                margin-bottom: 16px;
                animation: fadeIn 0.3s ease;
            }

            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .apolo-message-content {
                padding: 12px 16px;
                border-radius: 16px;
                max-width: 85%;
                word-wrap: break-word;
                line-height: 1.5;
            }

            .apolo-message.user .apolo-message-content {
                background: linear-gradient(135deg, ${this.primaryColor}, #FF6B35);
                color: white;
                margin-left: auto;
                border-bottom-right-radius: 4px;
            }

            .apolo-message.assistant .apolo-message-content {
                background: #1A1F2E;
                color: #B8C5D0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-bottom-left-radius: 4px;
            }

            .apolo-message-time {
                font-size: 11px;
                color: #6E7681;
                margin-top: 4px;
                display: block;
            }

            .apolo-message.user .apolo-message-time {
                text-align: right;
            }

            .apolo-typing {
                display: flex;
                gap: 4px;
                padding: 12px;
            }

            .apolo-typing span {
                width: 8px;
                height: 8px;
                background: ${this.primaryColor};
                border-radius: 50%;
                animation: typing 1.4s infinite;
            }

            .apolo-typing span:nth-child(2) {
                animation-delay: 0.2s;
            }

            .apolo-typing span:nth-child(3) {
                animation-delay: 0.4s;
            }

            @keyframes typing {
                0%, 60%, 100% {
                    transform: translateY(0);
                    opacity: 0.7;
                }
                30% {
                    transform: translateY(-10px);
                    opacity: 1;
                }
            }

            .apolo-chat-input-container {
                padding: 16px;
                background: #1A1F2E;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }

            .apolo-chat-input-wrapper {
                display: flex;
                gap: 8px;
                background: #0B0F19;
                border-radius: 12px;
                padding: 4px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: border-color 0.3s ease;
            }

            .apolo-chat-input-wrapper:focus-within {
                border-color: ${this.primaryColor};
            }

            .apolo-chat-input {
                flex: 1;
                background: transparent;
                border: none;
                color: white;
                padding: 12px;
                font-size: 14px;
                outline: none;
                font-family: inherit;
            }

            .apolo-chat-input::placeholder {
                color: #6E7681;
            }

            .apolo-chat-send {
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, ${this.primaryColor}, #FF6B35);
                border: none;
                border-radius: 10px;
                color: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }

            .apolo-chat-send:hover:not(:disabled) {
                transform: scale(1.05);
                box-shadow: 0 4px 15px rgba(255, 69, 0, 0.3);
            }

            .apolo-chat-send:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            .apolo-powered-by {
                text-align: center;
                padding: 8px;
                font-size: 11px;
                color: #6E7681;
                background: #0B0F19;
            }

            .apolo-powered-by a {
                color: ${this.primaryColor};
                text-decoration: none;
                font-weight: 600;
            }

            .apolo-powered-by a:hover {
                text-decoration: underline;
            }

            .apolo-welcome-message {
                background: #1A1F2E;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 16px;
            }

            .apolo-welcome-message h4 {
                margin: 0 0 8px 0;
                color: white;
                font-size: 14px;
            }

            .apolo-welcome-message p {
                margin: 0;
                color: #B8C5D0;
                font-size: 13px;
                line-height: 1.5;
            }

            @media (max-width: 480px) {
                .apolo-chat-container {
                    width: calc(100vw - 20px);
                    height: calc(100vh - 100px);
                    bottom: 10px;
                    left: 10px;
                    right: 10px;
                }
            }
        `;
        document.head.appendChild(style);
    }

    createChatbox() {
        const widget = document.createElement('div');
        widget.className = 'apolo-chat-widget';
        widget.innerHTML = `
            <button class="apolo-chat-button" id="apoloChatToggle">
                <span class="apolo-chat-icon">🤖</span>
                <span class="apolo-chat-badge" id="apoloChatBadge" style="display: none;">1</span>
            </button>

            <div class="apolo-chat-container" id="apoloChatContainer">
                <div class="apolo-chat-header">
                    <div class="apolo-chat-avatar">🧠</div>
                    <div class="apolo-chat-title">
                        <h3>Copiloto IA</h3>
                        <p>Respostas baseadas em evidências</p>
                    </div>
                    <div class="apolo-chat-status"></div>
                </div>

                <div class="apolo-chat-messages" id="apoloChatMessages">
                    <div class="apolo-welcome-message">
                        <h4>👋 Olá! Sou seu Copiloto IA</h4>
                        <p>Posso ajudá-lo com informações baseadas em evidências científicas do OpenEvidence.com</p>
                    </div>
                </div>

                <div class="apolo-chat-input-container">
                    <div class="apolo-chat-input-wrapper">
                        <input
                            type="text"
                            class="apolo-chat-input"
                            id="apoloChatInput"
                            placeholder="Digite sua pergunta..."
                            autocomplete="off"
                        />
                        <button class="apolo-chat-send" id="apoloChatSend">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                            </svg>
                        </button>
                    </div>
                </div>

                <div class="apolo-powered-by">
                    Powered by <a href="https://openevidence.com" target="_blank">OpenEvidence</a>
                </div>
            </div>
        `;

        document.body.appendChild(widget);
    }

    attachEventListeners() {
        const toggleBtn = document.getElementById('apoloChatToggle');
        const sendBtn = document.getElementById('apoloChatSend');
        const input = document.getElementById('apoloChatInput');

        toggleBtn.addEventListener('click', () => this.toggleChat());
        sendBtn.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const container = document.getElementById('apoloChatContainer');
        const button = document.getElementById('apoloChatToggle');
        const badge = document.getElementById('apoloChatBadge');

        if (this.isOpen) {
            container.classList.add('open');
            button.classList.add('open');
            badge.style.display = 'none';
            this.scrollToBottom();
        } else {
            container.classList.remove('open');
            button.classList.remove('open');
        }
    }

    async loadChatHistory() {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) return;

            const response = await fetch('/api/chat/history?limit=10', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const history = await response.json();
                history.reverse().forEach(msg => {
                    this.addMessage(msg.message, 'user', false);
                    if (msg.response) {
                        this.addMessage(msg.response, 'assistant', false);
                    }
                });
            }
        } catch (error) {
            console.log('Could not load chat history:', error);
        }
    }

    async sendMessage() {
        const input = document.getElementById('apoloChatInput');
        const message = input.value.trim();

        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        input.value = '';

        // Show typing indicator
        this.showTyping();

        try {
            const token = localStorage.getItem('access_token');
            const headers = {
                'Content-Type': 'application/json'
            };

            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ message: message })
            });

            this.hideTyping();

            if (response.ok) {
                const data = await response.json();
                this.addMessage(data.response || data.message, 'assistant');
            } else {
                this.addMessage(
                    'Desculpe, não consegui processar sua pergunta. Por favor, faça login para usar o chat.',
                    'assistant'
                );
            }
        } catch (error) {
            this.hideTyping();
            this.addMessage(
                'Erro ao conectar com o servidor. Tente novamente mais tarde.',
                'assistant'
            );
        }
    }

    addMessage(text, sender, scroll = true) {
        const messagesContainer = document.getElementById('apoloChatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `apolo-message ${sender}`;

        const time = new Date().toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.innerHTML = `
            <div class="apolo-message-content">
                ${this.formatMessage(text)}
                <span class="apolo-message-time">${time}</span>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);

        if (scroll) {
            this.scrollToBottom();
        }

        // Show badge if chat is closed
        if (!this.isOpen && sender === 'assistant') {
            const badge = document.getElementById('apoloChatBadge');
            badge.style.display = 'block';
        }
    }

    formatMessage(text) {
        // Convert markdown-style bold to HTML
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Convert line breaks
        text = text.replace(/\n/g, '<br>');
        return text;
    }

    showTyping() {
        const messagesContainer = document.getElementById('apoloChatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'apolo-message assistant';
        typingDiv.id = 'apoloTyping';
        typingDiv.innerHTML = `
            <div class="apolo-message-content">
                <div class="apolo-typing">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTyping() {
        const typingDiv = document.getElementById('apoloTyping');
        if (typingDiv) {
            typingDiv.remove();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('apoloChatMessages');
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 100);
    }
}

// Auto-initialize
if (typeof window !== 'undefined') {
    window.ApoloCopilotChat = ApoloCopilotChat;

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.apoloChat = new ApoloCopilotChat();
        });
    } else {
        window.apoloChat = new ApoloCopilotChat();
    }
}
