/**
 * Simple Theme Management System
 * Handles switching between built-in themes
 */

import { THEME_CONFIG } from '../themes/theme-config.js';

export class ThemeManager {
    constructor() {
        this.currentTheme = 'dark';
        this.dropdownOpen = false;
        this.themes = { ...THEME_CONFIG };
    }

    /**
     * Initialize theme system on page load
     */
    initialize() {
        console.log('Initializing theme manager...');
        const savedTheme = localStorage.getItem('theme') || 'dark';
        this.setTheme(savedTheme);
        this.setupSystemThemeListener();
        
        // Try to build dropdown immediately if elements exist
        if (document.getElementById('theme-dropdown')) {
            this.buildThemeDropdown();
        } else {
            // If elements don't exist yet, wait and try again
            console.log('Theme dropdown element not found, will retry after DOM loads');
            setTimeout(() => {
                this.buildThemeDropdown();
            }, 500);
        }
    }

    /**
     * Build the theme dropdown with all built-in themes
     */
    buildThemeDropdown() {
        const dropdown = document.getElementById('theme-dropdown');
        const themeButton = document.getElementById('theme-button');
        
        if (!dropdown) {
            console.warn('Theme dropdown element not found');
            return;
        }

        console.log('Building theme dropdown...');

        // Clear existing content
        dropdown.innerHTML = '';

        // Create dropdown header
        const header = document.createElement('div');
        header.className = 'dropdown-header';
        header.innerHTML = `
            <span class="dropdown-title">Select Theme</span>
            <span class="dropdown-arrow">▼</span>
        `;
        dropdown.appendChild(header);

        // Create dropdown content
        const content = document.createElement('div');
        content.className = 'dropdown-content';
        
        // Add built-in themes
        Object.values(this.themes).forEach(theme => {
            if (theme.category === 'built-in') {
                const option = document.createElement('div');
                option.className = `theme-option ${theme.id === this.currentTheme ? 'active' : ''}`;
                option.dataset.themeId = theme.id;
                option.innerHTML = `
                    <div class="theme-preview" style="background: ${theme.variables['--bg-primary']}; border: 1px solid ${theme.variables['--border']}"></div>
                    <div class="theme-info">
                        <div class="theme-name">${theme.name}</div>
                        <div class="theme-description">${theme.description}</div>
                    </div>
                `;
                option.addEventListener('click', () => {
                    console.log('Switching to theme:', theme.id);
                    this.setTheme(theme.id);
                });
                content.appendChild(option);
            }
        });

        dropdown.appendChild(content);

        // Add dropdown toggle functionality to theme button
        if (themeButton) {
            // Remove any existing listeners to avoid duplicates
            themeButton.removeEventListener('click', this.themeButtonClickHandler);
            
            this.themeButtonClickHandler = (e) => {
                e.stopPropagation();
                console.log('Theme button clicked');
                this.toggleDropdown();
            };
            
            themeButton.addEventListener('click', this.themeButtonClickHandler);
            console.log('Theme button click handler attached');
        } else {
            console.warn('Theme button element not found');
        }
        
        // Add dropdown toggle functionality to header as well
        header.addEventListener('click', () => {
            console.log('Dropdown header clicked');
            this.toggleDropdown();
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target) && !themeButton?.contains(e.target)) {
                this.closeDropdown();
            }
        });

        console.log('Theme dropdown built successfully');
    }

    /**
     * Toggle dropdown open/closed
     */
    toggleDropdown() {
        const dropdown = document.getElementById('theme-dropdown');
        if (!dropdown) return;

        this.dropdownOpen = !this.dropdownOpen;
        dropdown.classList.toggle('open', this.dropdownOpen);
        
        const arrow = dropdown.querySelector('.dropdown-arrow');
        if (arrow) {
            arrow.textContent = this.dropdownOpen ? '▲' : '▼';
        }
    }

    /**
     * Close dropdown
     */
    closeDropdown() {
        const dropdown = document.getElementById('theme-dropdown');
        if (!dropdown) return;

        this.dropdownOpen = false;
        dropdown.classList.remove('open');
        
        const arrow = dropdown.querySelector('.dropdown-arrow');
        if (arrow) {
            arrow.textContent = '▼';
        }
    }

    /**
     * Set the current theme
     */
    setTheme(themeId) {
        if (!this.themes[themeId]) {
            console.warn('Theme not found:', themeId);
            return;
        }

        const theme = this.themes[themeId];
        this.currentTheme = themeId;

        console.log('Setting theme to:', themeId);

        // Apply theme variables to CSS
        const root = document.documentElement;
        Object.entries(theme.variables).forEach(([property, value]) => {
            root.style.setProperty(property, value);
        });

        // Update body theme attribute
        document.body.setAttribute('data-theme', themeId);

        // Save to localStorage
        localStorage.setItem('theme', themeId);

        // Update dropdown selection
        this.updateDropdownSelection();

        // Close dropdown after selection
        this.closeDropdown();

        console.log('Theme applied successfully:', themeId);
    }

    /**
     * Update dropdown selection visual state
     */
    updateDropdownSelection() {
        const dropdown = document.getElementById('theme-dropdown');
        if (!dropdown) return;

        const options = dropdown.querySelectorAll('.theme-option');
        options.forEach(option => {
            option.classList.toggle('active', option.dataset.themeId === this.currentTheme);
        });
    }

    /**
     * Setup system theme change listener
     */
    setupSystemThemeListener() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addListener((e) => {
                // Only auto-switch if user hasn't manually selected a theme
                const savedTheme = localStorage.getItem('theme');
                if (!savedTheme) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Get theme by ID
     */
    getTheme(themeId) {
        return this.themes[themeId];
    }

    /**
     * Get all available themes
     */
    getAllThemes() {
        return Object.values(this.themes);
    }

    /**
     * Get themes by category
     */
    getThemesByCategory(category) {
        return Object.values(this.themes).filter(theme => theme.category === category);
    }
}

// Create global instance
export const themeManager = new ThemeManager();

// Make available globally for backward compatibility
window.themeManager = themeManager;

// Global functions for backward compatibility
window.toggleDropdown = function() {
    if (window.themeManager) {
        window.themeManager.toggleDropdown();
    }
};

window.setTheme = function(themeId) {
    if (window.themeManager) {
        window.themeManager.setTheme(themeId);
    }
};