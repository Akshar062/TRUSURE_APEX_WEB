/**
 * Theme Configuration System
 * Defines available themes and their properties
 */

export const THEME_CONFIG = {
    // Built-in themes
    dark: {
        id: 'dark',
        name: 'Dark',
        description: 'Classic dark theme for low-light environments',
        icon: 'moon-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#1a1a1a',
            '--bg-secondary': '#2d2d2d',
            '--bg-tertiary': '#404040',
            '--bg-quaternary': '#525252',
            '--text-primary': '#ffffff',
            '--text-secondary': '#b0b0b0',
            '--text-tertiary': '#888888',
            '--accent': '#007acc',
            '--accent-hover': '#005a9e',
            '--accent-light': '#4da6d9',
            '--border': '#555555',
            '--border-light': '#666666',
            '--hover': '#3d3d3d',
            '--hover-light': '#4a4a4a',
            '--shadow': 'rgba(0, 0, 0, 0.5)',
            '--success': '#28a745',
            '--warning': '#ffc107',
            '--error': '#dc3545',
            '--info': '#17a2b8'
        }
    },

    light: {
        id: 'light',
        name: 'Light',
        description: 'Clean light theme for bright environments',
        icon: 'sun-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#ffffff',
            '--bg-secondary': '#f8f9fa',
            '--bg-tertiary': '#e9ecef',
            '--bg-quaternary': '#dee2e6',
            '--text-primary': '#212529',
            '--text-secondary': '#6c757d',
            '--text-tertiary': '#adb5bd',
            '--accent': '#007bff',
            '--accent-hover': '#0056b3',
            '--accent-light': '#66b2ff',
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
    },

    blue: {
        id: 'blue',
        name: 'Ocean Blue',
        description: 'Professional blue theme with ocean-inspired colors',
        icon: 'water-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#0d1b2a',
            '--bg-secondary': '#1b263b',
            '--bg-tertiary': '#415a77',
            '--bg-quaternary': '#778da9',
            '--text-primary': '#e0e1dd',
            '--text-secondary': '#b8c5d6',
            '--text-tertiary': '#8fa3b8',
            '--accent': '#3a86ff',
            '--accent-hover': '#2563eb',
            '--accent-light': '#60a5fa',
            '--border': '#415a77',
            '--border-light': '#778da9',
            '--hover': '#1b263b',
            '--hover-light': '#415a77',
            '--shadow': 'rgba(13, 27, 42, 0.8)',
            '--success': '#10b981',
            '--warning': '#f59e0b',
            '--error': '#ef4444',
            '--info': '#06b6d4'
        }
    },

    green: {
        id: 'green',
        name: 'Forest Green',
        description: 'Nature-inspired green theme for a calming experience',
        icon: 'leaf-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#1a2e1a',
            '--bg-secondary': '#2d4a2d',
            '--bg-tertiary': '#406640',
            '--bg-quaternary': '#5c825c',
            '--text-primary': '#e8f5e8',
            '--text-secondary': '#c1dcc1',
            '--text-tertiary': '#9bb89b',
            '--accent': '#22c55e',
            '--accent-hover': '#16a34a',
            '--accent-light': '#4ade80',
            '--border': '#406640',
            '--border-light': '#5c825c',
            '--hover': '#2d4a2d',
            '--hover-light': '#406640',
            '--shadow': 'rgba(26, 46, 26, 0.8)',
            '--success': '#22c55e',
            '--warning': '#eab308',
            '--error': '#ef4444',
            '--info': '#06b6d4'
        }
    },

    purple: {
        id: 'purple',
        name: 'Royal Purple',
        description: 'Elegant purple theme with rich, royal colors',
        icon: 'crown-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#1e1a2e',
            '--bg-secondary': '#2d2548',
            '--bg-tertiary': '#4c3b6d',
            '--bg-quaternary': '#6b5b95',
            '--text-primary': '#f3f0ff',
            '--text-secondary': '#d4c5ff',
            '--text-tertiary': '#b19cd9',
            '--accent': '#8b5cf6',
            '--accent-hover': '#7c3aed',
            '--accent-light': '#a78bfa',
            '--border': '#4c3b6d',
            '--border-light': '#6b5b95',
            '--hover': '#2d2548',
            '--hover-light': '#4c3b6d',
            '--shadow': 'rgba(30, 26, 46, 0.8)',
            '--success': '#10b981',
            '--warning': '#f59e0b',
            '--error': '#ef4444',
            '--info': '#8b5cf6'
        }
    },

    cyberpunk: {
        id: 'cyberpunk',
        name: 'Cyberpunk',
        description: 'Futuristic neon theme inspired by cyberpunk aesthetics',
        icon: 'cpu-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#0a0a0a',
            '--bg-secondary': '#1a0a1a',
            '--bg-tertiary': '#2a1a2a',
            '--bg-quaternary': '#3a2a3a',
            '--text-primary': '#00ff88',
            '--text-secondary': '#88ff00',
            '--text-tertiary': '#ffff00',
            '--accent': '#ff0088',
            '--accent-hover': '#cc0066',
            '--accent-light': '#ff44aa',
            '--border': '#ff0088',
            '--border-light': '#ff44aa',
            '--hover': '#1a0a1a',
            '--hover-light': '#2a1a2a',
            '--shadow': 'rgba(255, 0, 136, 0.3)',
            '--success': '#00ff88',
            '--warning': '#ffaa00',
            '--error': '#ff0044',
            '--info': '#0088ff'
        }
    },

    sunset: {
        id: 'sunset',
        name: 'Sunset Orange',
        description: 'Warm sunset colors with orange and red tones',
        icon: 'sun-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#2c1810',
            '--bg-secondary': '#3d2317',
            '--bg-tertiary': '#5c3422',
            '--bg-quaternary': '#7a4530',
            '--text-primary': '#fff5f0',
            '--text-secondary': '#f4c2a1',
            '--text-tertiary': '#d19975',
            '--accent': '#ff6b35',
            '--accent-hover': '#e55a2e',
            '--accent-light': '#ff8660',
            '--border': '#5c3422',
            '--border-light': '#7a4530',
            '--hover': '#3d2317',
            '--hover-light': '#5c3422',
            '--shadow': 'rgba(44, 24, 16, 0.8)',
            '--success': '#32d74b',
            '--warning': '#ff9500',
            '--error': '#ff3b30',
            '--info': '#007aff'
        }
    },

    midnight: {
        id: 'midnight',
        name: 'Midnight Blue',
        description: 'Deep midnight blue theme for late-night work',
        icon: 'moon-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#0c1424',
            '--bg-secondary': '#152238',
            '--bg-tertiary': '#1f304c',
            '--bg-quaternary': '#2a3f60',
            '--text-primary': '#e6f1ff',
            '--text-secondary': '#b8d4ff',
            '--text-tertiary': '#8ab6ff',
            '--accent': '#4a9eff',
            '--accent-hover': '#3584e4',
            '--accent-light': '#70b1ff',
            '--border': '#1f304c',
            '--border-light': '#2a3f60',
            '--hover': '#152238',
            '--hover-light': '#1f304c',
            '--shadow': 'rgba(12, 20, 36, 0.9)',
            '--success': '#26d0ce',
            '--warning': '#f8a331',
            '--error': '#ed333b',
            '--info': '#33c7de'
        }
    },

    crimson: {
        id: 'crimson',
        name: 'Crimson Red',
        description: 'Bold crimson red theme with deep red accents',
        icon: 'heart-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#2c0a0a',
            '--bg-secondary': '#3d1515',
            '--bg-tertiary': '#5c2020',
            '--bg-quaternary': '#7a2b2b',
            '--text-primary': '#fff0f0',
            '--text-secondary': '#f4c1c1',
            '--text-tertiary': '#d19999',
            '--accent': '#dc2626',
            '--accent-hover': '#b91c1c',
            '--accent-light': '#ef4444',
            '--border': '#5c2020',
            '--border-light': '#7a2b2b',
            '--hover': '#3d1515',
            '--hover-light': '#5c2020',
            '--shadow': 'rgba(44, 10, 10, 0.8)',
            '--success': '#16a34a',
            '--warning': '#f59e0b',
            '--error': '#dc2626',
            '--info': '#0ea5e9'
        }
    },

    emerald: {
        id: 'emerald',
        name: 'Emerald Green',
        description: 'Rich emerald green theme with precious gem colors',
        icon: 'gem-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#0a2c0a',
            '--bg-secondary': '#15381d',
            '--bg-tertiary': '#1f502b',
            '--bg-quaternary': '#2d6839',
            '--text-primary': '#f0fff0',
            '--text-secondary': '#ccf2d1',
            '--text-tertiary': '#a7e6b2',
            '--accent': '#10b981',
            '--accent-hover': '#059669',
            '--accent-light': '#34d399',
            '--border': '#1f502b',
            '--border-light': '#2d6839',
            '--hover': '#15381d',
            '--hover-light': '#1f502b',
            '--shadow': 'rgba(10, 44, 10, 0.8)',
            '--success': '#10b981',
            '--warning': '#f59e0b',
            '--error': '#ef4444',
            '--info': '#06b6d4'
        }
    },

    slate: {
        id: 'slate',
        name: 'Slate Gray',
        description: 'Professional slate gray theme for focused work',
        icon: 'square-icon',
        category: 'built-in',
        variables: {
            '--bg-primary': '#1e293b',
            '--bg-secondary': '#334155',
            '--bg-tertiary': '#475569',
            '--bg-quaternary': '#64748b',
            '--text-primary': '#f1f5f9',
            '--text-secondary': '#cbd5e1',
            '--text-tertiary': '#94a3b8',
            '--accent': '#3b82f6',
            '--accent-hover': '#2563eb',
            '--accent-light': '#60a5fa',
            '--border': '#475569',
            '--border-light': '#64748b',
            '--hover': '#334155',
            '--hover-light': '#475569',
            '--shadow': 'rgba(30, 41, 59, 0.8)',
            '--success': '#22c55e',
            '--warning': '#f59e0b',
            '--error': '#ef4444',
            '--info': '#06b6d4'
        }
    },

    system: {
        id: 'system',
        name: 'System',
        description: 'Follows your system theme preference',
        icon: 'system-icon',
        category: 'built-in',
        variables: {} // Will be populated based on system preference
    }
};

export const THEME_CATEGORIES = {
    'built-in': {
        name: 'Built-in Themes',
        description: 'All available themes for the camera interface'
    }
};

export class ThemeValidator {
    static validateTheme(theme) {
        const requiredFields = ['id', 'name', 'variables'];
        const requiredVariables = [
            '--bg-primary', '--bg-secondary', '--text-primary', 
            '--text-secondary', '--accent', '--border', '--hover'
        ];

        for (const field of requiredFields) {
            if (!theme[field]) {
                throw new Error(`Theme missing required field: ${field}`);
            }
        }

        for (const variable of requiredVariables) {
            if (!theme.variables[variable]) {
                throw new Error(`Theme missing required CSS variable: ${variable}`);
            }
        }

        return true;
    }
}
