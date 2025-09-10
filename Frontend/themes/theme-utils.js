/**
 * Theme Utilities
 * Helper functions for theme management and creation
 */

export class ThemeUtils {
    /**
     * Convert hex color to RGB
     */
    static hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    /**
     * Convert RGB to hex
     */
    static rgbToHex(r, g, b) {
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }

    /**
     * Calculate color luminance
     */
    static getLuminance(hex) {
        const rgb = this.hexToRgb(hex);
        if (!rgb) return 0;

        const { r, g, b } = rgb;
        const rsRGB = r / 255;
        const gsRGB = g / 255;
        const bsRGB = b / 255;

        const rLin = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
        const gLin = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
        const bLin = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4);

        return 0.2126 * rLin + 0.7152 * gLin + 0.0722 * bLin;
    }

    /**
     * Calculate contrast ratio between two colors
     */
    static getContrastRatio(color1, color2) {
        const lum1 = this.getLuminance(color1);
        const lum2 = this.getLuminance(color2);
        const brightest = Math.max(lum1, lum2);
        const darkest = Math.min(lum1, lum2);
        return (brightest + 0.05) / (darkest + 0.05);
    }

    /**
     * Check if color combination meets accessibility standards
     */
    static isAccessible(backgroundColor, textColor, level = 'AA') {
        const ratio = this.getContrastRatio(backgroundColor, textColor);
        const thresholds = {
            'AA': 4.5,
            'AAA': 7,
            'AA-large': 3,
            'AAA-large': 4.5
        };
        return ratio >= thresholds[level];
    }

    /**
     * Generate a color palette from a base color
     */
    static generatePalette(baseColor, steps = 5) {
        const rgb = this.hexToRgb(baseColor);
        if (!rgb) return [];

        const palette = [];
        const { r, g, b } = rgb;

        for (let i = 0; i < steps; i++) {
            const factor = (i / (steps - 1)) * 0.8 + 0.1; // 0.1 to 0.9
            const newR = Math.round(r * factor);
            const newG = Math.round(g * factor);
            const newB = Math.round(b * factor);
            palette.push(this.rgbToHex(newR, newG, newB));
        }

        return palette;
    }

    /**
     * Lighten a color by a percentage
     */
    static lighten(hex, percent) {
        const rgb = this.hexToRgb(hex);
        if (!rgb) return hex;

        const factor = 1 + (percent / 100);
        const r = Math.min(255, Math.round(rgb.r * factor));
        const g = Math.min(255, Math.round(rgb.g * factor));
        const b = Math.min(255, Math.round(rgb.b * factor));

        return this.rgbToHex(r, g, b);
    }

    /**
     * Darken a color by a percentage
     */
    static darken(hex, percent) {
        const rgb = this.hexToRgb(hex);
        if (!rgb) return hex;

        const factor = 1 - (percent / 100);
        const r = Math.max(0, Math.round(rgb.r * factor));
        const g = Math.max(0, Math.round(rgb.g * factor));
        const b = Math.max(0, Math.round(rgb.b * factor));

        return this.rgbToHex(r, g, b);
    }

    /**
     * Create a theme from a base color
     */
    static createThemeFromColor(baseColor, themeName, isDark = true) {
        const palette = this.generatePalette(baseColor, 7);
        
        if (isDark) {
            return {
                id: themeName.toLowerCase().replace(/[^a-zA-Z0-9]/g, '-'),
                name: themeName,
                description: `Custom dark theme based on ${baseColor}`,
                category: 'custom',
                icon: 'custom-icon',
                variables: {
                    '--bg-primary': palette[0],
                    '--bg-secondary': palette[1],
                    '--bg-tertiary': palette[2],
                    '--bg-quaternary': palette[3],
                    '--text-primary': '#ffffff',
                    '--text-secondary': '#cccccc',
                    '--text-tertiary': '#999999',
                    '--accent': baseColor,
                    '--accent-hover': this.darken(baseColor, 20),
                    '--accent-light': this.lighten(baseColor, 20),
                    '--border': palette[2],
                    '--border-light': palette[3],
                    '--hover': palette[1],
                    '--hover-light': palette[2],
                    '--shadow': 'rgba(0, 0, 0, 0.5)',
                    '--success': '#28a745',
                    '--warning': '#ffc107',
                    '--error': '#dc3545',
                    '--info': '#17a2b8'
                }
            };
        } else {
            return {
                id: themeName.toLowerCase().replace(/[^a-zA-Z0-9]/g, '-'),
                name: themeName,
                description: `Custom light theme based on ${baseColor}`,
                category: 'custom',
                icon: 'custom-icon',
                variables: {
                    '--bg-primary': '#ffffff',
                    '--bg-secondary': '#f8f9fa',
                    '--bg-tertiary': '#e9ecef',
                    '--bg-quaternary': '#dee2e6',
                    '--text-primary': palette[0],
                    '--text-secondary': palette[1],
                    '--text-tertiary': palette[2],
                    '--accent': baseColor,
                    '--accent-hover': this.darken(baseColor, 20),
                    '--accent-light': this.lighten(baseColor, 20),
                    '--border': '#dee2e6',
                    '--border-light': '#e9ecef',
                    '--hover': '#f8f9fa',
                    '--hover-light': '#e9ecef',
                    '--shadow': 'rgba(0, 0, 0, 0.15)',
                    '--success': '#28a745',
                    '--warning': '#ffc107',
                    '--error': '#dc3545',
                    '--info': '#17a2b8'
                }
            };
        }
    }

    /**
     * Validate theme accessibility
     */
    static validateThemeAccessibility(theme) {
        const issues = [];
        const variables = theme.variables;

        // Check background vs text contrast
        const bgPrimary = variables['--bg-primary'];
        const textPrimary = variables['--text-primary'];
        
        if (!this.isAccessible(bgPrimary, textPrimary)) {
            issues.push('Primary background and text colors do not meet accessibility standards');
        }

        // Check accent vs background contrast
        const accent = variables['--accent'];
        if (!this.isAccessible(bgPrimary, accent, 'AA-large')) {
            issues.push('Accent color may not be visible enough on primary background');
        }

        return {
            isAccessible: issues.length === 0,
            issues: issues
        };
    }

    /**
     * Export theme for sharing
     */
    static exportTheme(theme) {
        return {
            ...theme,
            exportedAt: new Date().toISOString(),
            exportedFrom: 'LANCAM Theme Manager v2.0',
            format: 'lancam-theme',
            version: '2.0'
        };
    }

    /**
     * Import and validate external theme
     */
    static importTheme(themeData) {
        try {
            // Basic validation
            if (!themeData.id || !themeData.name || !themeData.variables) {
                throw new Error('Invalid theme format: missing required fields');
            }

            // Sanitize theme
            const sanitized = {
                id: themeData.id.replace(/[^a-zA-Z0-9-]/g, ''),
                name: themeData.name.substring(0, 50),
                description: (themeData.description || '').substring(0, 200),
                category: themeData.category || 'custom',
                icon: themeData.icon || 'custom-icon',
                variables: { ...themeData.variables }
            };

            // Validate accessibility
            const accessibilityCheck = this.validateThemeAccessibility(sanitized);
            
            return {
                success: true,
                theme: sanitized,
                warnings: accessibilityCheck.issues
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

/**
 * Theme Builder - Interactive theme creation
 */
export class ThemeBuilder {
    constructor() {
        this.currentTheme = null;
        this.previewMode = false;
    }

    /**
     * Start building a new theme
     */
    startNew(baseTheme = 'dark') {
        const base = window.themeManager?.themes[baseTheme] || THEME_CONFIG.dark;
        this.currentTheme = JSON.parse(JSON.stringify(base));
        this.currentTheme.id = 'custom-' + Date.now();
        this.currentTheme.name = 'Custom Theme';
        this.currentTheme.category = 'custom';
        return this.currentTheme;
    }

    /**
     * Update a theme variable
     */
    updateVariable(variable, value) {
        if (this.currentTheme) {
            this.currentTheme.variables[variable] = value;
            
            if (this.previewMode) {
                this.previewChanges();
            }
        }
    }

    /**
     * Preview current changes
     */
    previewChanges() {
        if (this.currentTheme && window.themeManager) {
            // Temporarily apply the theme
            window.themeManager.applyThemeVariables(this.currentTheme.variables);
            this.previewMode = true;
        }
    }

    /**
     * Stop preview and revert to original theme
     */
    stopPreview() {
        if (window.themeManager && this.previewMode) {
            const originalTheme = window.themeManager.themes[window.themeManager.currentTheme];
            if (originalTheme) {
                window.themeManager.applyThemeVariables(originalTheme.variables);
            }
            this.previewMode = false;
        }
    }

    /**
     * Save the current theme
     */
    save() {
        if (this.currentTheme && window.themeManager) {
            const result = window.themeManager.addCustomTheme(this.currentTheme);
            if (result.success && this.previewMode) {
                window.themeManager.setTheme(this.currentTheme.id);
                this.previewMode = false;
            }
            return result;
        }
        return { success: false, error: 'No theme to save' };
    }
}
