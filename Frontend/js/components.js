/**
 * Component loader module
 * Handles loading of HTML components (navbar, footer, etc.)
 */

export class ComponentLoader {
    /**
     * Load navbar component
     */
    static async loadNavbar() {
        try {
            const response = await fetch('./components/navbar.html');
            const navbarHTML = await response.text();
            const container = document.getElementById('navbar');
            if (container) {
                container.innerHTML = navbarHTML;
            }
        } catch (error) {
            console.error('Error loading navbar component:', error);
        }
    }

    /**
     * Load footer component
     */
    static async loadFooter() {
        try {
            const response = await fetch('./components/footer.html');
            const footerHTML = await response.text();
            const footer = document.getElementById('footer');
            if (footer) {
                footer.innerHTML = footerHTML;
            }
        } catch (error) {
            console.error('Error loading footer component:', error);
        }
    }

    /**
     * Load all components
     */
    static async loadAll() {
        await Promise.all([
            this.loadNavbar(),
            this.loadFooter()
        ]);
    }
}
