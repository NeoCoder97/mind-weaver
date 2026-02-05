/**
 * MindWeaver Form Handler
 * Provides utilities for form handling and modals
 */

const Forms = {
    /**
     * Show a modal with form content
     */
    showModal(content, options = {}) {
        const {
            title = '',
            size = 'md',
            footer = null,
            onClose = null
        } = options;

        const modalHTML = `
            <div class="modal-overlay" id="active-modal">
                <div class="modal modal-${size}">
                    ${title ? `
                    <div class="modal-header">
                        <h2 class="modal-title">${title}</h2>
                        <button class="modal-close" data-close-modal>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                            </svg>
                        </button>
                    </div>
                    ` : ''}
                    <div class="modal-body">
                        ${content}
                    </div>
                    ${footer ? `
                    <div class="modal-footer">
                        ${footer}
                    </div>
                    ` : ''}
                </div>
            </div>
        `;

        const container = document.getElementById('modal-container');
        container.innerHTML = modalHTML;

        const modal = container.querySelector('#active-modal');

        // Add close handlers
        const closeHandler = () => {
            modal.remove();
            if (onClose) onClose();
        };

        modal.querySelector('[data-close-modal]')?.addEventListener('click', closeHandler);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeHandler();
        });

        // Handle Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                closeHandler();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);

        return modal;
    },

    /**
     * Close active modal
     */
    closeModal() {
        const modal = document.querySelector('#active-modal');
        if (modal) {
            modal.remove();
        }
    },

    /**
     * Show a confirm dialog
     */
    confirm(message, options = {}) {
        const {
            title = '确认',
            confirmText = '确认',
            cancelText = '取消',
            onConfirm = null,
            onCancel = null
        } = options;

        const content = `
            <p>${message}</p>
        `;

        const footer = `
            <button class="btn btn-secondary" data-cancel>${cancelText}</button>
            <button class="btn btn-danger" data-confirm>${confirmText}</button>
        `;

        const modal = this.showModal(content, { title, footer });

        modal.querySelector('[data-confirm]')?.addEventListener('click', () => {
            modal.remove();
            if (onConfirm) onConfirm();
        });

        modal.querySelector('[data-cancel]')?.addEventListener('click', () => {
            modal.remove();
            if (onCancel) onCancel();
        });
    },

    /**
     * Show an alert dialog
     */
    alert(message, options = {}) {
        const {
            title = '提示',
            type = 'info'
        } = options;

        const content = `
            <p>${message}</p>
        `;

        const footer = `
            <button class="btn btn-primary" data-close>确定</button>
        `;

        const modal = this.showModal(content, { title, footer });

        modal.querySelector('[data-close]')?.addEventListener('click', () => {
            modal.remove();
        });
    },

    /**
     * Validate form
     */
    validate(form) {
        const errors = [];
        const data = {};

        // Get all form inputs
        const inputs = form.querySelectorAll('input, select, textarea');

        inputs.forEach(input => {
            const name = input.name;
            const value = input.value.trim();
            const required = input.hasAttribute('required');
            const type = input.type;

            // Skip unchecked checkboxes
            if (type === 'checkbox' && !input.checked) {
                return;
            }

            // Required validation
            if (required && !value) {
                errors.push(`${input.previousElementSibling?.textContent || name} 是必填项`);
                return;
            }

            // Email validation
            if (type === 'email' && value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    errors.push('请输入有效的邮箱地址');
                    return;
                }
            }

            // URL validation
            if (type === 'url' && value) {
                try {
                    new URL(value);
                } catch {
                    errors.push('请输入有效的URL');
                    return;
                }
            }

            // Store value
            if (type === 'checkbox') {
                data[name] = input.checked;
            } else if (type === 'number') {
                data[name] = value ? parseFloat(value) : null;
            } else {
                data[name] = value;
            }
        });

        return {
            valid: errors.length === 0,
            errors,
            data
        };
    },

    /**
     * Collect form data
     */
    getFormData(form) {
        const data = {};
        const formData = new FormData(form);

        for (const [key, value] of formData.entries()) {
            // Check if key already exists (for checkboxes)
            if (data[key] !== undefined) {
                if (!Array.isArray(data[key])) {
                    data[key] = [data[key]];
                }
                data[key].push(value);
            } else {
                data[key] = value;
            }
        }

        // Handle checkboxes
        form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            if (!checkbox.name) return;
            if (!formData.has(checkbox.name)) {
                data[checkbox.name] = false;
            }
        });

        return data;
    },

    /**
     * Populate form with data
     */
    populateForm(form, data) {
        Object.entries(data).forEach(([key, value]) => {
            const input = form.querySelector(`[name="${key}"]`);
            if (!input) return;

            const type = input.type;

            if (type === 'checkbox') {
                input.checked = Boolean(value);
            } else if (type === 'radio') {
                if (input.value === String(value)) {
                    input.checked = true;
                }
            } else {
                input.value = value || '';
            }
        });
    },

    /**
     * Reset form
     */
    resetForm(form) {
        form.reset();
        // Clear custom error styles
        form.querySelectorAll('.error')?.forEach(el => {
            el.classList.remove('error');
        });
        form.querySelectorAll('.error-message')?.forEach(el => {
            el.remove();
        });
    },

    /**
     * Show field error
     */
    showFieldError(input, message) {
        input.classList.add('error');

        let errorEl = input.nextElementSibling;
        if (!errorEl || !errorEl.classList.contains('error-message')) {
            errorEl = document.createElement('div');
            errorEl.className = 'error-message';
            input.parentNode.insertBefore(errorEl, input.nextSibling);
        }
        errorEl.textContent = message;
    },

    /**
     * Clear field error
     */
    clearFieldError(input) {
        input.classList.remove('error');
        const errorEl = input.nextElementSibling;
        if (errorEl && errorEl.classList.contains('error-message')) {
            errorEl.remove();
        }
    },

    /**
     * Handle form submission
     */
    async handleSubmit(form, url, method = 'POST', options = {}) {
        const {
            onSuccess = null,
            onError = null,
            onSuccessMessage = '操作成功',
            onErrorMessage = '操作失败'
        } = options;

        // Validate form
        const validation = this.validate(form);
        if (!validation.valid) {
            validation.errors.forEach(error => {
                Toast.error(error);
            });
            return false;
        }

        // Get form data
        const data = this.getFormData(form);

        // Disable submit button
        const submitBtn = form.querySelector('[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.dataset.originalText = submitBtn.textContent;
            submitBtn.textContent = '提交中...';
        }

        try {
            // Make API request
            let response;
            switch (method.toUpperCase()) {
                case 'POST':
                    response = await API.post(url, data);
                    break;
                case 'PUT':
                    response = await API.put(url, data);
                    break;
                case 'PATCH':
                    response = await API.patch(url, data);
                    break;
                default:
                    throw new Error(`Unsupported method: ${method}`);
            }

            if (response.success) {
                if (onSuccessMessage) {
                    Toast.success(onSuccessMessage);
                }
                this.closeModal();
                if (onSuccess) onSuccess(response);
                return true;
            } else {
                Toast.error(response.error || onErrorMessage);
                if (onError) onError(response);
                return false;
            }
        } catch (error) {
            Toast.error(onErrorMessage);
            if (onError) onError(error);
            return false;
        } finally {
            // Re-enable submit button
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = submitBtn.dataset.originalText || '提交';
            }
        }
    }
};

// Toast notification system
const Toast = {
    show(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icon = this.getIcon(type);

        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
            </button>
        `;

        container.appendChild(toast);

        // Auto remove
        const timeout = setTimeout(() => {
            toast.remove();
        }, duration);

        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            clearTimeout(timeout);
            toast.remove();
        });

        return toast;
    },

    success(message, duration) {
        return this.show(message, 'success', duration);
    },

    error(message, duration) {
        return this.show(message, 'error', duration);
    },

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    },

    info(message, duration) {
        return this.show(message, 'info', duration);
    },

    getIcon(type) {
        const icons = {
            success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
            error: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>',
            warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
            info: '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>'
        };
        return icons[type] || icons.info;
    }
};

// Make available globally
window.Forms = Forms;
window.Toast = Toast;
