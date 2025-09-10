/**
 * Power menu module
 * Handles power button functionality and power actions
 */

export class PowerManager {
    constructor() {
        this.powerMenuOpen = false;
    }

    /**
     * Toggle power menu visibility
     */
    togglePowerMenu() {
        const overlay = document.getElementById('power-menu-overlay');
        this.powerMenuOpen = !this.powerMenuOpen;
        
        if (this.powerMenuOpen) {
            overlay.classList.add('show');
            document.addEventListener('click', this.closePowerMenuOnOutsideClick.bind(this));
            document.addEventListener('keydown', this.closePowerMenuOnEscape.bind(this));
        } else {
            overlay.classList.remove('show');
            document.removeEventListener('click', this.closePowerMenuOnOutsideClick.bind(this));
            document.removeEventListener('keydown', this.closePowerMenuOnEscape.bind(this));
        }
    }

    /**
     * Close power menu
     */
    closePowerMenu() {
        const overlay = document.getElementById('power-menu-overlay');
        overlay.classList.remove('show');
        this.powerMenuOpen = false;
        document.removeEventListener('click', this.closePowerMenuOnOutsideClick.bind(this));
        document.removeEventListener('keydown', this.closePowerMenuOnEscape.bind(this));
    }

    /**
     * Close power menu when clicking outside
     */
    closePowerMenuOnOutsideClick(event) {
        const powerMenu = document.querySelector('.power-menu');
        if (!powerMenu.contains(event.target)) {
            this.closePowerMenu();
        }
    }

    /**
     * Close power menu on escape key
     */
    closePowerMenuOnEscape(event) {
        if (event.key === 'Escape') {
            this.closePowerMenu();
        }
    }

    /**
     * Handle power actions
     * @param {string} action - 'poweroff', 'shutdown', or 'logout'
     */
    handlePowerAction(action) {
        // Close the menu first
        this.closePowerMenu();
        
        // Handle the power action
        switch(action) {
            case 'poweroff':
                alert('Power Off action triggered');
                // Add your power off logic here
                break;
            case 'shutdown':
                alert('Shutdown action triggered');
                // Add your shutdown logic here
                break;
            case 'logout':
                alert('Logout action triggered');
                // Add your logout logic here
                break;
            default:
                console.log('Unknown power action:', action);
        }
    }
}

// Global functions for backward compatibility
window.powerButton = function() {
    if (window.powerManager) {
        window.powerManager.togglePowerMenu();
    }
};

window.handlePowerAction = function(action) {
    if (window.powerManager) {
        window.powerManager.handlePowerAction(action);
    }
};
