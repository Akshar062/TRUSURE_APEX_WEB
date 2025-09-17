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
    // Define routes
    const routes = {
        "/": "home",
        "/home": "home",
        "/scan": "scan",
        "/result": "result",
        "/compare": "compare",
        "/certificates": "certificates",
        "/history": "history",
        "/settings": "settings",
        "/help": "help"
    };

    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();

            const tab = this.getAttribute('data-tab');
            const route = routes[`/${tab}`] || tab;

            // ✅ Prevent reload if already on same route
            if (UIControls.currentRoute === route) {
                console.log("Already on the same route:", route);
                return;
            }

            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));

            // Add active class to clicked item
            this.classList.add('active');

            console.log('Navigating to:', route);

            // Navigate to the page
            UIControls.navigateToPage(route);
        });
    });
}


    /**
     * Navigate to different pages based on route
     * @param {string} route - The route to navigate to
     */
  
    static async navigateToPage(route) {
    // Save the current route
    UIControls.currentRoute = route;

    const mainContent = document.querySelector('.sidebar').parentElement;

    // Hide all core sections initially
    const sections = ['.sidebar', '.camera-area', '.controls-panel', '.wake-area'];
    sections.forEach(sel => {
        const el = document.querySelector(sel);
        if (el) el.style.display = 'none';
    });

    // Hide all dynamic containers (result, scan, etc.)
    document.querySelectorAll('.page-container').forEach(container => {
        container.style.display = 'none';
    });

    if (route === 'home') {
        // Show main layout again
        sections.forEach(sel => {
            const el = document.querySelector(sel);
            if (el) el.style.display = 'block';
        });
        return;
    }

    try {
        const response = await fetch(`./components/${route}.html`);
        const resultHTML = await response.text();

        let container = document.getElementById(route);
        if (!container) {
            container = document.createElement('div');
            container.id = route;
            container.classList.add('page-container');
            mainContent.appendChild(container);
        }

        const parser = new DOMParser();
        const doc = parser.parseFromString(resultHTML, 'text/html');
        const bodyContent = doc.querySelector(`#${route}`);

        container.innerHTML = bodyContent ? bodyContent.outerHTML : resultHTML;
        container.style.display = 'flex';

    } catch (error) {
        console.error(`Error loading ${route} page:`, error);
    }
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

     /**      * Handle Super Image toggle functionality
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
