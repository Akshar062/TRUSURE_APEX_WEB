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
        
        // Set up zoom on camera preview if it exists and camera is active
        if (this.cameraActive) {
            // Small delay to ensure DOM is ready
            setTimeout(() => {
                this.setupCameraEventListeners();
            }, 200);
        }
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
            console.log('Camera preview element found, setting up event listeners');
            
            cameraPreview.addEventListener('error', function() {
                console.error('Failed to load camera stream');
                this.style.display = 'none';
                this.parentElement.innerHTML = '<div style="color: #ff6b6b; text-align: center;">Camera stream unavailable</div>';
            });
            
            cameraPreview.addEventListener('load', function() {
                console.log('Camera stream loaded successfully');
            });

            // 🔹 Add zoom with mouse scroll
            this.setupZoomListener(cameraPreview);
        } else {
            console.warn('Camera preview element not found!');
        }
    }

    setupZoomListener(cameraPreview) {
        let zoom = 1.0;        // Default zoom
        const zoomStep = 0.1;
        const minZoom = 1.0;
        const maxZoom = 4.0;

        console.log('Setting up zoom listener on camera preview');

        // Add wheel event listener for zoom
        const handleZoom = async (event) => {
            console.log('Wheel event detected:', event.deltaY);
            event.preventDefault();
            event.stopPropagation();

            const oldZoom = zoom;
            
            if (event.deltaY < 0) {
                zoom = Math.min(zoom + zoomStep, maxZoom); // zoom in
            } else {
                zoom = Math.max(zoom - zoomStep, minZoom); // zoom out
            }

            if (zoom !== oldZoom) {
                console.log("Zoom level changed from", oldZoom, "to", zoom);
                
                // Show zoom level to user
                this.showZoomFeedback(zoom);

                try {
                    const response = await fetch(`/api/camera/zoom?level=${zoom}`, { 
                        method: "POST" 
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    console.log('Zoom API response:', data);
                    
                } catch (err) {
                    console.error("Failed to set zoom:", err);
                    // Revert zoom on error
                    zoom = oldZoom;
                    this.showZoomFeedback(zoom, true);
                }
            }
        };

        // Try multiple ways to attach the event listener
        cameraPreview.addEventListener("wheel", handleZoom, { passive: false });
        
        // Also try on the parent container in case the image doesn't receive events
        const cameraFeed = cameraPreview.closest('.camera-feed');
        if (cameraFeed) {
            console.log('Also adding zoom listener to camera feed container');
            cameraFeed.addEventListener("wheel", handleZoom, { passive: false });
        }

        // Store the handler for potential cleanup
        this.zoomHandler = handleZoom;
        
        console.log('Zoom listener setup complete');
    }

    /**
     * Show zoom level feedback to user
     */
    showZoomFeedback(zoomLevel, isError = false) {
        // Remove any existing zoom feedback
        const existingFeedback = document.querySelector('.zoom-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        // Create zoom feedback element
        const feedback = document.createElement('div');
        feedback.className = 'zoom-feedback';
        feedback.style.cssText = `
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: ${isError ? 'rgba(255, 107, 107, 0.9)' : 'rgba(0, 0, 0, 0.7)'};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            z-index: 1000;
            pointer-events: none;
            transition: opacity 0.3s ease;
        `;
        
        feedback.textContent = isError ? 'Zoom Error!' : `Zoom: ${(zoomLevel * 100).toFixed(0)}%`;

        // Add to camera area
        const cameraArea = document.getElementById('cameraArea');
        if (cameraArea) {
            cameraArea.style.position = 'relative';
            cameraArea.appendChild(feedback);
        }

        // Auto-remove after 2 seconds
        setTimeout(() => {
            if (feedback && feedback.parentNode) {
                feedback.style.opacity = '0';
                setTimeout(() => {
                    if (feedback && feedback.parentNode) {
                        feedback.remove();
                    }
                }, 300);
            }
        }, 2000);
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
            .then(data => {
                console.log('Camera started:', data);
                // Ensure zoom listener is set up after camera starts
                this.setupCameraEventListeners();
            })
            .catch(error => console.error('Error starting camera:', error));
        }
    }

    /**
     * Set up camera event listeners after camera is started
     */
    setupCameraEventListeners() {
        // Small delay to ensure the camera preview is fully loaded
        setTimeout(() => {
            const cameraPreview = document.getElementById('cameraPreview');
            if (cameraPreview && !this.zoomHandler) {
                console.log('Setting up camera event listeners after wake');
                this.setupZoomListener(cameraPreview);
            }
        }, 500);
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
