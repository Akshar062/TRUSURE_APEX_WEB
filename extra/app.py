#!/usr/bin/env python3
"""
Flask + Picamera2 MJPEG preview + full web UI for manual/auto controls

Features:
 - MJPEG preview at /stream and an interactive single-file HTML UI at /
 - REST API to set controls: exposure_time (µs), analogue_gain, lens_position (0..1), awb_gains ([r,b]), awb_mode ('auto'/'off'), autofocus ('auto'/'off'), focus (absolute float if supported)
 - Status endpoint to inspect current/last-applied controls
 - Graceful errors when a control is unsupported by the camera

How to run (on Raspberry Pi with libcamera + Picamera2 installed):
  sudo apt update
  sudo apt install -y python3-pip
  pip3 install flask picamera2 pillow numpy
  sudo python3 flask_picamera2_server.py

Open http://<raspberry-pi-ip>:5000/ in your browser.

Notes:
 - Different camera modules expose different libcamera controls. This server accepts friendly keys and will forward them to Picamera2.set_controls(). If the camera doesn't support a control, Picamera2 will raise — the API returns the error so you can see what failed.
 - For better performance on high resolutions you should adapt the preview configuration or use hardware MJPEG encoding.
"""

from flask import Flask, Response, render_template_string, request, jsonify
from picamera2 import Picamera2
from PIL import Image
import io
import threading
import time
import numpy as np

app = Flask(__name__)

# ===== CAMERA SETUP =====
picam2 = Picamera2()
# Preview size — adjust for performance / quality
PREVIEW_SIZE = (1280, 720)
preview_config = picam2.create_preview_configuration({"size": PREVIEW_SIZE})
picam2.configure(preview_config)

# Start camera
picam2.start()

# Lock to protect camera operations
cam_lock = threading.Lock()

# ===== HTML UI =====
HTML_PAGE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Picamera2 Flask — Preview & Controls</title>
    <style>
      body{font-family:Inter, Arial, sans-serif; margin:18px}
      .row{display:flex; gap:18px}
      .panel{border:1px solid #ddd;padding:12px;border-radius:8px}
      img#stream{max-width:100%;height:auto;border-radius:6px}
      label{display:block;margin-top:8px;font-size:14px}
      input[type=range]{width:320px}
      .small{font-size:12px;color:#444}
      button{margin-top:8px;padding:6px 12px;border-radius:6px}
    </style>
  </head>
  <body>
    <h1>Picamera2 Preview</h1>
    <div class="row">
      <div class="panel">
        <img id="stream" src="/stream" alt="camera stream" />
      </div>
      <div class="panel" style="min-width:360px">
        <h2>Controls</h2>

        <label>Exposure time (µs): <input id="exposure" type="number" value="0"/></label>
        <label>Analogue gain: <input id="gain" type="number" step="0.1" value="0"/></label>
        <label>Lens position (0.0-1.0): <input id="lens" type="number" step="0.01" value="0"/></label>
        <label>AF focus (absolute): <input id="focus" type="number" step="0.01" value="0"/></label>
        <label>AWB gains R,B: <input id="awb_r" type="number" step="0.01" value="0"/> , <input id="awb_b" type="number" step="0.01" value="0"/></label>

        <div style="margin-top:8px">
          <button onclick="applyControls()">Apply Manual Controls</button>
          <button onclick="setAutoAwb()">Enable AWB Auto</button>
          <button onclick="disableAutoAwb()">Disable AWB Auto</button>
        </div>

        <div style="margin-top:12px">
          <button onclick="setAutofocus('auto')">Enable Autofocus</button>
          <button onclick="setAutofocus('off')">Disable Autofocus</button>
        </div>

        <h3 style="margin-top:12px">Status</h3>
        <pre id="status" class="small">Loading...</pre>
      </div>
    </div>

    <script>
      async function applyControls(){
        const body = {};
        const exposure = parseInt(document.getElementById('exposure').value) || 0;
        const gain = parseFloat(document.getElementById('gain').value) || 0;
        const lens = parseFloat(document.getElementById('lens').value) || 0;
        const focus = parseFloat(document.getElementById('focus').value) || 0;
        const awb_r = parseFloat(document.getElementById('awb_r').value) || 0;
        const awb_b = parseFloat(document.getElementById('awb_b').value) || 0;

        if(exposure>0) body['exposure_time'] = exposure;
        if(gain>0) body['analogue_gain'] = gain;
        if(!Number.isNaN(lens)) body['lens_position'] = lens;
        if(!Number.isNaN(focus)) body['focus'] = focus;
        if(awb_r>0 || awb_b>0) body['awb_gains'] = [awb_r, awb_b];

        const r = await fetch('/api/control', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
        const j = await r.json();
        document.getElementById('status').innerText = JSON.stringify(j, null, 2);
      }

      async function setAutoAwb(){
        const r = await fetch('/api/control', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({'awb_mode':'auto'})});
        const j = await r.json();
        document.getElementById('status').innerText = JSON.stringify(j, null, 2);
      }

      async function disableAutoAwb(){
        const r = await fetch('/api/control', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({'awb_mode':'off'})});
        const j = await r.json();
        document.getElementById('status').innerText = JSON.stringify(j, null, 2);
      }

      async function setAutofocus(mode){
        const r = await fetch('/api/control', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({'autofocus': mode})});
        const j = await r.json();
        document.getElementById('status').innerText = JSON.stringify(j, null, 2);
      }

      async function refreshStatus(){
        try{
          const r = await fetch('/api/status');
          const j = await r.json();
          document.getElementById('status').innerText = JSON.stringify(j, null, 2);
        }catch(e){
          document.getElementById('status').innerText = String(e);
        }
      }

      setInterval(refreshStatus, 1500);
      refreshStatus();
    </script>
  </body>
</html>
"""

# ===== MJPEG generator =====

def jpeg_generator():
    """Yield MJPEG frames captured from Picamera2."""
    try:
        while True:
            with cam_lock:
                arr = picam2.capture_array()
            # convert array BGR/RGB -> JPEG
            img = Image.fromarray(arr)
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=85)
            jpg = buf.getvalue()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')
            # throttle
            time.sleep(0.03)
    except GeneratorExit:
        return


# ===== HELPERS =====

def apply_controls_safely(controls):
    """Attempt to apply controls and return a tuple (ok:bool, message/dict).
       Catch exceptions from Picamera2 and return them as error details.
    """
    try:
        with cam_lock:
            picam2.set_controls(controls)
        # return last-applied controls if get_controls is available
        last = {}
        try:
            if hasattr(picam2, 'get_controls'):
                last = picam2.get_controls()
        except Exception:
            last = {}
        return True, {'applied': controls, 'current': last}
    except Exception as e:
        return False, {'error': str(e), 'attempted': controls}


# ===== ROUTES =====

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)


@app.route('/stream')
def stream():
    return Response(jpeg_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/control', methods=['POST'])
def api_control():
    body = request.get_json(force=True)
    if not body:
        return jsonify({'error': 'no json provided'}), 400

    controls = {}
    # friendly keys -> libcamera control names
    if 'exposure_time' in body:
        try:
            controls['ExposureTime'] = int(body['exposure_time'])
        except Exception:
            return jsonify({'error': 'exposure_time must be integer microseconds'}), 400

    if 'analogue_gain' in body:
        try:
            controls['AnalogueGain'] = float(body['analogue_gain'])
        except Exception:
            return jsonify({'error': 'analogue_gain must be numeric'}), 400

    if 'lens_position' in body:
        try:
            controls['LensPosition'] = float(body['lens_position'])
        except Exception:
            return jsonify({'error': 'lens_position must be float 0..1'}), 400

    # autofocus control request
    if 'autofocus' in body:
        # try common control names for autofocus; many cameras don't support AF
        mode = body['autofocus']
        if mode == 'auto':
            # try a few possible AF control names
            controls['AfMode'] = 1  # some drivers use integers for modes
            # also try enabling AutoFocus via 'AfEnable' or 'AutoFocus'
            controls['AfEnable'] = True
        elif mode == 'off':
            controls['AfEnable'] = False

    # absolute focus (if supported)
    if 'focus' in body:
        try:
            controls['Focus'] = float(body['focus'])
        except Exception:
            controls['Focus'] = body['focus']

    # AWB
    if 'awb_gains' in body:
        g = body['awb_gains']
        if isinstance(g, (list, tuple)) and len(g) == 2:
            try:
                controls['AwbGains'] = (float(g[0]), float(g[1]))
            except Exception:
                return jsonify({'error': 'awb_gains must be two numbers [r,b]'}), 400

    if 'awb_mode' in body:
        if body['awb_mode'] == 'auto':
            # some cameras use 'AwbEnable'
            controls['AwbEnable'] = True
        else:
            controls['AwbEnable'] = False

    # direct raw controls passthrough
    if 'controls' in body and isinstance(body['controls'], dict):
        controls.update(body['controls'])

    if not controls:
        return jsonify({'error': 'no known controls provided'}), 400

    ok, result = apply_controls_safely(controls)
    if ok:
        return jsonify({'status': 'ok', 'result': result})
    else:
        return jsonify({'status': 'error', 'result': result}), 500


@app.route('/api/status')
def api_status():
    info = {'preview_size': PREVIEW_SIZE}
    # try to fetch last-applied controls if supported
    try:
        if hasattr(picam2, 'get_controls'):
            info['controls'] = picam2.get_controls()
    except Exception:
        info['controls'] = {}

    # include camera configuration if available
    try:
        info['camera_config'] = picam2.camera_config if hasattr(picam2, 'camera_config') else {}
    except Exception:
        info['camera_config'] = {}

    return jsonify(info)


if __name__ == '__main__':
    # Run Flask
    app.run(host='0.0.0.0', port=5000, threaded=True)
