#!/usr/bin/env python3
"""
Flask Picamera2 Live Streaming Application with Real-time Controls
Provides MJPEG streaming and camera control interface
"""

from flask import Flask, render_template_string, Response, jsonify, request
from picamera2 import Picamera2
import cv2
import json
import threading
import time
import traceback
from io import BytesIO

app = Flask(__name__)

# Global camera instance
camera = None
camera_lock = threading.Lock()
current_frame = None

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Picamera2 Live Stream with Controls</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stream-container {
            text-align: center;
            margin-bottom: 30px;
        }
        #stream {
            max-width: 100%;
            border: 2px solid #333;
            border-radius: 5px;
        }
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .control-group {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }
        .control-group h3 {
            margin-top: 0;
            color: #495057;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 5px;
        }
        .control-item {
            margin-bottom: 15px;
        }
        .control-item label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
            color: #495057;
        }
        .slider-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        input[type="range"] {
            flex: 1;
            height: 6px;
            border-radius: 3px;
            background: #ddd;
            outline: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #007bff;
            cursor: pointer;
        }
        .value-display {
            min-width: 80px;
            text-align: center;
            font-weight: bold;
            color: #007bff;
        }
        select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .button-group {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        .btn-primary {
            background-color: #007bff;
            color: white;
        }
        .btn-primary:hover {
            background-color: #0056b3;
        }
        .btn-secondary {
            background-color: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background-color: #545b62;
        }
        .status-info {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            border-left: 4px solid #007bff;
        }
        .error-msg {
            color: #dc3545;
            background: #f8d7da;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            display: none;
        }
        .success-msg {
            color: #155724;
            background: #d4edda;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📷 Picamera2 Live Stream Control</h1>
        
        <div class="stream-container">
            <img id="stream" src="/stream" alt="Live Stream">
        </div>

        <div class="controls-grid">
            <!-- Exposure Controls -->
            <div class="control-group">
                <h3>🌞 Exposure Settings</h3>
                <div class="control-item">
                    <label for="exposureTime">Exposure Time (µs)</label>
                    <div class="slider-container">
                        <input type="range" id="exposureTime" min="100" max="30000" value="10000">
                        <div class="value-display" id="exposureTimeValue">10000</div>
                    </div>
                </div>
                <div class="control-item">
                    <label for="analogueGain">Analogue Gain</label>
                    <div class="slider-container">
                        <input type="range" id="analogueGain" min="1.0" max="8.0" step="0.1" value="1.0">
                        <div class="value-display" id="analogueGainValue">1.0</div>
                    </div>
                </div>
            </div>

            <!-- Focus Controls -->
            <div class="control-group">
                <h3>🔍 Focus Settings</h3>
                <div class="control-item">
                    <label for="afMode">Auto Focus Mode</label>
                    <select id="afMode">
                        <option value="0">Auto</option>
                        <option value="1">Manual</option>
                        <option value="2">Continuous</option>
                    </select>
                </div>
                <div class="control-item">
                    <label for="lensPosition">Lens Position (Manual Focus)</label>
                    <div class="slider-container">
                        <input type="range" id="lensPosition" min="0" max="10" step="0.1" value="1.0">
                        <div class="value-display" id="lensPositionValue">1.0</div>
                    </div>
                </div>
            </div>

            <!-- Color Controls -->
            <div class="control-group">
                <h3>🎨 Color Balance</h3>
                <div class="control-item">
                    <label for="colourGainRed">Red Gain</label>
                    <div class="slider-container">
                        <input type="range" id="colourGainRed" min="0.5" max="3.0" step="0.1" value="1.0">
                        <div class="value-display" id="colourGainRedValue">1.0</div>
                    </div>
                </div>
                <div class="control-item">
                    <label for="colourGainBlue">Blue Gain</label>
                    <div class="slider-container">
                        <input type="range" id="colourGainBlue" min="0.5" max="3.0" step="0.1" value="1.0">
                        <div class="value-display" id="colourGainBlueValue">1.0</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="button-group">
            <button class="btn-primary" onclick="resetToAuto()">🔄 Reset to Auto</button>
            <button class="btn-secondary" onclick="updateStatus()">📊 Refresh Status</button>
        </div>

        <div class="error-msg" id="errorMsg"></div>
        <div class="success-msg" id="successMsg"></div>

        <div class="status-info">
            <h3>📋 Camera Status</h3>
            <pre id="statusDisplay">Loading...</pre>
        </div>
    </div>

    <script>
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            setupEventListeners();
            updateStatus();
            // Update status every 5 seconds
            setInterval(updateStatus, 5000);
        });

        function setupEventListeners() {
            // Exposure controls
            document.getElementById('exposureTime').addEventListener('input', function(e) {
                updateValueDisplay('exposureTime', e.target.value);
                setControl('ExposureTime', parseInt(e.target.value));
            });
            
            document.getElementById('analogueGain').addEventListener('input', function(e) {
                updateValueDisplay('analogueGain', e.target.value);
                setControl('AnalogueGain', parseFloat(e.target.value));
            });

            // Focus controls
            document.getElementById('afMode').addEventListener('change', function(e) {
                setControl('AfMode', parseInt(e.target.value));
            });
            
            document.getElementById('lensPosition').addEventListener('input', function(e) {
                updateValueDisplay('lensPosition', e.target.value);
                setControl('LensPosition', parseFloat(e.target.value));
            });

            // Color controls
            document.getElementById('colourGainRed').addEventListener('input', function(e) {
                updateValueDisplay('colourGainRed', e.target.value);
                updateColorGains();
            });
            
            document.getElementById('colourGainBlue').addEventListener('input', function(e) {
                updateValueDisplay('colourGainBlue', e.target.value);
                updateColorGains();
            });
        }

        function updateValueDisplay(controlId, value) {
            document.getElementById(controlId + 'Value').textContent = value;
        }

        function updateColorGains() {
            const redGain = parseFloat(document.getElementById('colourGainRed').value);
            const blueGain = parseFloat(document.getElementById('colourGainBlue').value);
            setControl('ColourGains', [redGain, blueGain]);
        }

        async function setControl(control, value) {
            try {
                const response = await fetch('/api/set_control', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        control: control,
                        value: value
                    })
                });

                const result = await response.json();
                
                if (result.success) {
                    showSuccess(`${control} updated successfully`);
                } else {
                    showError(`Failed to update ${control}: ${result.error}`);
                }
            } catch (error) {
                showError(`Network error: ${error.message}`);
            }
        }

        async function setControls(controls) {
            try {
                const response = await fetch('/api/set_controls', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(controls)
                });

                const result = await response.json();
                
                if (result.success) {
                    showSuccess('Controls updated successfully');
                } else {
                    showError(`Failed to update controls: ${result.error}`);
                }
            } catch (error) {
                showError(`Network error: ${error.message}`);
            }
        }

        async function resetToAuto() {
            const autoControls = {
                'AeEnable': true,
                'AfMode': 0,  // Auto focus
                'ColourGains': [1.0, 1.0]  // Reset color gains
            };
            
            await setControls(autoControls);
            
            // Update UI to reflect auto settings
            document.getElementById('afMode').value = '0';
            document.getElementById('colourGainRed').value = '1.0';
            document.getElementById('colourGainBlue').value = '1.0';
            updateValueDisplay('colourGainRed', '1.0');
            updateValueDisplay('colourGainBlue', '1.0');
            
            updateStatus();
        }

        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                
                if (status.success) {
                    document.getElementById('statusDisplay').textContent = 
                        JSON.stringify(status.data, null, 2);
                } else {
                    document.getElementById('statusDisplay').textContent = 
                        'Error loading status: ' + status.error;
                }
            } catch (error) {
                document.getElementById('statusDisplay').textContent = 
                    'Network error: ' + error.message;
            }
        }

        function showError(message) {
            const errorMsg = document.getElementById('errorMsg');
            errorMsg.textContent = message;
            errorMsg.style.display = 'block';
            document.getElementById('successMsg').style.display = 'none';
            setTimeout(() => {
                errorMsg.style.display = 'none';
            }, 5000);
        }

        function showSuccess(message) {
            const successMsg = document.getElementById('successMsg');
            successMsg.textContent = message;
            successMsg.style.display = 'block';
            document.getElementById('errorMsg').style.display = 'none';
            setTimeout(() => {
                successMsg.style.display = 'none';
            }, 3000);
        }
    </script>
</body>
</html>
"""

def initialize_camera():
    """Initialize and configure the Picamera2 instance."""
    global camera
    try:
        camera = Picamera2()
        
        # Configure for preview with RGB format
        config = camera.create_preview_configuration(
            main={"format": "RGB888", "size": (1280, 720)}
        )
        camera.configure(config)
        
        # Start the camera
        camera.start()
        
        # Wait for camera to settle
        time.sleep(2)
        
        print("Camera initialized successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing camera: {e}")
        traceback.print_exc()
        return False

def capture_frames():
    """Background thread to continuously capture frames."""
    global current_frame, camera
    
    while camera is not None:
        try:
            with camera_lock:
                if camera is not None:
                    # Capture frame as RGB array
                    frame = camera.capture_array()
                    
                    # Convert RGB to BGR for OpenCV
                    # frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # Encode as JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, 
                                             [cv2.IMWRITE_JPEG_QUALITY, 100])
                    
                    if ret:
                        current_frame = buffer.tobytes()
                        
            time.sleep(1/30)  # ~30 FPS
            
        except Exception as e:
            print(f"Error capturing frame: {e}")
            time.sleep(1)

def generate_frames():
    """Generator function for streaming frames."""
    global current_frame
    
    while True:
        if current_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')
        time.sleep(1/30)  # ~30 FPS

@app.route('/')
def index():
    """Serve the main HTML interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/stream')
def stream():
    """MJPEG streaming endpoint."""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def get_status():
    """Get current camera status and configuration."""
    try:
        with camera_lock:
            if camera is None:
                return jsonify({
                    'success': False, 
                    'error': 'Camera not initialized'
                })
            
            # Get camera configuration
            config = camera.camera_configuration()
            
            # Get current controls (only JSON-serializable ones)
            controls = {}
            try:
                camera_controls = camera.capture_metadata()
                
                # Extract key controls that are JSON serializable
                json_safe_controls = [
                    'ExposureTime', 'AnalogueGain', 'ColourGains',
                    'AfMode', 'LensPosition', 'AeEnable', 'FocusFoM'
                ]
                
                for control in json_safe_controls:
                    if control in camera_controls:
                        value = camera_controls[control]
                        # Ensure value is JSON serializable
                        if isinstance(value, (int, float, bool, str, list)):
                            controls[control] = value
                        else:
                            controls[control] = str(value)
                            
            except Exception as e:
                controls = {'error': f'Could not read controls: {str(e)}'}
            
            return jsonify({
                'success': True,
                'data': {
                    'configuration': str(config),
                    'controls': controls,
                    'timestamp': time.time()
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Status error: {str(e)}'
        })

@app.route('/api/set_control', methods=['POST'])
def set_control():
    """Set a single camera control."""
    try:
        data = request.get_json()
        if not data or 'control' not in data or 'value' not in data:
            return jsonify({
                'success': False,
                'error': 'Invalid request. Need control and value.'
            })
        
        control_name = data['control']
        control_value = data['value']
        
        with camera_lock:
            if camera is None:
                return jsonify({
                    'success': False,
                    'error': 'Camera not initialized'
                })
            
            # Set the control
            camera.set_controls({control_name: control_value})
            
        return jsonify({
            'success': True,
            'message': f'Control {control_name} set to {control_value}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Control error: {str(e)}'
        })

@app.route('/api/set_controls', methods=['POST'])
def set_controls():
    """Set multiple camera controls at once."""
    try:
        controls = request.get_json()
        if not controls:
            return jsonify({
                'success': False,
                'error': 'Invalid request. Need controls object.'
            })
        
        with camera_lock:
            if camera is None:
                return jsonify({
                    'success': False,
                    'error': 'Camera not initialized'
                })
            
            # Set all controls
            camera.set_controls(controls)
            
        return jsonify({
            'success': True,
            'message': f'Set {len(controls)} controls successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Controls error: {str(e)}'
        })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

def cleanup():
    """Cleanup function to properly close camera."""
    global camera
    if camera is not None:
        try:
            camera.stop()
            camera.close()
            camera = None
            print("Camera cleaned up successfully")
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == '__main__':
    try:
        print("Initializing Picamera2...")
        
        if not initialize_camera():
            print("Failed to initialize camera. Exiting.")
            exit(1)
        
        # Start frame capture thread
        frame_thread = threading.Thread(target=capture_frames, daemon=True)
        frame_thread.start()
        
        print("Starting Flask server...")
        print("Open http://localhost:5000 to view the stream and controls")
        
        # Run Flask app
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    except KeyboardInterrupt:
        print("\nShutting down...")
        
    finally:
        cleanup()