/**
 * MindWeaver Keyboard Shortcuts
 * Provides keyboard shortcuts for common actions
 */

const Keyboard = {
    shortcuts: {},
    enabled: true,

    /**
     * Register a keyboard shortcut
     */
    register(key, handler, description = '') {
        this.shortcuts[key] = { handler, description };
    },

    /**
     * Unregister a keyboard shortcut
     */
    unregister(key) {
        delete this.shortcuts[key];
    },

    /**
     * Handle key press
     */
    handleKeyPress(event) {
        if (!this.enabled) return;

        // Ignore if user is typing in an input field
        const tag = event.target.tagName.toLowerCase();
        if (tag === 'input' || tag === 'textarea' || tag === 'select') {
            return;
        }

        // Build key string
        let key = '';
        if (event.ctrlKey) key += 'Ctrl+';
        if (event.altKey) key += 'Alt+';
        if (event.shiftKey) key += 'Shift+';
        if (event.metaKey) key += 'Meta+';

        // Special keys
        if (event.key === 'Escape') {
            key += 'Escape';
        } else if (event.key === 'Enter') {
            key += 'Enter';
        } else if (event.key === 'Delete') {
            key += 'Delete';
        } else if (event.key === 'Backspace') {
            key += 'Backspace';
        } else if (event.key === ' ') {
            key += 'Space';
        } else if (event.key.startsWith('Arrow')) {
            key += event.key.replace('Arrow', '');
        } else {
            // Single character
            key += event.key.toLowerCase();
        }

        // Check if we have a handler for this key
        if (this.shortcuts[key]) {
            event.preventDefault();
            this.shortcuts[key].handler(event);
        }
    },

    /**
     * Enable keyboard shortcuts
     */
    enable() {
        this.enabled = true;
    },

    /**
     * Disable keyboard shortcuts
     */
    disable() {
        this.enabled = false;
    },

    /**
     * Initialize keyboard shortcuts
     */
    init() {
        document.addEventListener('keydown', this.handleKeyPress.bind(this));

        // Register default shortcuts
        this.register('Escape', () => {
            // Close modal if open
            const modal = document.querySelector('.modal-overlay');
            if (modal) {
                modal.remove();
            }
        }, 'Close modal');

        this.register('?', () => {
            // Show keyboard shortcuts help
            this.showHelp();
        }, 'Show keyboard shortcuts');
    },

    /**
     * Show keyboard shortcuts help
     */
    showHelp() {
        const shortcutsHTML = Object.entries(this.shortcuts)
            .map(([key, { description }]) => `
                <tr>
                    <td><kbd>${this.formatKey(key)}</kbd></td>
                    <td>${description}</td>
                </tr>
            `).join('');

        const helpHTML = `
            <div class="modal-overlay" id="keyboard-help-modal">
                <div class="modal modal-sm">
                    <div class="modal-header">
                        <h2 class="modal-title">键盘快捷键</h2>
                        <button class="modal-close" data-close-modal>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                            </svg>
                        </button>
                    </div>
                    <div class="modal-body">
                        <table class="data-table">
                            <tbody>
                                ${shortcutsHTML}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        const container = document.getElementById('modal-container');
        container.innerHTML = helpHTML;

        // Add close handlers
        container.querySelector('[data-close-modal]').addEventListener('click', () => {
            container.innerHTML = '';
        });

        container.querySelector('.modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                container.innerHTML = '';
            }
        });
    },

    /**
     * Format key for display
     */
    formatKey(key) {
        return key
            .replace('Ctrl', '⌃')
            .replace('Alt', '⌥')
            .replace('Shift', '⇧')
            .replace('Meta', '⌘')
            .replace('ArrowUp', '↑')
            .replace('ArrowDown', '↓')
            .replace('ArrowLeft', '←')
            .replace('ArrowRight', '→')
            .replace('Space', '␣');
    },

    /**
     * Get all shortcuts as formatted array
     */
    getShortcuts() {
        return Object.entries(this.shortcuts).map(([key, { description }]) => ({
            key: this.formatKey(key),
            description
        }));
    }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Keyboard.init());
} else {
    Keyboard.init();
}

// Make Keyboard available globally
window.Keyboard = Keyboard;
