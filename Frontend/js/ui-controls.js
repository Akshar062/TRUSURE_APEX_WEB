/**
 * UI Controls module
 * Handles various UI interactions and controls
 */

export class UIControls {
    /**
     * Initialize UI controls
     */
    static initialize() {
        this.setupNavigationTabs();
        this.setupControlButtons();
        this.setupToggleSwitches();
    }

    /**
     * Set up navigation tab functionality
     */
    static setupNavigationTabs() {
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Remove active class from all items
                navItems.forEach(nav => nav.classList.remove('active'));
                
                // Add active class to clicked item
                this.classList.add('active');
                
                // Navigation logic
                const tab = this.getAttribute('data-tab');
                console.log('Navigating to:', tab);
            });
        });
    }

    /**
     * Set up control buttons (light, scan, etc.)
     */
    static setupControlButtons() {
        // Light button toggle
        const lightBtn = document.querySelector('.light-btn');
        if (lightBtn) {
            lightBtn.addEventListener('click', function() {
                if (this.textContent === 'Turn On Light') {
                    this.textContent = 'Turn Off Light';
                    this.style.background = '#4CAF50';
                } else {
                    this.textContent = 'Turn On Light';
                    this.style.background = '#333';
                }
            });
        }

        // Scan button toggle
        const scanBtn = document.querySelector('.scan-btn');
        if (scanBtn) {
            scanBtn.addEventListener('click', function() {
                if (this.textContent === 'Scan Bangles') {
                    this.textContent = 'Stop Scanning';
                    this.style.background = '#4CAF50';
                    
                    // Ensure camera is active for scanning
                    if (window.cameraManager && !window.cameraManager.cameraActive) {
                        window.cameraManager.wakeCamera();
                    }
                    
                    console.log('Started scanning bangles');
                } else {
                    this.textContent = 'Scan Bangles';
                    this.style.background = '#333';
                    console.log('Stopped scanning bangles');
                }
            });
        }
    }

    /**
     * Set up toggle switches
     */
    static setupToggleSwitches() {
        // Toggle switch functionality is handled by the global toggleSwitch function
        // This could be refactored to be more modular if needed
    }

    /**
     * Toggle switch functionality
     * @param {HTMLElement} element - The toggle switch element
     */
    static toggleSwitch(element) {
        element.classList.toggle('active');
        
        // Get the label to know which toggle was clicked
        const label = element.parentElement.querySelector('label').textContent;
        const isActive = element.classList.contains('active');
        
        // Log the state change
        console.log(`${label} is now ${isActive ? 'ON' : 'OFF'}`);
        
        // Handle specific functionality for each toggle
        if (label === 'Super Image') {
            this.handleSuperImageToggle(isActive);
        } else if (label === 'Auto Marking') {
            this.handleAutoMarkingToggle(isActive);
        }
    }

    /**
     * Handle Super Image toggle functionality
     * @param {boolean} isOn - Whether the toggle is on
     */
    static handleSuperImageToggle(isOn) {
        if (isOn) {
            console.log('Super Image feature enabled');
            // Add your Super Image logic here
        } else {
            console.log('Super Image feature disabled');
            // Add your Super Image disable logic here
        }
    }

    /**
     * Handle Auto Marking toggle functionality
     * @param {boolean} isOn - Whether the toggle is on
     */
    static handleAutoMarkingToggle(isOn) {
        if (isOn) {
            console.log('Auto Marking feature enabled');
            // Add your Auto Marking logic here
        } else {
            console.log('Auto Marking feature disabled');
            // Add your Auto Marking disable logic here
        }
    }
}

// Global function for backward compatibility
window.toggleSwitch = function(element) {
    UIControls.toggleSwitch(element);
};
