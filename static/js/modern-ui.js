// Modern UI JavaScript for ShieldOps AI

// Star Rating System - initialize when DOM is ready
let stars = [];
let selectedRating = 0;

document.addEventListener('DOMContentLoaded', function() {
    stars = document.querySelectorAll('.star') || [];
    initializeStarRating();
    initializeRatingForm();
    initializeScrollAnimations();
    initializeScoreCards();
    initializeLanguageClass();
});

function initializeStarRating() {
    if (!stars.length) return;
    stars.forEach((star, index) => {
        star.addEventListener('click', () => {
            selectedRating = index + 1;
            updateStars();
            addGlowEffect();
        });
        star.addEventListener('mouseenter', () => {
            highlightStars(index + 1);
        });
    });

    if (document.querySelector('.rating-stars')) {
        document.querySelector('.rating-stars').addEventListener('mouseleave', () => {
            updateStars();
        });
    }
}

const getToastIcon = (type) => {
    if (type === 'success') return '✅';
    if (type === 'error') return '❌';
    if (type === 'warning') return '⚠️';
    return 'ℹ️';
};

window.showToast = function showToast(message, type = 'info') {
    const msg = String(message || '').trim();
    if (!msg) return;
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${getToastIcon(type)}</span>
        <div class="toast-content">${msg}</div>
        <button class="toast-close" type="button">✕</button>
    `;
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });
    container.appendChild(toast);
    setTimeout(() => {
        if (toast && toast.parentNode) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-8px)';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
};

window.alert = function(message) {
    showToast(message, 'error');
};

window.showToast = function showToast(message, type = 'info', options = {}) {
    const msg = String(message || '').trim();
    if (!msg) return;

    const actionLabel = String(options.actionLabel || '').trim();
    const onAction = typeof options.onAction === 'function' ? options.onAction : null;
    const duration = Number(options.duration) > 0 ? Number(options.duration) : 5000;
    const color = type === 'success' ? '#00ff88' : (type === 'warning' ? '#ff9500' : (type === 'error' ? '#ff3366' : '#00d4ff'));

    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.setProperty('--toast-color', color);

    const iconEl = document.createElement('span');
    iconEl.className = 'toast-icon';
    iconEl.textContent = getToastIcon(type);

    const bodyEl = document.createElement('div');
    bodyEl.className = 'toast-body';

    const contentEl = document.createElement('div');
    contentEl.className = 'toast-content';
    contentEl.textContent = msg;
    bodyEl.appendChild(contentEl);

    if (actionLabel && onAction) {
        const actionBtn = document.createElement('button');
        actionBtn.className = 'toast-action';
        actionBtn.type = 'button';
        actionBtn.textContent = actionLabel;
        actionBtn.addEventListener('click', () => {
            try {
                onAction();
            } finally {
                toast.remove();
            }
        });
        bodyEl.appendChild(actionBtn);
    }

    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.type = 'button';
    closeBtn.textContent = '✕';
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });

    toast.appendChild(iconEl);
    toast.appendChild(bodyEl);
    toast.appendChild(closeBtn);
    container.appendChild(toast);

    setTimeout(() => {
        if (toast && toast.parentNode) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(12px)';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
};

stars.forEach((star, index) => {
    star.addEventListener('click', () => {
        selectedRating = index + 1;
        updateStars();
        addGlowEffect();
    });

    star.addEventListener('mouseenter', () => {
        highlightStars(index + 1);
    });
});

if (document.querySelector('.rating-stars')) {
    document.querySelector('.rating-stars').addEventListener('mouseleave', () => {
        updateStars();
    });
}

function updateStars() {
    stars.forEach((star, index) => {
        if (index < selectedRating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function highlightStars(rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function addGlowEffect() {
    stars.forEach((star, index) => {
        if (index < selectedRating) {
            star.classList.add('glow');
            setTimeout(() => star.classList.remove('glow'), 1500);
        }
    });
}

// Form Submission for Rating
function initializeRatingForm() {
    const ratingForm = document.getElementById('ratingForm');
    if (!ratingForm) return;
    ratingForm.addEventListener('submit', (e) => {
        e.preventDefault();

        if (selectedRating === 0) {
            const lang = document.documentElement.lang || 'ar';
            const messages = {
                ar: 'يرجى اختيار تقييم بالنجوم',
                en: 'Please select a star rating',
                zh: '请选择星级评分',
                es: 'Por favor selecciona una calificación con estrellas'
            };
            showToast(messages[lang] || messages.ar, 'warning');
            return;
        }

        const submitBtn = e.target.querySelector('.submit-btn');
        const originalText = submitBtn.innerHTML;
        const lang = document.documentElement.lang || 'ar';

        const submitTexts = {
            ar: '<i class="fas fa-spinner fa-spin"></i> جار الإرسال...',
            en: '<i class="fas fa-spinner fa-spin"></i> Submitting...',
            zh: '<i class="fas fa-spinner fa-spin"></i> 提交中...',
            es: '<i class="fas fa-spinner fa-spin"></i> Enviando...'
        };

        const successTexts = {
            ar: '<i class="fas fa-check"></i> تم الإرسال بنجاح!',
            en: '<i class="fas fa-check"></i> Submitted successfully!',
            zh: '<i class="fas fa-check"></i> 提交成功！',
            es: '<i class="fas fa-check"></i> ¡Enviado con éxito!'
        };

        submitBtn.innerHTML = submitTexts[lang];
        submitBtn.disabled = true;

        // Send to backend
        const formData = new FormData(e.target);
        formData.append('rating', selectedRating);

        fetch('/submit_rating', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Rating submission failed');
                }
                return response.json();
            })
            .then(data => {
                submitBtn.innerHTML = successTexts[lang];
                submitBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';

                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    submitBtn.disabled = false;
                    ratingForm.reset();
                    selectedRating = 0;
                    updateStars();
                }, 2000);
            })
            .catch(error => {
                console.error('Error submitting rating:', error);
                submitBtn.innerHTML = originalText;
                submitBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                submitBtn.disabled = false;
            });
    });
}

// Vote System - One vote per user per suggestion
function vote(button, isUpvote) {
    const voteBtns = button.parentElement.querySelectorAll('.vote-btn');
    const suggestionCard = button.closest('.suggestion-card');
    const suggestionTitle = suggestionCard?.querySelector('h4')?.textContent || 'Unknown';

    // Create unique key for this suggestion
    const voteKey = `vote_${suggestionTitle.replace(/\s+/g, '_')}`;

    // Check if user already voted (client-side check)
    const existingVote = localStorage.getItem(voteKey);
    if (existingVote) {
        const lang = document.documentElement.lang || 'ar';
        const messages = {
            ar: 'لقد قمت بالتصويت بالفعل على هذا الاقتراح',
            en: 'You have already voted on this suggestion',
            zh: '您已经对此建议投票',
            es: 'Ya has votado por esta sugerencia'
        };
        showToast(messages[lang] || messages.ar, 'warning');
        return;
    }

    // Remove previous votes visually
    voteBtns.forEach(btn => btn.classList.remove('voted'));

    // Add current vote
    button.classList.add('voted');

    // Animate the button
    button.style.transform = 'scale(0.95)';
    setTimeout(() => {
        button.style.transform = 'scale(1)';
    }, 150);

    // Disable both buttons to prevent multiple clicks
    voteBtns.forEach(btn => btn.style.pointerEvents = 'none');

    // Send vote to backend
    fetch('/submit_vote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            suggestion: suggestionTitle,
            vote_type: isUpvote ? 'upvote' : 'downvote'
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Vote submitted successfully');

                // Update counter visually
                const counterSpan = button.querySelector('span');
                if (counterSpan) {
                    let currentCount = parseInt(counterSpan.textContent.replace(/[()]/g, '')) || 0;
                    currentCount++;
                    counterSpan.textContent = `(${currentCount})`;
                }

                // Save vote to localStorage to prevent duplicate votes
                localStorage.setItem(voteKey, isUpvote ? 'upvote' : 'downvote');
            } else {
                // If backend says already voted, restore UI
                const lang = document.documentElement.lang || 'ar';
                const messages = {
                    ar: data.message || 'لقد قمت بالتصويت بالفعل',
                    en: data.message || 'Already voted',
                    zh: data.message || '已投票',
                    es: data.message || 'Ya votado'
                };
                showToast(messages[lang], 'error');

                // Re-enable buttons
                voteBtns.forEach(btn => {
                    btn.classList.remove('voted');
                    btn.style.pointerEvents = 'auto';
                });
            }
        })
        .catch(error => {
            console.error('Error submitting vote:', error);
            // Re-enable buttons on error
            voteBtns.forEach(btn => {
                btn.classList.remove('voted');
                btn.style.pointerEvents = 'auto';
            });
        });
}

// Make vote function available globally
window.vote = vote;

// Scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

function initializeScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });
}

function initializeScoreCards() {
    // Add smooth hover effects for score cards
    document.querySelectorAll('.score-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px) scale(1.02)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Simulate real-time updates for score trends
    setInterval(() => {
        const trends = document.querySelectorAll('.score-trend');
        trends.forEach(trend => {
            if (Math.random() > 0.7) { // 30% chance to update
                const isPositive = Math.random() > 0.5;
                const change = Math.floor(Math.random() * 5) + 1;
                const symbol = isPositive ? '↗️' : '↘️';
                const percentage = change + '%';
                trend.textContent = `${symbol} ${isPositive ? '+' : '-'}${percentage}`;
            }
        });
    }, 5000);
}

function initializeLanguageClass() {
    const lang = document.documentElement.lang || 'ar';
    document.body.classList.add(`lang-${lang}`);
}

// Export: Download structured report (PDF if available, else HTML)
function buildReportExtras() {
    const getNum = (id) => {
        const el = document.getElementById(id);
        const v = el ? parseFloat((el.textContent || '0').replace(/[^0-9.]/g, '')) : 0;
        return isNaN(v) ? 0 : v;
    };

    const heuristic = window.currentHeuristicDetails && typeof window.currentHeuristicDetails === 'object'
        ? window.currentHeuristicDetails
        : null;
    const v2 = window.currentV2Scan && typeof window.currentV2Scan === 'object'
        ? window.currentV2Scan
        : null;
    const baseReco = window.currentBaseImageRecommendation && typeof window.currentBaseImageRecommendation === 'object'
        ? window.currentBaseImageRecommendation
        : null;
    const layerAnalysis = window.currentImageLayerAnalysis && typeof window.currentImageLayerAnalysis === 'object'
        ? window.currentImageLayerAnalysis
        : null;
    const dockerignoreAnalysis = window.currentDockerignoreAnalysis && typeof window.currentDockerignoreAnalysis === 'object'
        ? window.currentDockerignoreAnalysis
        : null;
    const advancedDelivery = window.currentAdvancedDeliveryAnalysis && typeof window.currentAdvancedDeliveryAnalysis === 'object'
        ? window.currentAdvancedDeliveryAnalysis
        : null;
    const sbomSummary = window.currentSbomSummary && typeof window.currentSbomSummary === 'object'
        ? window.currentSbomSummary
        : null;
    const supplyChainSummary = window.currentSupplyChainSummary && typeof window.currentSupplyChainSummary === 'object'
        ? window.currentSupplyChainSummary
        : null;
    const beforeContent = (window.lastOriginalDockerfileBeforeFix || '').trim();
    const afterContent = (window.lastFixedDockerfile || '').trim();
    const analysisV2 = window.currentAnalysisPayload && typeof window.currentAnalysisPayload === 'object'
        ? window.currentAnalysisPayload.analysis_v2
        : null;
    const beforeAfter = beforeContent
        ? {
            before: beforeContent,
            after: afterContent
        }
        : null;

    return {
        scores: {
            security: getNum('securityScore'),
            performance: getNum('performanceScore'),
            efficiency: getNum('efficiencyScore'),
            bestPractices: getNum('bestPracticesScore')
        },
        engine: window.currentEngine || ((window.currentAnalysisPayload && window.currentAnalysisPayload.engine) || ''),
        internal_engine: heuristic,
        v2_scan: v2,
        analysis_v2: analysisV2,
        base_image_recommendation: baseReco,
        image_layer_analysis: layerAnalysis,
        dockerignore_analysis: dockerignoreAnalysis,
        advanced_delivery_analysis: advancedDelivery,
        sbom_summary: sbomSummary,
        supply_chain_summary: supplyChainSummary,
        before_after: beforeAfter
    };
}

function _isPdfPlanAllowed() {
    const ctx = document.getElementById('plan-ctx');
    const plan = (ctx && ctx.dataset && ctx.dataset.plan) ? ctx.dataset.plan : 'free';
    return plan === 'team' || plan === 'enterprise';
}

async function downloadReport(analysisText) {
    if (!analysisText) {
        const lang = document.documentElement.lang || 'ar';
        const messages = {
            ar: 'لا توجد بيانات تحليل متاحة. يرجى إجراء تحليل أولاً.',
            en: 'No analysis data available. Please run an analysis first.',
            zh: '暂无分析数据。请先运行分析。',
            es: 'No hay datos de análisis disponibles. Ejecuta un análisis primero.'
        };
        showToast(messages[lang] || messages.ar, 'warning');
        return;
    }
    try {
        const title = 'Dockerfile Analysis Report';
        const extras = buildReportExtras();
        const beforeContent = (window.lastOriginalDockerfileBeforeFix || '').trim();
        const afterContent = (window.lastFixedDockerfile || '').trim();

        if (_isPdfPlanAllowed()) {
            try {
                const pdfResp = await fetch('/analyze/report_pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title,
                        analysis: analysisText,
                        stats: {},
                        extras,
                        before_dockerfile: beforeContent || '',
                        after_dockerfile: afterContent || ''
                    })
                });

                if (pdfResp.ok && (pdfResp.headers.get('Content-Type') || '').includes('application/pdf')) {
                    const blob = await pdfResp.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'dockerfile-report.pdf';
                    a.click();
                    URL.revokeObjectURL(url);
                    return;
                }
            } catch (pdfErr) {
                console.log('PDF endpoint not available, using HTML fallback');
            }
        }

        // Fallback: open HTML report in a new tab for viewing first
        // User can then download HTML / PDF / SARIF from buttons inside the report page
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/analyze/report';
        form.target = '_blank';
        const add = (name, value) => {
            const i = document.createElement('input');
            i.type = 'hidden';
            i.name = name;
            i.value = typeof value === 'string' ? value : JSON.stringify(value);
            form.appendChild(i);
        };
        // Add CSRF token for the regular form submission
        const csrfMeta = document.querySelector('meta[name="csrf-token"]");
        if (csrfMeta) {
            add('csrf_token', csrfMeta.getAttribute('content'));
        }

        add('title', title);
        add('analysis', analysisText);
        add('stats', {});
        add('extras', extras);
        // NO auto_print — report opens for review; download from within the page
        if (window.currentScanId) add('scan_id', window.currentScanId);
        document.body.appendChild(form);
        form.submit();
        form.remove();
    } catch (e) {
        const lang = document.documentElement.lang || 'ar';
        const messages = {
            ar: 'فشل تنزيل التقرير: ',
            en: 'Failed to download report: ',
            zh: '报告下载失败：',
            es: 'No se pudo descargar el informe: '
        };
        showToast((messages[lang] || messages.ar) + e.message, 'error');
    }
}

// Expose globally
window.downloadReport = downloadReport;

// View PDF inline in a new tab
async function viewReport(analysisText) {
    const title = 'Dockerfile Analysis Report';
    const extras = buildReportExtras();
    const beforeContent = (window.lastOriginalDockerfileBeforeFix || '').trim();
    const afterContent = (window.lastFixedDockerfile || '').trim();

    if (_isPdfPlanAllowed()) {
        try {
            const resp = await fetch('/analyze/report_pdf?inline=1', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title,
                    analysis: analysisText || '',
                    stats: {},
                    extras,
                    disposition: 'inline',
                    before_dockerfile: beforeContent || '',
                    after_dockerfile: afterContent || ''
                })
            });
            const ct = resp.headers.get('Content-Type') || '';
            if (resp.ok && ct.includes('application/pdf')) {
                const blob = await resp.blob();
                const url = URL.createObjectURL(blob);
                window.open(url, '_blank');
                return;
            }
        } catch (e) {
            // ignore and fallback
        }
    }

    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/analyze/report';
    form.target = '_blank';
    const add = (name, value) => {
        const i = document.createElement('input');
        i.type = 'hidden';
        i.name = name; i.value = typeof value === 'string' ? value : JSON.stringify(value);
        form.appendChild(i);
    };
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        add('csrf_token', csrfMeta.getAttribute('content'));
    }
    add('title', title);
    add('analysis', analysisText || '');
    add('stats', {});
    add('extras', extras);
    if (window.currentScanId) add('scan_id', window.currentScanId);
    document.body.appendChild(form);
    form.submit();
    form.remove();
}

window.viewReport = viewReport;

(function () {

    function getWorkspace() {
        return document.querySelector('[data-live-workspace]');
    }

    function parseI18n(workspace) {
        const script = workspace ? workspace.querySelector('[data-live-i18n]') : null;
        if (!script) return {};
        try {
            return JSON.parse(script.textContent || '{}');
        } catch (e) {
            return {};
        }
    }

    function LiveRuntimeUI(workspace) {
        this.workspace = workspace;
        this.feed = workspace.querySelector('[data-live-feed]');
        this.progress = workspace.querySelector('[data-live-progress]');
        this.status = workspace.querySelector('[data-live-status]');
        this.autoscroll = workspace.querySelector('[data-live-autoscroll]');
        this.runId = null;
        this.i18n = parseI18n(workspace);
        this.autoScrollEnabled = true;
        this.lastHeight = { top: 60, bottom: 40 };
        this._bind();
    }

    LiveRuntimeUI.prototype._bind = function () {
        const clearBtn = this.workspace.querySelector('[data-live-action="clear"]');
        const copyBtn = this.workspace.querySelector('[data-live-action="copy"]');
        const collapseBtn = this.workspace.querySelector('[data-live-action="collapse"]');
        const expandBtn = this.workspace.querySelector('[data-live-action="expand"]');
        const resizer = this.workspace.querySelector('[data-live-resizer]');
        const topPane = this.workspace.querySelector('.live-pane-top');
        const bottomPane = this.workspace.querySelector('.live-pane-bottom');
        const feedEl = this.feed;
        const self = this;

        if (clearBtn) {
            clearBtn.addEventListener('click', function () {
                self.clear();
            });
        }
        if (copyBtn) {
            copyBtn.addEventListener('click', function () {
                self.copy();
            });
        }
        if (collapseBtn) {
            collapseBtn.addEventListener('click', function () {
                self.setCollapsed(true);
            });
        }
        if (expandBtn) {
            expandBtn.addEventListener('click', function () {
                self.setCollapsed(false);
            });
        }
        if (feedEl) {
            feedEl.addEventListener('scroll', function () {
                if (!feedEl) return;
                const nearBottom = feedEl.scrollHeight - feedEl.scrollTop - feedEl.clientHeight < 10;
                self.autoScrollEnabled = nearBottom;
                self.updateAutoscroll();
            });
        }

        if (resizer && topPane && bottomPane) {
            let dragging = false;
            let startY = 0;
            let startTop = 0;
            let startBottom = 0;
            resizer.addEventListener('mousedown', function (e) {
                dragging = true;
                startY = e.clientY;
                startTop = topPane.getBoundingClientRect().height;
                startBottom = bottomPane.getBoundingClientRect().height;
                document.body.style.cursor = 'row-resize';
            });
            document.addEventListener('mousemove', function (e) {
                if (!dragging) return;
                const delta = e.clientY - startY;
                const total = startTop + startBottom;
                let newTop = startTop + delta;
                let newBottom = total - newTop;
                const minTop = total * 0.45;
                const maxTop = total * 0.75;
                if (newTop < minTop) newTop = minTop;
                if (newTop > maxTop) newTop = maxTop;
                newBottom = total - newTop;
                const topPct = (newTop / total) * 100;
                const bottomPct = (newBottom / total) * 100;
                topPane.style.flex = `0 0 ${topPct}%`;
                bottomPane.style.flex = `0 0 ${bottomPct}%`;
                self.lastHeight = { top: topPct, bottom: bottomPct };
            });
            document.addEventListener('mouseup', function () {
                if (dragging) {
                    dragging = false;
                    document.body.style.cursor = '';
                }
            });
        }
    };

    LiveRuntimeUI.prototype.setRunId = function (runId) {
        this.runId = runId;
    };

    LiveRuntimeUI.prototype.activate = function () {
        if (this.workspace) {
            this.workspace.classList.add('is-active');
        }
    };

    LiveRuntimeUI.prototype.updateAutoscroll = function () {
        if (!this.autoscroll) return;
        const on = this.i18n.autoscroll_on || 'Auto-scroll on';
        const off = this.i18n.autoscroll_off || 'Auto-scroll paused';
        this.autoscroll.textContent = this.autoScrollEnabled ? on : off;
    };

    LiveRuntimeUI.prototype.setStatus = function (text) {
        if (this.status) this.status.textContent = text || '';
    };

    LiveRuntimeUI.prototype.setProgress = function (value) {
        if (!this.progress) return;
        const pct = Math.max(0, Math.min(100, Number(value || 0)));
        this.progress.style.width = `${pct}%`;
    };

    LiveRuntimeUI.prototype.clear = function () {
        if (this.feed) this.feed.innerHTML = '';
        this.setProgress(0);
        this.setStatus('');
        this.autoScrollEnabled = true;
        this.updateAutoscroll();
    };

    LiveRuntimeUI.prototype.copy = function () {
        const lines = [];
        if (!this.feed) return;
        this.feed.querySelectorAll('[data-live-event-line]').forEach(function (node) {
            lines.push(node.textContent || '');
        });
        const text = lines.join('\n').trim();
        if (!text) return;
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text);
            return;
        }
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    };

    LiveRuntimeUI.prototype.setCollapsed = function (collapsed) {
        if (!this.workspace) return;
        if (collapsed) {
            this.workspace.classList.add('is-collapsed');
        } else {
            this.workspace.classList.remove('is-collapsed');
            const topPane = this.workspace.querySelector('.live-pane-top');
            const bottomPane = this.workspace.querySelector('.live-pane-bottom');
            if (topPane && bottomPane && this.lastHeight) {
                topPane.style.flex = `0 0 ${this.lastHeight.top}%`;
                bottomPane.style.flex = `0 0 ${this.lastHeight.bottom}%`;
            }
        }
    };

    LiveRuntimeUI.prototype.addEvent = function (evt) {
        if (!this.feed || !evt) return;
        const stepLabels = (this.i18n.steps || {});
        const statusLabels = (this.i18n.status || {});
        const title = stepLabels[evt.step] || evt.step || '';
        const message = evt.message || (this.i18n.messages && this.i18n.messages[evt.step]) || '';
        const statusText = statusLabels[evt.status] || evt.status || '';
        const ts = evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : '';
        const wrapper = document.createElement('div');
        wrapper.className = `live-event status-${evt.status || 'pending'}`;
        const metaHtml = `
            <div class="live-event-meta">
                <div>${ts}</div>
                <div class="live-event-status"><span class="live-status-dot"></span>${statusText}</div>
            </div>
        `;
        const metaText = evt.meta ? ` • ${JSON.stringify(evt.meta)}` : '';
        const bodyHtml = `
            <div>
                <div class="live-event-title">${title}</div>
                <div class="live-event-message" data-live-event-line>${message}${metaText}</div>
            </div>
        `;
        wrapper.innerHTML = metaHtml + bodyHtml;
        this.feed.appendChild(wrapper);
        if (typeof evt.progress !== 'undefined') {
            this.setProgress(evt.progress);
        }
        if (this.autoScrollEnabled) {
            this.feed.scrollTop = this.feed.scrollHeight;
        }
    };

    function getUI() {
        const workspace = getWorkspace();
        if (!workspace) return null;
        if (!workspace._liveRuntimeUI) {
            workspace._liveRuntimeUI = new LiveRuntimeUI(workspace);
        }
        return workspace._liveRuntimeUI;
    }

    async function startLive(opts) {
        const ui = getUI();
        if (ui) {
            ui.activate();
            ui.clear();
            ui.updateAutoscroll();
            ui.setStatus('');
        }
        async function startJobFallback() {
            const formData = new FormData();
            formData.append('fileContent', String(opts.content || ''));
            formData.append('async', 'true');
            if (opts.filename) formData.append('filename', String(opts.filename));
            if (opts.vuln_ctx) formData.append('vulnerability_context', JSON.stringify(opts.vuln_ctx));
            if (opts.sbom_ctx) formData.append('sbom_context', JSON.stringify(opts.sbom_ctx));
            if (opts.ci_ctx) formData.append('ci_context', String(opts.ci_ctx));
            if (opts.runtime_ctx) formData.append('runtime_context', String(opts.runtime_ctx));

            const headers = {};
            if (opts.gemini_key) {
                headers['X-Gemini-Key'] = String(opts.gemini_key);
            }

            const resp = await fetch('/analyze/', {
                method: 'POST',
                headers,
                body: formData
            });
            const data = await resp.json().catch(function () { return {}; });
            if (!resp.ok) {
                const err = new Error(data.error || 'Failed to start');
                err.status = resp.status;
                throw err;
            }
            return { mode: 'job', runId: data.job_id || data.run_id };
        }

        if (ui) {
            ui.addEvent({ step: 'analysis_start', status: 'running', message: 'Starting analysis job...', timestamp: new Date().toISOString() });
        }
        try {
            const started = await startJobFallback();
            if (ui) ui.setRunId(started.runId);
            return await waitForResult(started.runId, ui, started.mode);
        } catch (err) {
            if (ui) {
                ui.addEvent({ step: 'analysis_complete', status: 'error', message: err.message || 'Failed to start', timestamp: new Date().toISOString() });
                ui.setStatus(err.message || '');
            }
            throw err;
        }
    }

    async function waitForResult(runId, ui, mode) {
        if (mode === 'job') {
            let delayMs = 2500;
            while (true) {
                const resp = await fetch(`/analyze/job/${encodeURIComponent(runId)}`);
                const data = await resp.json().catch(function () { return {}; });
                if (!resp.ok) {
                    if (resp.status === 429) {
                        delayMs = Math.min(delayMs * 2, 10000);
                        if (ui) {
                            ui.addEvent({
                                id: Date.now(),
                                step: 'analysis_progress',
                                status: 'running',
                                message: 'Waiting for analysis status window...',
                                timestamp: new Date().toISOString()
                            });
                        }
                        await new Promise(function (r) { setTimeout(r, delayMs); });
                        continue;
                    }
                    const err = new Error(data.error || 'Analysis job unavailable');
                    err.status = resp.status;
                    throw err;
                }

                delayMs = 2500;
                const status = String(data.status || '').toLowerCase();
                if (ui) {
                    ui.addEvent({
                        id: Date.now(),
                        step: 'analysis_progress',
                        status: status === 'done' ? 'success' : (status === 'failed' ? 'error' : 'running'),
                        message: status === 'done'
                            ? 'Analysis completed'
                            : (status === 'failed' ? (data.error || 'Analysis failed') : 'Analysis in progress...'),
                        timestamp: new Date().toISOString()
                    });
                }

                if (status === 'done') {
                    return data.result || {};
                }
                if (status === 'failed' || status === 'cancelled') {
                    const err = new Error(data.error || 'Analysis failed');
                    err.status = 500;
                    throw err;
                }
                await new Promise(function (r) { setTimeout(r, delayMs); });
            }
        }

        let lastId = 0;
        let stopped = false;
        let source = null;

        function handleEvent(evt) {
            if (!evt) return;
            lastId = Math.max(lastId, Number(evt.id || 0));
            if (ui) ui.addEvent(evt);
            if (evt.status === 'error') {
                if (ui) ui.setStatus(evt.message || '');
            }
        }

        function startSse() {
            if (!window.EventSource) return false;
            try {
                source = new EventSource(`/analyze/live/stream?run_id=${encodeURIComponent(runId)}`);
                source.onmessage = function (e) {
                    try {
                        const evt = JSON.parse(e.data || '{}');
                        handleEvent(evt);
                    } catch (_) {
                    }
                };
                source.onerror = function () {
                    if (source) {
                        source.close();
                        source = null;
                    }
                };
                return true;
            } catch (e) {
                return false;
            }
        }

        function stopSse() {
            if (source) {
                source.close();
                source = null;
            }
        }

        async function pollEvents() {
            while (!stopped) {
                const resp = await fetch(`/analyze/live/poll?run_id=${encodeURIComponent(runId)}&last_id=${lastId}`);
                if (!resp.ok) {
                    await new Promise(r => setTimeout(r, 1200));
                    continue;
                }
                const data = await resp.json().catch(function () { return {}; });
                const events = Array.isArray(data.events) ? data.events : [];
                events.forEach(handleEvent);
                if (data.status && data.status !== 'running') {
                    break;
                }
                await new Promise(r => setTimeout(r, 900));
            }
        }

        async function pollResult() {
            while (!stopped) {
                const resp = await fetch(`/analyze/live/result?run_id=${encodeURIComponent(runId)}`);
                if (!resp.ok) {
                    const errorPayload = await resp.json().catch(function () { return {}; });
                    const err = new Error(errorPayload.error || 'Live result unavailable');
                    err.status = resp.status;
                    throw err;
                }
                const data = await resp.json().catch(function () { return {}; });
                if (data.status === 'done') {
                    stopped = true;
                    stopSse();
                    return data.result || {};
                }
                if (data.status === 'failed' || data.status === 'cancelled') {
                    stopped = true;
                    stopSse();
                    const err = new Error(data.error || 'Analysis failed');
                    err.status = 500;
                    throw err;
                }
                await new Promise(r => setTimeout(r, 1000));
            }
            return {};
        }

        const sseStarted = startSse();
        if (!sseStarted) {
            pollEvents();
        }
        return pollResult();
    }

    function stopLive(runId) {
        if (!runId) return;
        fetch('/analyze/live/stop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ run_id: runId })
        }).catch(function () {});
    }

    window.LiveRuntime = {
        start: startLive,
        stop: stopLive,
        ui: getUI
    };

    window.addEventListener('beforeunload', function () {
        const ui = getUI();
        if (ui && ui.runId) {
            const payload = JSON.stringify({ run_id: ui.runId });
            if (navigator.sendBeacon) {
                const blob = new Blob([payload], { type: 'application/json' });
                navigator.sendBeacon('/analyze/live/stop', blob);
            } else {
                stopLive(ui.runId);
            }
        }
    });
})();


