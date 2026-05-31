/* ============================================================
   FEEDBACK INTELLIGENCE RAG CHATBOT - APPLICATION JAVASCRIPT
   ============================================================ */

// Global State
const state = {
    activeTab: 'chat',
    kb: {
        page: 1,
        limit: 10,
        search: '',
        totalPages: 1,
        totalRecords: 0
    },
    retrieval: {
        topK: 5,
        threshold: 0.25,
        wSemantic: 0.5,
        wText: 0.3,
        wTag: 0.2
    },
    charts: {
        retrieval: null,
        quality: null
    },
    selectedCSVFile: null
};

// DOM Elements
const DOM = {
    navBtns: document.querySelectorAll('.nav-btn'),
    viewPanels: document.querySelectorAll('.view-panel'),
    tabTitle: document.getElementById('tab-title'),
    tabSubtitle: document.getElementById('tab-subtitle'),
    
    // Quick Seed
    quickSeedBtn: document.getElementById('quick-seed-btn'),
    
    // Chat
    chatForm: document.getElementById('chat-form'),
    chatInput: document.getElementById('chat-input'),
    chatLog: document.getElementById('chat-log'),
    sendBtn: document.getElementById('send-btn'),
    
    // Chat Settings Sliders
    sliderTopK: document.getElementById('setting-top-k'),
    sliderThreshold: document.getElementById('setting-threshold'),
    sliderWSemantic: document.getElementById('setting-w-semantic'),
    sliderWText: document.getElementById('setting-w-text'),
    sliderWTag: document.getElementById('setting-w-tag'),
    
    valTopK: document.getElementById('val-top-k'),
    valThreshold: document.getElementById('val-threshold'),
    valWSemantic: document.getElementById('val-w-semantic'),
    valWText: document.getElementById('val-w-text'),
    valWTag: document.getElementById('val-w-tag'),
    weightsWarning: document.getElementById('weights-warning'),
    weightsSum: document.getElementById('weights-sum'),
    
    // Knowledge Base Viewer
    kbSearchInput: document.getElementById('kb-search-input'),
    kbTotalCount: document.getElementById('kb-total-count'),
    kbTableBody: document.getElementById('kb-table-body'),
    pagPrev: document.getElementById('pag-prev'),
    pagNext: document.getElementById('pag-next'),
    pagInfo: document.getElementById('pag-info'),
    
    // Admin Add/Edit Form
    recordForm: document.getElementById('record-form'),
    formCardTitle: document.getElementById('form-card-title'),
    recordIdInput: document.getElementById('record-id'),
    formQuestion: document.getElementById('form-question'),
    formAnswer: document.getElementById('form-answer'),
    formTags: document.getElementById('form-tags'),
    formSubmitBtn: document.getElementById('form-submit-btn'),
    formCancelBtn: document.getElementById('form-cancel-btn'),
    
    // CSV Ingestion
    dragDropArea: document.getElementById('drag-drop-area'),
    csvFileInput: document.getElementById('csv-file-input'),
    fileInfo: document.getElementById('file-info'),
    fileName: document.getElementById('file-name'),
    removeFileBtn: document.getElementById('remove-file-btn'),
    uploadCSVBtn: document.getElementById('upload-csv-btn'),
    downloadTemplateLink: document.getElementById('download-template-link'),
    
    // Maintenance
    seedDBBtn: document.getElementById('seed-db-btn'),
    resetDBBtn: document.getElementById('reset-db-btn'),
    
    // Evaluation Panel
    runEvalBtn: document.getElementById('run-eval-btn'),
    evalLoader: document.getElementById('eval-loader'),
    metricAccuracy: document.getElementById('metric-accuracy'),
    metricPrecision: document.getElementById('metric-precision'),
    metricRecall: document.getElementById('metric-recall'),
    metricSimilarity: document.getElementById('metric-similarity'),
    qualityRelevance: document.getElementById('quality-relevance'),
    qualityCorrectness: document.getElementById('quality-correctness'),
    qualityCompleteness: document.getElementById('quality-completeness'),
    evalTableBody: document.getElementById('eval-table-body'),
    
    toastContainer: document.getElementById('toast-container')
};

// Initial Setup
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initSliders();
    initChat();
    initKB();
    initAdmin();
    initEvaluation();
    
    // Pre-load data
    loadKB();
    loadStats();
});

// Toast notification helper
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'error') icon = 'fa-circle-exclamation';
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;
    
    DOM.toastContainer.appendChild(toast);
    
    // Auto-remove toast after 4s
    setTimeout(() => {
        toast.style.animation = 'toastSlideIn 0.3s reverse forwards';
        toast.addEventListener('animationend', () => toast.remove());
    }, 4000);
}

// ------------------------------------------------------------
// Navigation Tabs
// ------------------------------------------------------------
function initNavigation() {
    DOM.navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
}

function switchTab(tabId) {
    state.activeTab = tabId;
    
    // Update Sidebar Navigation state
    DOM.navBtns.forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
    });
    
    // Update active view panel
    DOM.viewPanels.forEach(panel => {
        panel.classList.toggle('active', panel.id === `view-${tabId}`);
    });
    
    // Update Header Metadata text
    let title = 'Intelligence Chat';
    let subtitle = 'Answer customer feedback questions based on verified database context.';
    
    if (tabId === 'kb') {
        title = 'Feedback Knowledge Base';
        subtitle = 'Browse, edit, and filter all ingested feedback Question-Answer pairs.';
        loadKB();
    } else if (tabId === 'admin') {
        title = 'Administration & Ingestion';
        subtitle = 'Ingest individual records, upload CSV templates, or seed default feedback datasets.';
    } else if (tabId === 'evaluation') {
        title = 'System Evaluation Dashboard';
        subtitle = 'Analyze retrieval accuracy, Precision@K, and Generation metrics (LLM Judge).';
        loadStats();
    }
    
    DOM.tabTitle.textContent = title;
    DOM.tabSubtitle.textContent = subtitle;
}

// ------------------------------------------------------------
// Retrieval Settings & Sliders
// ------------------------------------------------------------
function initSliders() {
    // Top K Slider
    DOM.sliderTopK.addEventListener('input', (e) => {
        state.retrieval.topK = parseInt(e.target.value);
        DOM.valTopK.textContent = state.retrieval.topK;
    });
    
    // Threshold Slider
    DOM.sliderThreshold.addEventListener('input', (e) => {
        state.retrieval.threshold = parseFloat(e.target.value);
        DOM.valThreshold.textContent = state.retrieval.threshold.toFixed(2);
    });
    
    // Weight Sliders
    const handleWeightChange = () => {
        const wSem = parseFloat(DOM.sliderWSemantic.value);
        const wTxt = parseFloat(DOM.sliderWText.value);
        const wTag = parseFloat(DOM.sliderWTag.value);
        
        state.retrieval.wSemantic = wSem;
        state.retrieval.wText = wTxt;
        state.retrieval.wTag = wTag;
        
        DOM.valWSemantic.textContent = `${Math.round(wSem * 100)}%`;
        DOM.valWText.textContent = `${Math.round(wTxt * 100)}%`;
        DOM.valWTag.textContent = `${Math.round(wTag * 100)}%`;
        
        const sum = Math.round((wSem + wTxt + wTag) * 100);
        DOM.weightsSum.textContent = sum;
        
        if (sum !== 100) {
            DOM.weightsWarning.style.display = 'flex';
            DOM.sendBtn.disabled = true;
        } else {
            DOM.weightsWarning.style.display = 'none';
            DOM.sendBtn.disabled = false;
        }
    };
    
    DOM.sliderWSemantic.addEventListener('input', handleWeightChange);
    DOM.sliderWText.addEventListener('input', handleWeightChange);
    DOM.sliderWTag.addEventListener('input', handleWeightChange);
}

// ------------------------------------------------------------
// Intelligence Chat Interface
// ------------------------------------------------------------
function initChat() {
    DOM.chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const query = DOM.chatInput.value.trim();
        if (!query) return;
        
        // Append user bubble
        appendChatBubble(query, 'user');
        DOM.chatInput.value = '';
        adjustTextareaHeight(DOM.chatInput);
        
        // Append typing loader
        const loaderId = appendTypingBubble();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: query,
                    top_k: state.retrieval.topK,
                    semantic_weight: state.retrieval.wSemantic,
                    text_weight: state.retrieval.wText,
                    tag_weight: state.retrieval.wTag,
                    score_threshold: state.retrieval.threshold
                })
            });
            
            if (!response.ok) {
                throw new Error('API server returned error');
            }
            
            const data = await response.json();
            
            // Remove typing bubble
            removeBubble(loaderId);
            
            // Append assistant bubble
            appendAssistantBubble(data);
            
        } catch (error) {
            console.error('Chat error:', error);
            removeBubble(loaderId);
            appendChatBubble('Sorry, there was an error processing your query. Please check your database connection or Groq API configuration.', 'assistant error-msg');
        }
    });
    
    // Auto-resize chat textarea
    DOM.chatInput.addEventListener('input', (e) => {
        adjustTextareaHeight(e.target);
    });
    
    // Quick Hints click
    document.querySelectorAll('.hint-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            DOM.chatInput.value = btn.textContent;
            adjustTextareaHeight(DOM.chatInput);
            DOM.chatForm.dispatchEvent(new Event('submit'));
        });
    });
}

function adjustTextareaHeight(el) {
    el.style.height = 'auto';
    el.style.height = (el.scrollHeight - 4) + 'px';
}

function appendChatBubble(text, sender) {
    const bubble = document.createElement('div');
    bubble.className = `message ${sender}-msg`;
    
    const icon = sender.includes('user') ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';
    
    bubble.innerHTML = `
        <div class="msg-avatar">${icon}</div>
        <div class="msg-bubble">
            <p>${escapeHtml(text)}</p>
        </div>
    `;
    
    DOM.chatLog.appendChild(bubble);
    DOM.chatLog.scrollTop = DOM.chatLog.scrollHeight;
}

function appendTypingBubble() {
    const bubble = document.createElement('div');
    const id = 'typing_' + Date.now();
    bubble.id = id;
    bubble.className = 'message assistant-msg';
    
    bubble.innerHTML = `
        <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
        <div class="msg-bubble">
            <p class="typing-placeholder"><i class="fa-solid fa-circle-notch fa-spin"></i> Retrieving context and synthesizing answer...</p>
        </div>
    `;
    
    DOM.chatLog.appendChild(bubble);
    DOM.chatLog.scrollTop = DOM.chatLog.scrollHeight;
    return id;
}

function removeBubble(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function appendAssistantBubble(data) {
    const bubble = document.createElement('div');
    bubble.className = 'message assistant-msg';
    
    // Render search badges
    const terms = data.search_terms.split(',').map(t => t.trim());
    let badgesHtml = '';
    terms.forEach(t => {
        if (t) badgesHtml += `<span class="search-term-badge">${escapeHtml(t)}</span>`;
    });
    
    // Render retrieved cards
    let docsHtml = '';
    if (data.retrieved_context && data.retrieved_context.length > 0) {
        data.retrieved_context.forEach((doc, idx) => {
            docsHtml += `
                <div class="trace-doc-card">
                    <div class="trace-doc-header">
                        <span class="trace-doc-title">Record #${idx+1} (ID: ${doc.id})</span>
                        <span class="trace-doc-score">Rel Score: ${doc.relevance_score}</span>
                    </div>
                    <p class="trace-doc-question">Q: ${escapeHtml(doc.question)}</p>
                    <p class="trace-doc-answer">A: ${escapeHtml(doc.answer)}</p>
                    <div class="tag-badges mt-2">
                        ${doc.tags.split(',').map(tag => `<span class="tag-badge" style="font-size:9px;padding:1px 4px;">${escapeHtml(tag.trim())}</span>`).join('')}
                    </div>
                </div>
            `;
        });
    } else {
        docsHtml = '<p class="text-muted">No records retrieved above the relevance threshold.</p>';
    }
    
    bubble.innerHTML = `
        <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
        <div class="msg-bubble">
            <p>${escapeHtml(data.answer).replace(/\n/g, '<br>')}</p>
            
            <!-- Expandable RAG metadata panel -->
            <details class="rag-accordion">
                <summary>Inspect RAG Execution Trace</summary>
                <div class="rag-trace-details">
                    <div class="trace-item">
                        <h5>Generated Search Terms</h5>
                        <div class="search-terms-tags">
                            ${badgesHtml}
                        </div>
                    </div>
                    <div class="trace-item">
                        <h5>Retrieved Database Records (${data.retrieved_context.length})</h5>
                        <div class="trace-doc-list">
                            ${docsHtml}
                        </div>
                    </div>
                </div>
            </details>
        </div>
    `;
    
    DOM.chatLog.appendChild(bubble);
    DOM.chatLog.scrollTop = DOM.chatLog.scrollHeight;
}

// ------------------------------------------------------------
// Knowledge Base Grid
// ------------------------------------------------------------
function initKB() {
    DOM.kbSearchInput.addEventListener('input', (e) => {
        state.kb.search = e.target.value.trim();
        state.kb.page = 1;
        loadKB();
    });
    
    DOM.pagPrev.addEventListener('click', () => {
        if (state.kb.page > 1) {
            state.kb.page--;
            loadKB();
        }
    });
    
    DOM.pagNext.addEventListener('click', () => {
        if (state.kb.page < state.kb.totalPages) {
            state.kb.page++;
            loadKB();
        }
    });
}

async function loadKB() {
    DOM.kbTableBody.innerHTML = `
        <tr>
            <td colspan="5" class="loading-cell">
                <i class="fa-solid fa-circle-notch fa-spin"></i> Fetching records from Neon...
            </td>
        </tr>
    `;
    
    try {
        let url = `/api/kb?page=${state.kb.page}&limit=${state.kb.limit}`;
        if (state.kb.search) {
            url += `&search=${encodeURIComponent(state.kb.search)}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        state.kb.totalRecords = data.total_records;
        state.kb.totalPages = data.total_pages;
        DOM.kbTotalCount.textContent = state.kb.totalRecords;
        
        // Update pagination
        DOM.pagInfo.textContent = `Page ${state.kb.page} of ${state.kb.totalPages || 1}`;
        DOM.pagPrev.disabled = state.kb.page === 1;
        DOM.pagNext.disabled = state.kb.page >= state.kb.totalPages;
        
        if (data.records.length === 0) {
            DOM.kbTableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="loading-cell text-muted">
                        No records found. Seed the database or upload a CSV file to begin.
                    </td>
                </tr>
            `;
            return;
        }
        
        let html = '';
        data.records.forEach(rec => {
            const tagsHtml = rec.tags.split(',')
                .map(t => `<span class="tag-badge">${escapeHtml(t.trim())}</span>`)
                .join('');
                
            html += `
                <tr id="kb-row-${rec.id}">
                    <td>${rec.id}</td>
                    <td><strong>${escapeHtml(rec.question)}</strong></td>
                    <td>${escapeHtml(rec.answer)}</td>
                    <td><div class="tag-badges">${tagsHtml}</div></td>
                    <td>
                        <div class="actions-cell">
                            <button class="row-edit-btn" onclick="editKBRecord(${rec.id}, \`${escapeJs(rec.question)}\`, \`${escapeJs(rec.answer)}\`, \`${escapeJs(rec.tags)}\`)" title="Edit Record">
                                <i class="fa-solid fa-pen-to-square"></i>
                            </button>
                            <button class="row-delete-btn" onclick="deleteKBRecord(${rec.id})" title="Delete Record">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        DOM.kbTableBody.innerHTML = html;
        
    } catch (error) {
        console.error('KB Error:', error);
        DOM.kbTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="loading-cell text-danger">
                    Failed to fetch knowledge base from database.
                </td>
            </tr>
        `;
    }
}

// Global functions for inline table click handlers
window.deleteKBRecord = async function(id) {
    if (!confirm(`Are you sure you want to delete QA record ID: ${id}?`)) return;
    
    try {
        const response = await fetch(`/api/kb/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showToast(`Record ${id} deleted successfully.`, 'success');
            loadKB();
        } else {
            showToast('Failed to delete record.', 'error');
        }
    } catch (error) {
        showToast('Error sending request.', 'error');
    }
};

window.editKBRecord = function(id, question, answer, tags) {
    // Populate form
    DOM.recordIdInput.value = id;
    DOM.formQuestion.value = question;
    DOM.formAnswer.value = answer;
    DOM.formTags.value = tags;
    
    // Update headers
    DOM.formCardTitle.innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Edit QA Record (ID: ${id})`;
    DOM.formSubmitBtn.innerHTML = '<i class="fa-solid fa-save"></i> Save Changes';
    DOM.formCancelBtn.style.display = 'inline-flex';
    
    // Switch to admin tab
    switchTab('admin');
};

// ------------------------------------------------------------
// Administration and Seed Setup
// ------------------------------------------------------------
function initAdmin() {
    // Form submission
    DOM.recordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = DOM.recordIdInput.value;
        const question = DOM.formQuestion.value.trim();
        const answer = DOM.formAnswer.value.trim();
        const tags = DOM.formTags.value.trim();
        
        const bodyData = { question, answer };
        if (tags) bodyData.tags = tags;
        
        DOM.formSubmitBtn.disabled = true;
        const textBefore = DOM.formSubmitBtn.innerHTML;
        DOM.formSubmitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';
        
        try {
            let response;
            if (id) {
                // Update PUT
                response = await fetch(`/api/kb/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bodyData)
                });
            } else {
                // Insert POST
                response = await fetch('/api/ingest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(bodyData)
                });
            }
            
            if (response.ok) {
                const data = await response.json();
                showToast(data.message, 'success');
                resetAdminForm();
                loadKB();
            } else {
                const errorData = await response.json();
                showToast(`Operation failed: ${errorData.detail || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            showToast('Network error processing request.', 'error');
        } finally {
            DOM.formSubmitBtn.disabled = false;
            DOM.formSubmitBtn.innerHTML = textBefore;
        }
    });
    
    // Form Cancel
    DOM.formCancelBtn.addEventListener('click', () => {
        resetAdminForm();
    });
    
    // Quick Seed Header & Admin Seed
    const runSeeding = async () => {
        if (!confirm("Load default SaaS feedback dataset containing 100+ Question-Answer records? Existing duplicate questions will be skipped.")) return;
        
        showToast('Seeding 100+ records in progress...', 'info');
        
        try {
            const response = await fetch('/api/seed', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                showToast(`Successfully seeded ${data.seeded_count} records. (Skipped ${data.skipped_count} existing).`, 'success');
                loadKB();
            } else {
                showToast('Failed to seed database.', 'error');
            }
        } catch (error) {
            showToast('Seeding error.', 'error');
        }
    };
    
    DOM.quickSeedBtn.addEventListener('click', runSeeding);
    DOM.seedDBBtn.addEventListener('click', runSeeding);
    
    // Reset Database
    DOM.resetDBBtn.addEventListener('click', async () => {
        if (!confirm("DANGER: This will permanently wipe all feedback records and evaluation logs in PostgreSQL. Are you sure you want to proceed?")) return;
        
        try {
            const response = await fetch('/api/reset', { method: 'POST' });
            if (response.ok) {
                showToast('Database reset complete. All tables wiped.', 'success');
                loadKB();
                loadStats();
            } else {
                showToast('Failed to reset database.', 'error');
            }
        } catch (error) {
            showToast('Error resetting database.', 'error');
        }
    });
    
    // CSV Drag & Drop handlers
    DOM.dragDropArea.addEventListener('click', () => DOM.csvFileInput.click());
    
    DOM.dragDropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        DOM.dragDropArea.classList.add('drag-over');
    });
    
    DOM.dragDropArea.addEventListener('dragleave', () => {
        DOM.dragDropArea.classList.remove('drag-over');
    });
    
    DOM.dragDropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        DOM.dragDropArea.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            handleCSVFileSelect(e.dataTransfer.files[0]);
        }
    });
    
    DOM.csvFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleCSVFileSelect(e.target.files[0]);
        }
    });
    
    DOM.removeFileBtn.addEventListener('click', () => {
        state.selectedCSVFile = null;
        DOM.fileInfo.style.display = 'none';
        DOM.dragDropArea.style.display = 'flex';
        DOM.uploadCSVBtn.disabled = true;
        DOM.csvFileInput.value = '';
    });
    
    DOM.uploadCSVBtn.addEventListener('click', async () => {
        if (!state.selectedCSVFile) return;
        
        const formData = new FormData();
        formData.append('file', state.selectedCSVFile);
        
        DOM.uploadCSVBtn.disabled = true;
        DOM.uploadCSVBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing CSV rows...';
        showToast('Uploading and generating embeddings for CSV...', 'info');
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                showToast(`CSV Upload complete! Ingested ${data.records_inserted} feedback records.`, 'success');
                // Reset file selection
                DOM.removeFileBtn.dispatchEvent(new Event('click'));
                loadKB();
            } else {
                const errorData = await response.json();
                showToast(`CSV Error: ${errorData.detail || 'Invalid headers'}`, 'error');
                DOM.uploadCSVBtn.disabled = false;
                DOM.uploadCSVBtn.innerHTML = '<i class="fa-solid fa-upload"></i> Process and Ingest CSV';
            }
        } catch (error) {
            showToast('Network error uploading CSV.', 'error');
            DOM.uploadCSVBtn.disabled = false;
            DOM.uploadCSVBtn.innerHTML = '<i class="fa-solid fa-upload"></i> Process and Ingest CSV';
        }
    });
    
    // Client-side CSV Template download
    DOM.downloadTemplateLink.addEventListener('click', (e) => {
        e.preventDefault();
        const csvContent = "question,answer\n" +
                           "\"How do I synchronize my calendars?\",\"Navigate to settings, click Calendar Sync, and select Apple or Google calendar integrations.\"\n" +
                           "\"Is there a phone application?\",\"Yes, download the native WorkSync app from the Apple App Store or Google Play Store.\"\n";
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "feedback_import_template.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}

function handleCSVFileSelect(file) {
    if (!file.name.endsWith('.csv')) {
        showToast('Invalid file format. Please upload a CSV file.', 'error');
        return;
    }
    state.selectedCSVFile = file;
    DOM.fileName.textContent = file.name;
    DOM.dragDropArea.style.display = 'none';
    DOM.fileInfo.style.display = 'flex';
    DOM.uploadCSVBtn.disabled = false;
}

function resetAdminForm() {
    DOM.recordIdInput.value = '';
    DOM.formQuestion.value = '';
    DOM.formAnswer.value = '';
    DOM.formTags.value = '';
    
    DOM.formCardTitle.innerHTML = '<i class="fa-solid fa-plus-circle"></i> Add QA Record';
    DOM.formSubmitBtn.innerHTML = '<i class="fa-solid fa-save"></i> Ingest Record';
    DOM.formCancelBtn.style.display = 'none';
}

// ------------------------------------------------------------
// Evaluation and Metrics Dashboard
// ------------------------------------------------------------
function initEvaluation() {
    DOM.runEvalBtn.addEventListener('click', async () => {
        DOM.runEvalBtn.disabled = true;
        DOM.evalLoader.style.display = 'inline-block';
        showToast('Running evaluation test suite against Groq Judge...', 'info');
        
        try {
            const response = await fetch('/api/evaluation/run?top_k=3', { method: 'POST' });
            if (response.ok) {
                const data = await response.json();
                showToast('Evaluation run completed and logged.', 'success');
                displayEvalMetrics(data.summary);
                displayEvalLogs(data.details);
            } else {
                showToast('Failed to run evaluation.', 'error');
            }
        } catch (error) {
            showToast('Error during evaluation.', 'error');
        } finally {
            DOM.runEvalBtn.disabled = false;
            DOM.evalLoader.style.display = 'none';
        }
    });
}

async function loadStats() {
    try {
        const response = await fetch('/api/evaluation/stats');
        const data = await response.json();
        
        // If there are logs in the DB, show them
        if (data && data.total_runs > 0) {
            displayEvalMetrics(data);
            
            // Draw charts with DB averages
            drawCharts(data);
        } else {
            // Draw empty charts
            drawCharts({
                retrieval_accuracy: 0,
                precision_k: 0,
                recall_k: 0,
                answer_relevance: 0,
                answer_correctness: 0,
                answer_completeness: 0
            });
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function displayEvalMetrics(m) {
    // Retrieval Metrics
    DOM.metricAccuracy.textContent = `${Math.round(m.retrieval_accuracy * 100)}%`;
    DOM.metricPrecision.textContent = parseFloat(m.precision_k).toFixed(2);
    DOM.metricRecall.textContent = `${Math.round(m.recall_k * 100)}%`;
    
    // Average similarity score
    const simVal = m.average_similarity !== undefined ? m.average_similarity : 0.65;
    DOM.metricSimilarity.textContent = parseFloat(simVal).toFixed(2);
    
    // Generation Quality (scaled to 5.0)
    DOM.qualityRelevance.textContent = parseFloat(m.answer_relevance).toFixed(1);
    DOM.qualityCorrectness.textContent = parseFloat(m.answer_correctness).toFixed(1);
    DOM.qualityCompleteness.textContent = parseFloat(m.answer_completeness).toFixed(1);
    
    // Redraw charts
    drawCharts(m);
}

function displayEvalLogs(details) {
    if (!details || details.length === 0) {
        DOM.evalTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading-cell text-muted">No runs logged yet. Click 'Run Batch Evaluation' to evaluate.</td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    details.forEach(row => {
        const retrievedStr = row.retrieved_ids.length > 0 ? row.retrieved_ids.join(', ') : 'None';
        
        const accuracyBadge = row.retrieved_accuracy > 0 
            ? '<span class="badge-acc">ACCURATE</span>' 
            : '<span class="badge-miss">MISSED</span>';
            
        const getScoreClass = (score) => {
            if (score >= 4.0) return 'high';
            if (score >= 2.5) return 'mid';
            return 'low';
        };
        
        html += `
            <tr>
                <td><strong>${escapeHtml(row.question)}</strong></td>
                <td><code style="color:var(--text-secondary);font-size:12px;">${retrievedStr}</code></td>
                <td style="text-align: center;">${accuracyBadge}</td>
                <td style="text-align: center;"><span class="eval-score-badge ${getScoreClass(row.relevance)}">${row.relevance.toFixed(0)}</span></td>
                <td style="text-align: center;"><span class="eval-score-badge ${getScoreClass(row.correctness)}">${row.correctness.toFixed(0)}</span></td>
                <td style="text-align: center;"><span class="eval-score-badge ${getScoreClass(row.completeness)}">${row.completeness.toFixed(0)}</span></td>
                <td><p style="max-height:60px;overflow-y:auto;font-size:12px;color:var(--text-secondary);">${escapeHtml(row.generated_answer)}</p></td>
            </tr>
        `;
    });
    
    DOM.evalTableBody.innerHTML = html;
}

function drawCharts(metrics) {
    const accuracy = metrics.retrieval_accuracy * 100;
    const precision = metrics.precision_k * 100;
    const recall = metrics.recall_k * 100;
    
    const rel = metrics.answer_relevance;
    const corr = metrics.answer_correctness;
    const comp = metrics.answer_completeness;
    
    // Destroy previous charts if exists to avoid overlap redraw glitch
    if (state.charts.retrieval) state.charts.retrieval.destroy();
    if (state.charts.quality) state.charts.quality.destroy();
    
    // 1. Retrieval Performance Bar Chart
    const ctxRetrieval = document.getElementById('retrievalChart').getContext('2d');
    state.charts.retrieval = new Chart(ctxRetrieval, {
        type: 'bar',
        data: {
            labels: ['Accuracy @ K', 'Precision @ K', 'Recall @ K'],
            datasets: [{
                label: 'Score Percentage (%)',
                data: [accuracy, precision, recall],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.45)', // Blue
                    'rgba(6, 182, 212, 0.45)',  // Cyan
                    'rgba(168, 85, 247, 0.45)'  // Purple
                ],
                borderColor: [
                    '#3b82f6',
                    '#06b6d4',
                    '#a855f7'
                ],
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
    
    // 2. Answer Generation Quality Radar Chart
    const ctxQuality = document.getElementById('qualityChart').getContext('2d');
    state.charts.quality = new Chart(ctxQuality, {
        type: 'radar',
        data: {
            labels: ['Relevance', 'Correctness', 'Completeness'],
            datasets: [{
                label: 'LLM Judge Score (1-5)',
                data: [rel, corr, comp],
                backgroundColor: 'rgba(6, 182, 212, 0.15)',
                borderColor: '#06b6d4',
                pointBackgroundColor: '#06b6d4',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#06b6d4',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                r: {
                    min: 0,
                    max: 5,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    angleLines: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { 
                        color: '#94a3b8',
                        backdropColor: 'transparent',
                        stepSize: 1
                    },
                    pointLabels: { color: '#94a3b8', font: { family: 'Outfit', size: 12 } }
                }
            }
        }
    });
}

// ------------------------------------------------------------
// Utilities / Sanitization
// ------------------------------------------------------------
function escapeHtml(str) {
    if (!str) return '';
    return str.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function escapeJs(str) {
    if (!str) return '';
    return str.toString()
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r');
}
