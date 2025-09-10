/**
 * Camera management module
 * Handles camera controls, streaming, and API interactions
 */

export class CameraManager {
    constructor() {
        this.cameraActive = true; // Camera starts active by default
    }

    /**
     * Initialize camera and load controls
     */
    async initialize() {
        this.initializeCamera();
        await this.loadCameraControls();
        this.setupEventListeners();
    }

    /**
     * Set up camera-related event listeners
     */
    setupEventListeners() {
        // Focus slider
        const focusSlider = document.getElementById('focusSlider');
        if (focusSlider) {
            focusSlider.addEventListener('input', async (e) => {
                const value = parseFloat(e.target.value);
                const valueDisplay = e.target.parentElement.querySelector('.focus-value');
                if (valueDisplay) valueDisplay.textContent = value.toFixed(1);

                try {
                    await fetch('/api/camera/set_focus', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ mode: 'manual', position: value })
                    });
                } catch (err) {
                    console.error('Failed to set focus:', err);
                }
            });
        }

        // Exposure slider
        const exposureSlider = document.getElementById('exposureSlider');
        if (exposureSlider) {
            exposureSlider.addEventListener('input', async (e) => {
                const value = e.target.value;
                const label = e.target.parentElement.querySelector('.control-label');
                if (label) label.textContent = `Exposure: ${value}.00 ms`;
            });
        }

        // Gain slider
        const gainSlider = document.getElementById('gainSlider');
        if (gainSlider) {
            gainSlider.addEventListener('input', (e) => {
                const value = e.target.value;
                const label = e.target.parentElement.querySelector('.control-label');
                if (label) label.textContent = `Gain: ${value / 100}.00`;
                
                try {
                    fetch('/api/camera/set_gain', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ gain: value / 100 })
                    });
                } catch (err) {
                    console.error('Failed to set gain:', err);
                }
            });
        }

        // Auto focus button
        const autoFocusBtn = document.querySelector('.auto-focus-btn');
        if (autoFocusBtn) {
            autoFocusBtn.addEventListener('click', async () => {
                try {
                    const res = await fetch('/api/camera/trigger_af', { method: 'POST' });
                    const data = await res.json();
                    console.log(data.message);
                } catch (err) {
                    console.error('Failed to trigger autofocus:', err);
                }
            });
        }

        // Camera preview error handling
        const cameraPreview = document.getElementById('cameraPreview');
        if (cameraPreview) {
            cameraPreview.addEventListener('error', function() {
                console.error('Failed to load camera stream');
                this.style.display = 'none';
                this.parentElement.innerHTML = '<div style="color: #ff6b6b; text-align: center;">Camera stream unavailable</div>';
            });
            
            cameraPreview.addEventListener('load', function() {
                console.log('Camera stream loaded successfully');
            });
        }
    }

    /**
     * Load camera controls from API
     */
    async loadCameraControls() {
        // Focus
        await this.loadFocusControl();
        await this.loadExposureControl();
        await this.loadGainControl();
    }

    /**
     * Load focus control settings
     */
    async loadFocusControl() {
        const focusSlider = document.getElementById("focusSlider");
        if (!focusSlider) return;

        try {
            const res = await fetch("/api/camera/get_control_range", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ control_name: "LensPosition" })
            });
            const data = await res.json();
            
            if (data.success) {
                focusSlider.min = data.min;
                focusSlider.max = data.max;
                focusSlider.step = 0.1;
                focusSlider.value = data.current;
                
                const valueDisplay = focusSlider.parentElement.querySelector(".focus-value");
                if (valueDisplay) valueDisplay.textContent = data.current.toFixed(1);
            }
        } catch (error) {
            console.error('Failed to load focus control:', error);
        }
    }

    /**
     * Load exposure control settings
     */
    async loadExposureControl() {
        const exposureSlider = document.getElementById("exposureSlider");
        if (!exposureSlider) return;

        try {
            const res = await fetch("/api/camera/get_control_range", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ control_name: "ExposureTime" })
            });
            const data = await res.json();
            
            if (data.success) {
                // Convert µs to ms for UI
                let minMs = Math.round(data.min / 1000);
                let maxMs = Math.round(data.max / 1000);
                let currentMs = Math.round(data.current / 1000);

                // Keep max reasonable (e.g., 5000 ms = 5 sec)
                if (maxMs > 5000) maxMs = 5000;

                exposureSlider.min = minMs;
                exposureSlider.max = maxMs;
                exposureSlider.value = currentMs;
                
                const label = exposureSlider.parentElement.querySelector(".control-label");
                if (label) label.textContent = `Exposure: ${currentMs} ms`;
            }
        } catch (error) {
            console.error('Failed to load exposure control:', error);
        }
    }

    /**
     * Load gain control settings
     */
    async loadGainControl() {
        const gainSlider = document.getElementById("gainSlider");
        if (!gainSlider) return;

        try {
            const res = await fetch("/api/camera/get_control_range", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ control_name: "AnalogueGain" })
            });
            const data = await res.json();
            
            if (data.success) {
                gainSlider.min = 100;
                gainSlider.max = 6400;
                gainSlider.value = data.current * 100;
                
                const label = gainSlider.parentElement.querySelector(".control-label");
                if (label) label.textContent = `Gain: ${gainSlider.value / 100}.00`;
            }
        } catch (error) {
            console.error('Failed to load gain control:', error);
        }
    }

    /**
     * Wake up the camera
     */
    wakeCamera() {
        const cameraFeed = document.getElementById('cameraFeed');
        const cameraPlaceholder = document.getElementById('cameraPlaceholder');
        const cameraArea = document.getElementById('cameraArea');
        
        if (!this.cameraActive) {
            this.cameraActive = true;
            if (cameraFeed) cameraFeed.style.display = 'flex';
            if (cameraPlaceholder) cameraPlaceholder.style.display = 'none';
            if (cameraArea) cameraArea.classList.add('camera-active');
            
            // Start camera via API
            fetch('/api/camera/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => console.log('Camera started:', data))
            .catch(error => console.error('Error starting camera:', error));
        }
    }

    /**
     * Put camera to sleep
     */
    sleepCamera() {
        const cameraFeed = document.getElementById('cameraFeed');
        const cameraPlaceholder = document.getElementById('cameraPlaceholder');
        const cameraArea = document.getElementById('cameraArea');
        
        if (this.cameraActive) {
            this.cameraActive = false;
            if (cameraFeed) cameraFeed.style.display = 'none';
            if (cameraPlaceholder) cameraPlaceholder.style.display = 'flex';
            if (cameraArea) cameraArea.classList.remove('camera-active');
            
            // Stop camera via API
            fetch('/api/camera/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => console.log('Camera stopped:', data))
            .catch(error => console.error('Error stopping camera:', error));
        }
    }

    /**
     * Initialize camera state when page loads
     */
    initializeCamera() {
        const cameraFeed = document.getElementById('cameraFeed');
        const cameraPlaceholder = document.getElementById('cameraPlaceholder');
        const cameraArea = document.getElementById('cameraArea');
        
        if (this.cameraActive) {
            if (cameraFeed) cameraFeed.style.display = 'flex';
            if (cameraPlaceholder) cameraPlaceholder.style.display = 'none';
            if (cameraArea) cameraArea.classList.add('camera-active');
        } else {
            if (cameraFeed) cameraFeed.style.display = 'none';
            if (cameraPlaceholder) cameraPlaceholder.style.display = 'flex';
            if (cameraArea) cameraArea.classList.remove('camera-active');
        }
    }
}
