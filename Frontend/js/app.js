/**
 * Main application module
 * Coordinates all other modules and handles initialization
 */

import { themeManager } from './theme.js';
import { ComponentLoader } from './components.js';
import { DateTimeManager } from './datetime.js';
import { PowerManager } from './power.js';
import { CameraManager } from './camera.js';
import { UIControls } from './ui-controls.js';

class LancamApp {
    constructor() {
        this.themeManager = themeManager;
        this.dateTimeManager = new DateTimeManager();
        this.powerManager = new PowerManager();
        this.cameraManager = new CameraManager();
        
        // Make theme manager globally available
        window.themeManager = this.themeManager;
    }

    /**
     * Initialize the application
     */
    async initialize() {
        try {
            // Load components first
            await ComponentLoader.loadAll();
            
            // Wait for components to be fully loaded
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Initialize modules in sequence
            this.themeManager.initialize();
            
            // Rebuild theme dropdown after components are ready
            setTimeout(() => {
                if (this.themeManager) {
                    this.themeManager.buildThemeDropdown();
                }
            }, 200);
            
            // Initialize camera and UI controls
            await this.cameraManager.initialize();
            UIControls.initialize();
            
            // Start date/time updates
            setTimeout(() => {
                this.dateTimeManager.start();
            }, 300);
            
            // Make managers globally available
            window.themeManager = this.themeManager;
            window.powerManager = this.powerManager;
            window.cameraManager = this.cameraManager;
            
        } catch (error) {
            console.error('Failed to initialize LANCAM application:', error);
        }
    }

    /**
     * Cleanup when the application is unloaded
     */
    cleanup() {
        this.dateTimeManager.stop();
    }
}

export { LancamApp };
