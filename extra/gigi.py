#!/usr/bin/env python3
"""
Professional Raspberry Pi GigE Camera System
Converts Raspberry Pi into a professional streaming camera with:
- MJPEG/RTMP/RTSP streaming
- Professional camera controls
- Multi-format output
- Network camera interface
- Recording capabilities
"""

import os
import sys
import json
import time
import threading
import subprocess
import traceback
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template_string, Response, jsonify, request, send_file
from picamera2 import Picamera2
import cv2

app = Flask(__name__)

# Global variables
camera = None
camera_lock = threading.Lock()
current_frame = None
is_recording = False
rtmp_process = None
rtsp_process = None
recording_process = None

# Configuration
CONFIG = {
    'camera': {
        'resolution': (1920, 1080),  # Full HD for professional use
        'framerate': 30,
        'format': 'RGB888'
    },
    'streaming': {
        'mjpeg_quality': 85,
        'h264_bitrate': 4000000,  # 4Mbps for high quality
        'keyframe_interval': 30
    },
    'paths': {
        'recordings': '/home/mindrontm/camera_recordings',
        'logs': '/home/mindrontm/camera_logs'
    }
}

# Professional HTML Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎥 Professional GigE Camera System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #4a90e2;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.8;
        }
        
        .container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            padding: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .stream-section {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .stream-container {
            position: relative;
            margin-bottom: 20px;
        }
        
        #stream {
            width: 100%;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .stream-overlay {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.7);
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
        }
        
        .stream-controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        
        .controls-section {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            max-height: calc(100vh - 200px);
            overflow-y: auto;
        }
        
        .control-group {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .control-group h3 {
            margin-bottom: 15px;
            color: #4fc3f7;
            border-bottom: 1px solid rgba(79,195,247,0.3);
            padding-bottom: 5px;
        }
        
        .control-item {
            margin-bottom: 15px;
        }
        
        .control-item label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #e3f2fd;
        }
        
        .slider-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        input[type="range"] {
            flex: 1;
            height: 8px;
            border-radius: 4px;
            background: rgba(255,255,255,0.2);
            outline: none;
            appearance: none;
        }
        
        input[type="range"]::-webkit-slider-thumb {
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4fc3f7, #29b6f6);
            cursor: pointer;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }
        
        .value-display {
            min-width: 80px;
            text-align: center;
            font-weight: bold;
            color: #4fc3f7;
            background: rgba(255,255,255,0.1);
            padding: 5px 10px;
            border-radius: 5px;
        }
        
        select {
            width: 100%;
            padding: 10px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 14px;
        }
        
        select option {
            background: #1e3c72;
            color: white;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #4fc3f7, #29b6f6);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(79,195,247,0.4);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #f44336, #d32f2f);
            color: white;
        }
        
        .btn-danger:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(244,67,54,0.4);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #4caf50, #388e3c);
            color: white;
        }
        
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(76,175,80,0.4);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .status-display {
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            font-family: monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .streaming-status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .status-badge {
            padding: 8px 12px;
            border-radius: 20px;
            text-align: center;
            font-size: 12px;
            font-weight: bold;
        }
        
        .status-active {
            background: rgba(76,175,80,0.8);
            color: white;
        }
        
        .status-inactive {
            background: rgba(158,158,158,0.8);
            color: white;
        }
        
        .url-input {
            width: 100%;
            padding: 8px;
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 5px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 12px;
        }
        
        .url-input::placeholder {
            color: rgba(255,255,255,0.6);
        }
        
        .recording-controls {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-top: 10px;
        }
        
        .recording-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #f44336;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .message {
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-weight: bold;
        }
        
        .message.error {
            background: rgba(244,67,54,0.8);
            color: white;
        }
        
        .message.success {
            background: rgba(76,175,80,0.8);
            color: white;
        }
        
        .message.info {
            background: rgba(33,150,243,0.8);
            color: white;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎥 Professional GigE Camera System</h1>
        <div class="subtitle">Raspberry Pi Industrial Camera Interface</div>
    </div>

    <div class="container">
        <!-- Stream Section -->
        <div class="stream-section">
            <div class="stream-container">
                <img id="stream" src="/stream" alt="Live Stream">
                <div class="stream-overlay">
                    <div id="streamInfo">
                        <div>Resolution: 1920x1080</div>
                        <div>FPS: <span id="fpsCounter">30</span></div>
                        <div>Timestamp: <span id="timestamp"></span></div>
                    </div>
                </div>
            </div>
            
            <div class="streaming-status">
                <div class="status-badge status-inactive" id="mjpegStatus">MJPEG</div>
                <div class="status-badge status-inactive" id="rtmpStatus">RTMP</div>
                <div class="status-badge status-inactive" id="rtspStatus">RTSP</div>
                <div class="status-badge status-inactive" id="recordStatus">REC</div>
            </div>
            
            <div class="stream-controls">
                <button class="btn btn-primary" onclick="startRTMP()">Start RTMP Stream</button>
                <button class="btn btn-danger" onclick="stopRTMP()">Stop RTMP</button>
                <button class="btn btn-primary" onclick="startRTSP()">Start RTSP Server</button>
                <button class="btn btn-danger" onclick="stopRTSP()">Stop RTSP</button>
            </div>
            
            <div style="margin-top: 10px;">
                <input type="text" id="rtmpUrl" class="url-input" 
                       placeholder="RTMP URL (e.g., rtmp://youtube.com/live2/YOUR_KEY)">
            </div>
            
            <div class="recording-controls">
                <button class="btn btn-success" id="recordBtn" onclick="toggleRecording()">Start Recording</button>
                <div id="recordingIndicator" style="display: none;">
                    <div class="recording-indicator"></div>
                    <span>REC</span>
                </div>
            </div>
        </div>

        <!-- Controls Section -->
        <div class="controls-section">
            <!-- Camera Controls -->
            <div class="control-group">
                <h3>📹 Camera Settings</h3>
                <div class="control-item">
                    <label for="exposureTime">Exposure Time (µs)</label>
                    <div class="slider-container">
                        <input type="range" id="exposureTime" min="100" max="50000" value="10000">
                        <div class="value-display" id="exposureTimeValue">10000</div>
                    </div>
                </div>
                <div class="control-item">
                    <label for="analogueGain">Analogue Gain</label>
                    <div class="slider-container">
                        <input type="range" id="analogueGain" min="1.0" max="16.0" step="0.1" value="1.0">
                        <div class="value-display" id="analogueGainValue">1.0</div>
                    </div>
                </div>
                <div class="control-item">
                    <label for="digitalGain">Digital Gain</label>
                    <div class="slider-container">
                        <input type="range" id="digitalGain" min="1.0" max="4.0" step="0.1" value="1.0">
                        <div class="value-display" id="digitalGainValue">1.0</div>
                    </div>
                </div>
            </div>

            <!-- Focus & Lens Controls -->
            <div class="control-group">
                <h3>🔍 Focus & Lens</h3>
                <div class="control-item">
                    <label for="afMode">Auto Focus Mode</label>
                    <select id="afMode">
                        <option value="0">Manual</option>
                        <option value="1">Auto Single</option>
                        <option value="2">Continuous</option>
                    </select>
                </div>
                <div class="control-item">
                    <label for="lensPosition">Lens Position</label>
                    <div class="slider-container">
                        <input type="range" id="lensPosition" min="0" max="32" step="0.1" value="1.0">
                        <div class="value-display" id="lensPositionValue">1.0</div>
                    </div>
                </div>
            </div>

            <!-- Color Controls -->
            <div class="control-group">
                <h3>🎨 Color & White Balance</h3>
                <div class="control-item">
                    <label for="awbMode">White Balance Mode</label>
                    <select id="awbMode">
                        <option value="0">Auto</option>
                        <option value="1">Incandescent</option>
                        <option value="2">Tungsten</option>
                        <option value="3">Fluorescent</option>
                        <option value="4">Indoor</option>
                        <option value="5">Daylight</option>
                        <option value="6">Cloudy</option>
                    </select>
                </div>
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
                <div class="control-item">
                    <label for="saturation">Saturation</label>
                    <div class="slider-container">
                        <input type="range" id="saturation" min="0" max="2" step="0.1" value="1.0">
                        <div class="value-display" id="saturationValue">1.0</div>
                    </div>
                </div>
                <div class="control-item">
                    <label for="contrast">Contrast</label>
                    <div class="slider-container">
                        <input type="range" id="contrast" min="0" max="2" step="0.1" value="1.0">
                        <div class="value-display" id="contrastValue">1.0</div>
                    </div>
                </div>
            </div>

            <!-- Professional Presets -->
            <div class="control-group">
                <h3>⚙️ Professional Presets</h3>
                <div style="display: grid; gap: 10px;">
                    <button class="btn btn-primary" onclick="applyPreset('broadcast')">📺 Broadcast Quality</button>
                    <button class="btn btn-primary" onclick="applyPreset('studio')">🎬 Studio Lighting</button>
                    <button class="btn btn-primary" onclick="applyPreset('outdoor')">🌞 Outdoor/Daylight</button>
                    <button class="btn btn-primary" onclick="applyPreset('lowlight')">🌙 Low Light</button>
                    <button class="btn btn-primary" onclick="applyPreset('reset')">🔄 Reset All</button>
                </div>
            </div>

            <!-- System Status -->
            <div class="control-group">
                <h3>📊 System Status</h3>
                <div class="status-display" id="systemStatus">Loading system status...</div>
            </div>
        </div>
    </div>

    <div id="messageContainer"></div>

    <script>
        let statusUpdateInterval;
        
        document.addEventListener('DOMContentLoaded', function() {
            setupEventListeners();
            updateSystemStatus();
            updateTimestamp();
            
            // Update system status every 5 seconds
            statusUpdateInterval = setInterval(updateSystemStatus, 5000);
            
            // Update timestamp every second
            setInterval(updateTimestamp, 1000);
        });

        function setupEventListeners() {
            // Camera controls
            const controls = [
                'exposureTime', 'analogueGain', 'digitalGain', 'lensPosition',
                'colourGainRed', 'colourGainBlue', 'saturation', 'contrast'
            ];
            
            controls.forEach(control => {
                const element = document.getElementById(control);
                if (element) {
                    element.addEventListener('input', function(e) {
                        updateValueDisplay(control, e.target.value);
                        setControl(getControlName(control), parseValue(control, e.target.value));
                    });
                }
            });
            
            // Select controls
            document.getElementById('afMode').addEventListener('change', function(e) {
                setControl('AfMode', parseInt(e.target.value));
            });
            
            document.getElementById('awbMode').addEventListener('change', function(e) {
                setControl('AwbMode', parseInt(e.target.value));
            });
        }

        function getControlName(htmlId) {
            const mapping = {
                'exposureTime': 'ExposureTime',
                'analogueGain': 'AnalogueGain',
                'digitalGain': 'DigitalGain',
                'lensPosition': 'LensPosition',
                'colourGainRed': 'ColourGains',  // Special handling needed
                'colourGainBlue': 'ColourGains', // Special handling needed
                'saturation': 'Saturation',
                'contrast': 'Contrast'
            };
            return mapping[htmlId] || htmlId;
        }

        function parseValue(control, value) {
            if (control === 'exposureTime') return parseInt(value);
            return parseFloat(value);
        }

        function updateValueDisplay(controlId, value) {
            const displayElement = document.getElementById(controlId + 'Value');
            if (displayElement) {
                displayElement.textContent = value;
            }
        }

        function updateColorGains() {
            const redGain = parseFloat(document.getElementById('colourGainRed').value);
            const blueGain = parseFloat(document.getElementById('colourGainBlue').value);
            setControl('ColourGains', [redGain, blueGain]);
        }

        async function setControl(control, value) {
            if (control === 'ColourGains' && !Array.isArray(value)) {
                updateColorGains();
                return;
            }
            
            try {
                const response = await fetch('/api/set_control', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ control: control, value: value })
                });
                
                const result = await response.json();
                if (!result.success) {
                    showMessage(`Error: ${result.error}`, 'error');
                }
            } catch (error) {
                showMessage(`Network error: ${error.message}`, 'error');
            }
        }

        async function applyPreset(presetName) {
            try {
                const response = await fetch(`/api/preset/${presetName}`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage(`Applied ${presetName} preset`, 'success');
                    updateSystemStatus();
                } else {
                    showMessage(`Failed to apply preset: ${result.error}`, 'error');
                }
            } catch (error) {
                showMessage(`Network error: ${error.message}`, 'error');
            }
        }

        async function startRTMP() {
            const rtmpUrl = document.getElementById('rtmpUrl').value;
            if (!rtmpUrl) {
                showMessage('Please enter RTMP URL', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/streaming/rtmp/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: rtmpUrl })
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage('RTMP streaming started', 'success');
                    document.getElementById('rtmpStatus').className = 'status-badge status-active';
                } else {
                    showMessage(`Failed to start RTMP: ${result.error}`, 'error');
                }
            } catch (error) {
                showMessage(`Network error: ${error.message}`, 'error');
            }
        }

        async function stopRTMP() {
            try {
                const response = await fetch('/api/streaming/rtmp/stop', {
                    method: 'POST'
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage('RTMP streaming stopped', 'info');
                    document.getElementById('rtmpStatus').className = 'status-badge status-inactive';
                } else {
                    showMessage(`Failed to stop RTMP: ${result.error}`, 'error');
                }
            } catch (error) {
                showMessage(`Network error: ${error.message}`, 'error');
            }
        }

        async function startRTSP() {
            try {
                const response = await fetch('/api/streaming/rtsp/start', {
                    method: 'POST'
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage(`RTSP server started on ${result.url}`, 'success');
                    document.getElementById('rtspStatus').className = 'status-badge status-active';
                } else {
                    showMessage(`Failed to start RTSP: ${result.error}`, 'error');
                }
            } catch (error) {
                showMessage(`Network error: ${error.message}`, 'error');
            }
        }

        async function stopRTSP() {
            try {
                const response = await fetch('/api/streaming/rtsp/stop', {
                    method: 'POST'
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage('RTSP server stopped', 'info');
                    document.getElementById('rtspStatus').className = 'status-badge status-inactive';
                } else {
                    showMessage(`Failed to stop RTSP: ${result.error}`, 'error');
                }
            } catch (error) {
                showMessage(`Network error: ${error.message}`, 'error');
            }
        }

        async function toggleRecording() {
            const isCurrentlyRecording = document.getElementById('recordBtn').textContent === 'Stop Recording';
            
            try {
                const endpoint = isCurrentlyRecording ? '/api/recording/stop' : '/api/recording/start';
                const response = await fetch(endpoint, { method: 'POST' });
                
                const result = await response.json();
                if (result.success) {
                    if (isCurrentlyRecording) {
                        document.getElementById('recordBtn').textContent = 'Start Recording';
                        document.getElementById('recordBtn').className = 'btn btn-success';
                        document.getElementById('recordingIndicator').style.display = 'none';
                        document.getElementById('recordStatus').className = 'status-badge status-inactive';
                        showMessage(`Recording saved: ${result.filename}`, 'success');
                    } else {
                        document.getElementById('recordBtn').textContent = 'Stop Recording';
                        document.getElementById('recordBtn').className = 'btn btn-danger';
                        document.getElementById('recordingIndicator').style.display = 'flex';
                        document.getElementById('recordStatus').className = 'status-badge status-active';
                        showMessage('Recording started', 'success');
                    }
                } else {
                    showMessage(`Recording error: ${result.error}`, 'error');
                }
            } catch (error) {
                showMessage(`Network error: ${error.message}`, 'error');
            }
        }

        async function updateSystemStatus() {
            try {
                const response = await fetch('/api/system/status');
                const status = await response.json();
                
                if (status.success) {
                    document.getElementById('systemStatus').textContent = 
                        JSON.stringify(status.data, null, 2);
                } else {
                    document.getElementById('systemStatus').textContent = 
                        'Error loading status: ' + status.error;
                }
            } catch (error) {
                document.getElementById('systemStatus').textContent = 
                    'Network error: ' + error.message;
            }
        }

        function updateTimestamp() {
            const now = new Date();
            document.getElementById('timestamp').textContent = 
                now.toLocaleTimeString();
        }

        function showMessage(message, type) {
            const container = document.getElementById('messageContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = message;
            
            // Position at bottom right
            messageDiv.style.position = 'fixed';
            messageDiv.style.bottom = '20px';
            messageDiv.style.right = '20px';
            messageDiv.style.zIndex = '1000';
            messageDiv.style.minWidth = '300px';
            
            container.appendChild(messageDiv);
            
            setTimeout(() => {
                container.removeChild(messageDiv);
            }, 5000);
        }
    </script>
</body>
</html>
"""

class ProfessionalCamera:
    def __init__(self):
        self.camera = None
        self.frame_thread = None
        self.running = False
        
    def initialize(self):
        """Initialize camera with professional settings"""
        try:
            self.camera = Picamera2()
            
            # Professional configuration
            config = self.camera.create_video_configuration(
                main={
                    "format": CONFIG['camera']['format'],
                    "size": CONFIG['camera']['resolution']
                },
                lores={"format": "YUV420", "size": (640, 480)},  # For streaming
                display="lores"
            )
            
            self.camera.configure(config)
            self.camera.start()
            
            # Professional camera settings
            self.camera.set_controls({
                "AeEnable": True,
                "AwbEnable": True,
                "ExposureTime": 10000,
                "AnalogueGain": 1.0,
                "ColourGains": [1.0, 1.0],
                "Brightness": 0.0,
                "Contrast": 1.0,
                "Saturation": 1.0
            })
            
            time.sleep(2)  # Camera settle time
            
            # Start frame capture thread
            self.running = True
            self.frame_thread = threading.Thread(target=self._capture_frames, daemon=True)
            self.frame_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Camera initialization error: {e}")
            return False
    
    def _capture_frames(self):
        """Continuous frame capture for streaming"""
        global current_frame
        
        while self.running and self.camera is not None:
            try:
                with camera_lock:
                    if self.camera is not None:
                        frame = self.camera.capture_array()
                        
                        # Convert RGB to BGR for OpenCV
                        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        
                        # Encode as JPEG with professional quality
                        encode_params = [
                            cv2.IMWRITE_JPEG_QUALITY, CONFIG['streaming']['mjpeg_quality'],
                            cv2.IMWRITE_JPEG_PROGRESSIVE, 1,
                            cv2.IMWRITE_JPEG_OPTIMIZE, 1
                        ]
                        
                        ret, buffer = cv2.imencode('.jpg', frame_bgr, encode_params)
                        if ret:
                            current_frame = buffer.tobytes()
                
                time.sleep(1/CONFIG['camera']['framerate'])
                
            except Exception as e:
                print(f"Frame capture error: {e}")
                time.sleep(1)
    
    def stop(self):
        """Stop camera and cleanup"""
        self.running = False
        if self.camera is not None:
            try:
                self.camera.stop()
                self.camera.close()
                self.camera = None
            except Exception as e:
                print(f"Camera stop error: {e}")

# Global camera instance
pro_camera = ProfessionalCamera()

def create_directories():
    """Create necessary directories"""
    for path in CONFIG['paths'].values():
        Path(path).mkdir(parents=True, exist_ok=True)

def generate_frames():
    """Generator for MJPEG streaming"""
    while True:
        if current_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')
        time.sleep(1/CONFIG['camera']['framerate'])

# Flask Routes
@app.route('/')
def index():
    """Main interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/stream')
def stream():
    """MJPEG streaming endpoint"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/set_control', methods=['POST'])
def set_control():
    """Set single camera control"""
    try:
        data = request.get_json()
        if not data or 'control' not in data or 'value' not in data:
            return jsonify({'success': False, 'error': 'Invalid request'})
        
        control_name = data['control']
        control_value = data['value']
        
        with camera_lock:
            if pro_camera.camera is None:
                return jsonify({'success': False, 'error': 'Camera not initialized'})
            
            pro_camera.camera.set_controls({control_name: control_value})
            
        return jsonify({'success': True, 'message': f'Set {control_name} to {control_value}'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/preset/<preset_name>', methods=['POST'])
def apply_preset(preset_name):
    """Apply professional camera presets"""
    presets = {
        'broadcast': {
            'ExposureTime': 8333,  # 1/120s for broadcast
            'AnalogueGain': 2.0,
            'Contrast': 1.2,
            'Saturation': 1.1,
            'ColourGains': [1.1, 0.9]
        },
        'studio': {
            'ExposureTime': 16667,  # 1/60s for studio
            'AnalogueGain': 1.5,
            'Contrast': 1.0,
            'Saturation': 1.0,
            'ColourGains': [1.0, 1.0]
        },
        'outdoor': {
            'ExposureTime': 4000,   # 1/250s for outdoor
            'AnalogueGain': 1.0,
            'Contrast': 1.3,
            'Saturation': 1.2,
            'ColourGains': [0.9, 1.1]
        },
        'lowlight': {
            'ExposureTime': 33333,  # 1/30s for low light
            'AnalogueGain': 4.0,
            'Contrast': 0.9,
            'Saturation': 0.9,
            'ColourGains': [1.2, 0.8]
        },
        'reset': {
            'ExposureTime': 10000,
            'AnalogueGain': 1.0,
            'Contrast': 1.0,
            'Saturation': 1.0,
            'ColourGains': [1.0, 1.0],
            'AeEnable': True,
            'AwbEnable': True
        }
    }
    
    try:
        if preset_name not in presets:
            return jsonify({'success': False, 'error': 'Unknown preset'})
        
        preset_controls = presets[preset_name]
        
        with camera_lock:
            if pro_camera.camera is None:
                return jsonify({'success': False, 'error': 'Camera not initialized'})
            
            pro_camera.camera.set_controls(preset_controls)
        
        return jsonify({'success': True, 'message': f'Applied {preset_name} preset'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/streaming/rtmp/start', methods=['POST'])
def start_rtmp():
    """Start RTMP streaming"""
    global rtmp_process
    
    try:
        data = request.get_json()
        rtmp_url = data.get('url')
        
        if not rtmp_url:
            return jsonify({'success': False, 'error': 'RTMP URL required'})
        
        if rtmp_process and rtmp_process.poll() is None:
            return jsonify({'success': False, 'error': 'RTMP already running'})
        
        # FFmpeg command for RTMP streaming
        cmd = [
            'ffmpeg',
            '-f', 'mjpeg',
            '-r', str(CONFIG['camera']['framerate']),
            '-i', 'http://localhost:5000/stream',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-b:v', str(CONFIG['streaming']['h264_bitrate']),
            '-maxrate', str(CONFIG['streaming']['h264_bitrate']),
            '-bufsize', str(CONFIG['streaming']['h264_bitrate'] * 2),
            '-g', str(CONFIG['streaming']['keyframe_interval']),
            '-f', 'flv',
            rtmp_url
        ]
        
        rtmp_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return jsonify({'success': True, 'message': 'RTMP streaming started'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/streaming/rtmp/stop', methods=['POST'])
def stop_rtmp():
    """Stop RTMP streaming"""
    global rtmp_process
    
    try:
        if rtmp_process and rtmp_process.poll() is None:
            rtmp_process.terminate()
            rtmp_process.wait(timeout=5)
            rtmp_process = None
            return jsonify({'success': True, 'message': 'RTMP streaming stopped'})
        else:
            return jsonify({'success': False, 'error': 'RTMP not running'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/streaming/rtsp/start', methods=['POST'])
def start_rtsp():
    """Start RTSP server"""
    global rtsp_process
    
    try:
        if rtsp_process and rtsp_process.poll() is None:
            return jsonify({'success': False, 'error': 'RTSP already running'})
        
        # Start RTSP server using ffmpeg
        cmd = [
            'ffmpeg',
            '-f', 'mjpeg',
            '-r', str(CONFIG['camera']['framerate']),
            '-i', 'http://localhost:5000/stream',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-b:v', str(CONFIG['streaming']['h264_bitrate']),
            '-f', 'rtsp',
            'rtsp://0.0.0.0:8554/live'
        ]
        
        rtsp_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return jsonify({
            'success': True, 
            'message': 'RTSP server started',
            'url': 'rtsp://YOUR_PI_IP:8554/live'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/streaming/rtsp/stop', methods=['POST'])
def stop_rtsp():
    """Stop RTSP server"""
    global rtsp_process
    
    try:
        if rtsp_process and rtsp_process.poll() is None:
            rtsp_process.terminate()
            rtsp_process.wait(timeout=5)
            rtsp_process = None
            return jsonify({'success': True, 'message': 'RTSP server stopped'})
        else:
            return jsonify({'success': False, 'error': 'RTSP not running'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/recording/start', methods=['POST'])
def start_recording():
    """Start recording to file"""
    global recording_process, is_recording
    
    try:
        if recording_process and recording_process.poll() is None:
            return jsonify({'success': False, 'error': 'Recording already in progress'})
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.mp4"
        filepath = os.path.join(CONFIG['paths']['recordings'], filename)
        
        # FFmpeg command for recording
        cmd = [
            'ffmpeg',
            '-f', 'mjpeg',
            '-r', str(CONFIG['camera']['framerate']),
            '-i', 'http://localhost:5000/stream',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '18',  # High quality
            '-movflags', '+faststart',
            filepath
        ]
        
        recording_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        is_recording = True
        
        return jsonify({'success': True, 'message': 'Recording started', 'filename': filename})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/recording/stop', methods=['POST'])
def stop_recording():
    """Stop recording"""
    global recording_process, is_recording
    
    try:
        if recording_process and recording_process.poll() is None:
            recording_process.terminate()
            recording_process.wait(timeout=10)
            
            # Get the filename from the process
            filename = "recording_stopped.mp4"  # You might want to track this better
            
            recording_process = None
            is_recording = False
            
            return jsonify({'success': True, 'message': 'Recording stopped', 'filename': filename})
        else:
            return jsonify({'success': False, 'error': 'No recording in progress'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system/status')
def system_status():
    """Get comprehensive system status"""
    try:
        # Camera status
        camera_status = {
            'initialized': pro_camera.camera is not None,
            'running': pro_camera.running,
            'resolution': CONFIG['camera']['resolution'],
            'framerate': CONFIG['camera']['framerate']
        }
        
        # Get current controls if camera is available
        current_controls = {}
        if pro_camera.camera is not None:
            try:
                with camera_lock:
                    metadata = pro_camera.camera.capture_metadata()
                    json_safe_controls = [
                        'ExposureTime', 'AnalogueGain', 'ColourGains',
                        'AfMode', 'LensPosition', 'AeEnable', 'AwbEnable',
                        'Brightness', 'Contrast', 'Saturation'
                    ]
                    
                    for control in json_safe_controls:
                        if control in metadata:
                            value = metadata[control]
                            if isinstance(value, (int, float, bool, str, list)):
                                current_controls[control] = value
                                
            except Exception as e:
                current_controls = {'error': str(e)}
        
        # Streaming status
        streaming_status = {
            'mjpeg': True,  # Always available
            'rtmp': rtmp_process is not None and rtmp_process.poll() is None,
            'rtsp': rtsp_process is not None and rtsp_process.poll() is None,
            'recording': recording_process is not None and recording_process.poll() is None
        }
        
        # System info
        system_info = {
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time(),
            'recordings_path': CONFIG['paths']['recordings'],
        }
        
        return jsonify({
            'success': True,
            'data': {
                'camera': camera_status,
                'controls': current_controls,
                'streaming': streaming_status,
                'system': system_info
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/recordings')
def list_recordings():
    """List available recordings"""
    try:
        recordings_path = Path(CONFIG['paths']['recordings'])
        recordings = []
        
        if recordings_path.exists():
            for file in recordings_path.glob('*.mp4'):
                recordings.append({
                    'filename': file.name,
                    'size': file.stat().st_size,
                    'created': file.stat().st_ctime
                })
        
        return jsonify({'success': True, 'recordings': recordings})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def cleanup():
    """Cleanup all processes and camera"""
    global rtmp_process, rtsp_process, recording_process
    
    print("Cleaning up...")
    
    # Stop all streaming processes
    for process in [rtmp_process, rtsp_process, recording_process]:
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
    
    # Stop camera
    pro_camera.stop()

if __name__ == '__main__':
    try:
        print("🎥 Starting Professional GigE Camera System...")
        
        # Create directories
        create_directories()
        
        # Initialize camera
        if not pro_camera.initialize():
            print("❌ Failed to initialize camera")
            sys.exit(1)
        
        print("✅ Camera initialized successfully")
        print("🌐 Starting web server...")
        print("📱 Access the interface at: http://localhost:5000")
        print("📺 MJPEG stream available at: http://localhost:5000/stream")
        print("🎬 RTSP will be available at: rtsp://YOUR_PI_IP:8554/live")
        
        # Run Flask app
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    except KeyboardInterrupt:
        print("\n⏹️ Shutting down...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        
    finally:
        cleanup()