// Controlador de Interfaz de Caramell Assistant (IA)

document.addEventListener('DOMContentLoaded', () => {
    const openBtn = document.getElementById('open-chatbot-btn');
    const closeBtn = document.getElementById('close-chatbot-btn');
    const chatWindow = document.getElementById('chatbot-window');
    const chatForm = document.getElementById('chatbot-form');
    const chatInput = document.getElementById('chatbot-input');
    const chatMessages = document.getElementById('chatbot-messages');

    if (!openBtn || !closeBtn || !chatWindow) return;

    // Abrir ventana
    openBtn.addEventListener('click', () => {
        chatWindow.classList.remove('hidden');
        requestAnimationFrame(() => {
            chatWindow.classList.remove('scale-95', 'opacity-0');
            chatWindow.classList.add('scale-100', 'opacity-100');
        });
        openBtn.classList.add('hidden');
        if (chatInput) chatInput.focus();
        scrollToBottom();
    });

    // Cerrar ventana
    closeBtn.addEventListener('click', () => {
        chatWindow.classList.remove('scale-100', 'opacity-100');
        chatWindow.classList.add('scale-95', 'opacity-0');
        setTimeout(() => {
            chatWindow.classList.add('hidden');
            openBtn.classList.remove('hidden');
        }, 300);
    });

    // Envío del mensaje
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const texto = chatInput.value.trim();
        if (!texto) return;

        chatInput.value = '';
        appendUserMessage(texto);
        await enviarMensajeBackend(texto);
    });
});

function scrollToBottom() {
    const chatMessages = document.getElementById('chatbot-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function appendUserMessage(texto) {
    const chatMessages = document.getElementById('chatbot-messages');
    if (!chatMessages) return;

    const div = document.createElement('div');
    div.className = 'flex items-start justify-end gap-2.5';
    div.innerHTML = `
        <div class="bg-gradient-to-r from-pink-600 to-rose-500 text-white p-3.5 rounded-2xl rounded-tr-none shadow-sm max-w-[85%] leading-relaxed">
            ${escapeHTML(texto)}
        </div>
        <div class="w-7 h-7 rounded-xl bg-pink-200 text-pink-800 flex items-center justify-center shrink-0 font-bold text-xs">
            Tú
        </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();
}

function appendBotMessage(texto, esDerivacion = false) {
    const chatMessages = document.getElementById('chatbot-messages');
    if (!chatMessages) return;

    const div = document.createElement('div');
    div.className = 'flex items-start gap-2.5';

    const formattedContent = formatMarkdown(texto);
    const alertBorder = esDerivacion ? 'border-amber-400 bg-amber-50/50' : 'border-pink-100 bg-white';

    div.innerHTML = `
        <div class="w-7 h-7 rounded-xl bg-pink-100 text-pink-700 flex items-center justify-center shrink-0 text-sm shadow-sm">
            🍬
        </div>
        <div class="${alertBorder} p-3.5 rounded-2xl rounded-tl-none border shadow-sm max-w-[85%] text-gray-800 leading-relaxed">
            ${formattedContent}
        </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatbot-messages');
    if (!chatMessages) return null;

    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'flex items-start gap-2.5';
    indicator.innerHTML = `
        <div class="w-7 h-7 rounded-xl bg-pink-100 text-pink-700 flex items-center justify-center shrink-0 text-sm">
            🍬
        </div>
        <div class="bg-white px-4 py-3 rounded-2xl rounded-tl-none border border-pink-100 shadow-sm flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-pink-400 animate-bounce"></span>
            <span class="w-2 h-2 rounded-full bg-pink-500 animate-bounce [animation-delay:0.2s]"></span>
            <span class="w-2 h-2 rounded-full bg-pink-600 animate-bounce [animation-delay:0.4s]"></span>
        </div>
    `;
    chatMessages.appendChild(indicator);
    scrollToBottom();
    return indicator;
}

async function enviarMensajeBackend(texto) {
    const indicator = showTypingIndicator();

    try {
        const response = await fetch('/api/chatbot/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensaje: texto })
        });

        const data = await response.json();
        if (indicator) indicator.remove();

        if (data.success) {
            appendBotMessage(data.respuesta, data.derivacion_humana);
        } else {
            appendBotMessage("🍬 Disculpa, ocurrió un breve retraso en mi conexión con el catálogo. ¿Podrías intentar nuevamente?");
        }
    } catch (err) {
        if (indicator) indicator.remove();
        appendBotMessage("🍬 No pude comunicarme con el servidor central en este momento. Por favor verifica tu conexión o recarga la página.");
    }
}

function enviarSugerencia(texto) {
    const chatInput = document.getElementById('chatbot-input');
    const openBtn = document.getElementById('open-chatbot-btn');
    const chatWindow = document.getElementById('chatbot-window');

    if (chatWindow && chatWindow.classList.contains('hidden')) {
        openBtn.click();
    }

    if (chatInput) {
        chatInput.value = texto;
        document.getElementById('chatbot-form').dispatchEvent(new Event('submit'));
    }
}

function escapeHTML(str) {
    return str.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
}

function formatMarkdown(text) {
    let html = escapeHTML(text);

    // Negrita **texto**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Cursiva _texto_
    html = html.replace(/_(.*?)_/g, '<em>$1</em>');
    
    // Código en línea `código`
    html = html.replace(/`([^`]+)`/g, '<code class="bg-pink-100 text-pink-800 px-1 py-0.5 rounded text-[11px] font-mono">$1</code>');

    // Saltos de línea
    html = html.replace(/\n/g, '<br>');

    return html;
}
