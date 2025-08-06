// Chat history management
const chatHistory = JSON.parse(localStorage.getItem('aiChatHistory') || '[]');
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const loading = document.getElementById('loading');
const typingIndicator = document.getElementById('typing-indicator');
const clearChatBtn = document.getElementById('clear-chat-btn');

// Load chat history on page load
function loadChatHistory() {
    chatMessages.innerHTML = '';
    chatHistory.forEach(message => {
        addMessageToChat(message.content, message.type, message.timestamp, message.model);
    });
    scrollToBottom();
}

// Save chat history to localStorage
function saveChatHistory() {
    localStorage.setItem('aiChatHistory', JSON.stringify(chatHistory));
}

// Clear chat history
function clearChatHistory() {
    console.log('Clear chat button clicked');
    
    if (confirm('Are you sure you want to clear all chat history? This action cannot be undone.')) {
        console.log('User confirmed clear chat');
        
        try {
            // Clear the chat history array
            chatHistory.length = 0;
            console.log('Chat history array cleared');
            
            // Clear localStorage
            localStorage.removeItem('aiChatHistory');
            console.log('localStorage cleared');
            
            // Clear the UI
            if (chatMessages) {
                chatMessages.innerHTML = '';
                console.log('Chat messages UI cleared');
            } else {
                console.error('chatMessages element not found');
            }
            
            // Show a confirmation message
            const confirmationDiv = document.createElement('div');
            confirmationDiv.className = 'message ai';
            confirmationDiv.innerHTML = `
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    <em>✅ Chat history has been cleared successfully.</em>
                </div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            `;
            
            if (chatMessages) {
                chatMessages.appendChild(confirmationDiv);
                console.log('Confirmation message added');
            }
            
            // Scroll to bottom
            scrollToBottom();
            
            // Focus on input
            if (messageInput) {
                messageInput.focus();
            }
            
            console.log('Chat clear operation completed successfully');
            
        } catch (error) {
            console.error('Error clearing chat history:', error);
            alert('Error clearing chat history. Please try again.');
        }
    } else {
        console.log('User cancelled clear chat');
    }
}

// Clear chat button click handler
if (clearChatBtn) {
    clearChatBtn.addEventListener('click', clearChatHistory);
    console.log('Clear chat button event listener attached');
} else {
    console.error('Clear chat button not found in DOM');
}

// Add message to chat
function addMessageToChat(content, type, timestamp, model = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '👤' : '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    if (type === 'ai') {
        let summary = '';
        let response = '';
        // Always try to parse as JSON first
        if (typeof content === 'string') {
            try {
                const parsed = JSON.parse(content);
                if (parsed && typeof parsed === 'object') {
                    summary = parsed.summary || '';
                    response = parsed.response || '';
                }
            } catch (e) {
                // Not JSON, fallback to regex extraction
                const summaryMatch = content.match(/Summary:\s*(.*?)(?:\n|$)/i);
                const responseMatch = content.match(/Response:\s*([\s\S]*)/i);
                if (summaryMatch) summary = summaryMatch[1].trim();
                if (responseMatch) response = responseMatch[1].trim();
            }
        } else if (typeof content === 'object' && content !== null) {
            summary = content.summary || '';
            response = content.response || '';
        }
        // Fallback if nothing found
        if (!summary && !response) {
            summary = '';
            response = typeof content === 'string' ? content : JSON.stringify(content);
        }
        // Clean up response if it's a stringified JSON
        if (typeof response === 'string') {
            response = response.replace(/^"|"$/g, ''); // Remove leading/trailing quotes
            try {
                // If response is itself JSON, parse and pretty print
                if ((response.startsWith('{') && response.endsWith('}')) || (response.startsWith('[') && response.endsWith(']'))){
                    const respObj = JSON.parse(response);
                    response = typeof respObj === 'string' ? respObj : JSON.stringify(respObj, null, 2);
                }
            } catch (e) {}
        }
        
        // Format the content with proper HTML handling
        let formattedContent = '';
        formattedContent += `<strong>📝 Summary:</strong> ${summary}<br><br>`;
        formattedContent += `<strong>💬 AI Response:</strong><br>${response}`;
        messageContent.innerHTML = formattedContent;
    } else {
        messageContent.textContent = content;
    }
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date(timestamp).toLocaleTimeString();
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    messageDiv.appendChild(timeDiv);
    
    chatMessages.appendChild(messageDiv);
}



// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Auto-resize textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Handle Enter key (send on Enter, new line on Shift+Enter)
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send message function
function sendMessage() {
    const message = messageInput.value.trim();
    const model = document.getElementById('model').value;
    
    if (!message) return;
    
    // Add user message to chat
    const userTimestamp = new Date().toISOString();
    addMessageToChat(message, 'user', userTimestamp);
    
    // Save to history
    chatHistory.push({
        content: message,
        type: 'user',
        timestamp: userTimestamp,
        model: model
    });
    saveChatHistory();
    
    // Clear input and disable send button
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendButton.disabled = true;
    loading.classList.add('show');
    typingIndicator.classList.add('show');
    
    scrollToBottom();
    
    // Send to server
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'message': message,
            'model': model
        }),
    })
    .then(response => response.json())
    .then(data => {
        typingIndicator.classList.remove('show');
        loading.classList.remove('show');
        sendButton.disabled = false;
        
        if (data.error) {
            addMessageToChat('Error: ' + data.error, 'ai', new Date().toISOString());
        } else {
            const aiResponse = `Summary: ${data.summary}\nResponse: ${data.response}`;
            const aiTimestamp = new Date().toISOString();
            
            addMessageToChat(aiResponse, 'ai', aiTimestamp, model);
            
            // Save AI response to history
            chatHistory.push({
                content: aiResponse,
                type: 'ai',
                timestamp: aiTimestamp,
                model: model
            });
            saveChatHistory();
        }
        
        scrollToBottom();
    })
    .catch(error => {
        typingIndicator.classList.remove('show');
        loading.classList.remove('show');
        sendButton.disabled = false;
        addMessageToChat('Error: ' + error.message, 'ai', new Date().toISOString());
        scrollToBottom();
    });
}

// Send button click handler
sendButton.addEventListener('click', sendMessage);

// Load chat history when page loads
loadChatHistory();

// Focus on input when page loads
messageInput.focus(); 