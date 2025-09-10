import io
import time
import threading
from flask import Flask, Response, request, jsonify, send_from_directory
from picamera2 import Picamera2


app = Flask(__name__, static_folder="Frontend", static_url_path="")

# --- Camera Setup ---
picam2 = Picamera2()
sensorSize = picam2.sensor_resolution
preview_config = picam2.create_video_configuration(
    main={"size": (sensorSize[0] // 4, sensorSize[1] // 4)},
)
picam2.configure(preview_config)
picam2.start()

lock = threading.Lock()


# --- Serve UI (index.html + static files) ---
@app.route("/")
def index():
    return send_from_directory("Frontend", "index.html")


# --- MJPEG Preview Stream ---
@app.route("/stream")
def stream():
    def generate():
        while True:
            with lock:
                buf = io.BytesIO()
                picam2.capture_file(buf, format="jpeg")
                buf.seek(0)
                frame = buf.getvalue()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(0.03)  # ~30 fps
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


# --- get camera controls range ---
@app.route("/api/camera/get_control_range", methods=["POST"])
def get_control_range():
    data = request.json or {}
    control_name = data.get("control_name", "")
    if not control_name:
        return jsonify({"success": False, "message": "No control name provided"}), 400

    with lock:
        controls = picam2.camera_controls
        if control_name not in controls:
            return jsonify({"success": False, "message": f"Control '{control_name}' not found"}), 404

        min_val, max_val, default_val = controls[control_name]

        return jsonify({
            "success": True,
            "min": min_val,
            "max": max_val,
            "current": default_val
        })
    
# --- set camera control value ---
@app.route("/api/camera/set_focus", methods=["POST"])
def set_focus():
    data = request.json or {}
    mode = data.get("mode", "auto")       # "auto" or "manual"
    position = data.get("position", 0.0)  # float between 0.0 and 1.0

    with lock:
        try:
            picam2.set_controls({"AfMode": 0})
            if mode == "manual":
                picam2.set_controls({"LensPosition": float(position)})
            return jsonify({"success": True, "message": f"Focus set to {mode} / {position}"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        

# --- Camera Control Endpoints ---
@app.route("/api/camera/start", methods=["POST"])
def start_camera():
    with lock:
        if not picam2.started:
            picam2.start()
    return jsonify({"success": True, "message": "Camera started"})


@app.route("/api/camera/stop", methods=["POST"])
def stop_camera():
    with lock:
        if picam2.started:
            picam2.stop()
    return jsonify({"success": True, "message": "Camera stopped"})


@app.route("/api/camera/set", methods=["POST"])
def set_camera():
    data = request.json or {}
    width = int(data.get("width", 640))
    height = int(data.get("height", 480))
    fps = int(data.get("fps", 30))

    with lock:
        config = picam2.create_video_configuration(
            main={"size": (width, height)},
            controls={"FrameRate": fps},
        )
        picam2.stop()
        picam2.configure(config)
        picam2.start()

    return jsonify({"success": True, "message": "Camera settings updated"})


@app.route("/api/camera/status")
def status():
    return jsonify({
        "started": picam2.started,
        "resolution": picam2.camera_configuration()["main"]["size"],
    })


# --- Run App with LiveReload ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

