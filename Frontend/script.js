/**
 * LANCAM Frontend - Main Entry Point
 */

import { LancamApp } from './js/app.js';

// Initialize application when DOM is ready
function initializeApp() {
    const app = new LancamApp();
    app.initialize();
    
    // Store globally for external access
    window.lancamApp = app;
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        app.cleanup();
    });
}

// Start initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
