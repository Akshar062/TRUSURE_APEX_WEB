# LANCAM Frontend - JavaScript Module Structure

## Overview

The frontend JavaScript code has been modularized into separate files for better maintainability, reusability, and organization.

## Module Structure

```
Frontend/
├─ js/
│  ├─ app.js           # Main application coordinator
│  ├─ theme.js         # Theme management
│  ├─ components.js    # Component loading (navbar, footer)
│  ├─ datetime.js      # Date/time display
│  ├─ power.js         # Power menu functionality
│  ├─ camera.js        # Camera controls and API interactions
│  └─ ui-controls.js   # UI controls (buttons, toggles, navigation)
├─ script.js           # Main entry point (ES6 modules)
└─ script-original.js  # Original monolithic script (backup)
```

## Modules Description

### app.js - Main Application
- **Purpose**: Coordinates all other modules and handles application initialization
- **Key Features**:
  - Initializes all managers and components
  - Provides cleanup functionality
  - Maintains backward compatibility by exposing managers globally

### theme.js - Theme Management
- **Purpose**: Handles theme switching, storage, and system theme detection
- **Key Features**:
  - Light/Dark/System theme support
  - LocalStorage persistence
  - Dropdown management
  - System theme change detection

### components.js - Component Loader
- **Purpose**: Loads HTML components (navbar, footer)
- **Key Features**:
  - Async component loading
  - Error handling
  - Promise-based API

### datetime.js - Date & Time
- **Purpose**: Manages date/time display and updates
- **Key Features**:
  - Real-time updates
  - Formatted date/time display
  - Start/stop functionality

### power.js - Power Management
- **Purpose**: Handles power button functionality and power actions
- **Key Features**:
  - Power menu toggle
  - Outside click detection
  - Keyboard shortcuts (Escape)
  - Power action handling

### camera.js - Camera Management
- **Purpose**: Manages camera controls, streaming, and API interactions
- **Key Features**:
  - Camera control initialization
  - Focus/Exposure/Gain controls
  - Camera start/stop functionality
  - API communication
  - Error handling for camera stream

### ui-controls.js - UI Controls
- **Purpose**: Handles various UI interactions and controls
- **Key Features**:
  - Navigation tab management
  - Control buttons (light, scan)
  - Toggle switches
  - Event handling

## Benefits of Modularization

1. **Maintainability**: Each module has a single responsibility
2. **Reusability**: Modules can be reused in other projects
3. **Testing**: Individual modules can be tested in isolation
4. **Performance**: Modules can be loaded on-demand
5. **Collaboration**: Multiple developers can work on different modules
6. **Debugging**: Issues can be isolated to specific modules

## Backward Compatibility

The modular structure maintains backward compatibility with existing HTML:
- Global functions are still available for `onclick` handlers
- All original functionality is preserved
- Manager instances are accessible via `window` object

## Usage

### Basic Usage
The application initializes automatically when the DOM is ready. No manual initialization required.

### Accessing Managers
```javascript
// Access theme manager
window.themeManager.setTheme('dark');

// Access camera manager
window.cameraManager.wakeCamera();

// Access power manager
window.powerManager.handlePowerAction('shutdown');
```

### Importing Modules (for development)
```javascript
import { CameraManager } from './js/camera.js';
import { ThemeManager } from './js/theme.js';

const camera = new CameraManager();
const theme = new ThemeManager();
```

## Migration Notes

1. **Original script**: Backed up as `script-original.js`
2. **HTML changes**: Updated to use `type="module"` for ES6 imports
3. **Global functions**: Still available for existing HTML onclick handlers
4. **API compatibility**: All original API calls remain unchanged

## Future Enhancements

- Add unit tests for each module
- Implement lazy loading for non-critical modules
- Add TypeScript support
- Create build process for production optimization
- Add module bundling for better performance
