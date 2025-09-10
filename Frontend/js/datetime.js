/**
 * Date and Time module
 * Handles date/time display and updates
 */

export class DateTimeManager {
    constructor() {
        this.interval = null;
    }

    /**
     * Start the date/time updates
     */
    start() {
        this.updateDateTime();
        this.interval = setInterval(() => this.updateDateTime(), 1000);
    }

    /**
     * Stop the date/time updates
     */
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    /**
     * Update the date and time display
     */
    updateDateTime() {
        const now = new Date();
        
        // Format date as DD/MM/YYYY
        const day = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const year = now.getFullYear();
        const dateString = `${day}/${month}/${year}`;
        
        // Format time as HH:MM AM/PM
        let hours = now.getHours();
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // 0 should be 12
        const timeString = `${String(hours).padStart(2, '0')}:${minutes} ${ampm}`;
        
        // Update the DOM elements
        const dateElement = document.getElementById('current-date');
        const timeElement = document.getElementById('current-time');
        
        if (dateElement) dateElement.textContent = dateString;
        if (timeElement) timeElement.textContent = timeString;
    }
}
