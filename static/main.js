// --- Element Selectors ---
const userIdInput = document.getElementById('user-id-input');
const topicInput = document.getElementById('topic-input');
const promptInput = document.getElementById('prompt-input');
const chatForm = document.getElementById('chat-form');
const uploadForm = document.getElementById('upload-form');
const repoForm = document.getElementById('repo-form');
const chatWindow = document.getElementById('chat-window');
const statusMessage = document.getElementById('status-message');

// --- Event Listeners ---
repoForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const repoUrl = document.getElementById('repo-url-input').value;
    const userId = userIdInput.value;
    const topic = topicInput.value;
    if (!userId || !topic || !repoUrl) {
        showStatus('User ID, Topic, and Repository URL are required.', 'danger');
        return;
    }
    showStatus(`Starting ingestion for ${repoUrl}...`, 'info');
    try {
        const response = await fetch('/ingest_repo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, topic: topic, repo_url: repoUrl })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        showStatus(data.message, 'success');
    } catch (error) {
        showStatus(error.message, 'danger');
    }
});

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userId = userIdInput.value;
    const topic = topicInput.value;
    const fileInput = document.getElementById('file-input');
    if (!userId || !topic || fileInput.files.length === 0) {
        showStatus('User ID, Topic, and a file are required.', 'danger');
        return;
    }
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('file', fileInput.files[0]);
    formData.append('topic', topic);
    showStatus('Uploading...', 'info');
    try {
        const response = await fetch('/upload', { method: 'POST', body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Upload failed');
        showStatus(data.message, 'success');
        fileInput.value = '';
    } catch (error) {
        showStatus(error.message, 'danger');
    }
});

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userId = userIdInput.value;
    const topic = topicInput.value;
    const prompt = promptInput.value.trim();
    if (!userId || !topic || !prompt) {
        showStatus('User ID, Topic, and a message are required.', 'danger');
        return;
    }
    addMessage(prompt, 'user');
    promptInput.value = '';
    addSpinner();
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, topic: topic, prompt: prompt })
        });
        removeSpinner();
        if (!response.ok) throw new Error('Network response was not ok.');
        const data = await response.json();
        addMessage(data.response, 'ai');
    } catch (error) {
        removeSpinner();
        addMessage('Sorry, an error occurred.', 'ai error');
    }
});

// --- Helper Functions ---
function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `text-${type} small`;
    if (type !== 'info') {
        setTimeout(() => { statusMessage.textContent = ''; }, 5000);
    }
}
function addMessage(text, sender) {
    const wrapper = document.createElement('div');
    wrapper.className = `d-flex justify-content-${sender === 'user' ? 'end' : 'start'} mb-3`;
    const bubble = document.createElement('div');
    bubble.className = `p-3 rounded message-bubble ${sender}-message`;
    bubble.textContent = text;
    wrapper.appendChild(bubble);
    chatWindow.appendChild(wrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
function addSpinner() {
     const spinnerWrapper = document.createElement('div');
    spinnerWrapper.id = 'spinner';
    spinnerWrapper.className = 'd-flex justify-content-start mb-3';
    const spinnerBubble = document.createElement('div');
    spinnerBubble.className = 'p-3 rounded message-bubble ai-message';
    spinnerBubble.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>';
    spinnerWrapper.appendChild(spinnerBubble);
    chatWindow.appendChild(spinnerWrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
function removeSpinner() {
    const spinner = document.getElementById('spinner');
    if (spinner) spinner.remove();
}
promptInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});