# LANCAM - Modular Flask Camera Application

A modular Flask application for camera control and streaming using Picamera2.

## Project Structure

```
LANCAM/
├─ app/
│  ├─ __init__.py         # Create and configure the Flask app
│  ├─ camera_routes.py    # All camera-related endpoints
│  ├─ control_routes.py   # Other device/control endpoints
│  └─ utils.py            # Helper functions (validation, camera setup)
├─ Frontend/
│  ├─ index.html          # Main UI
│  ├─ script.js           # Frontend JavaScript
│  ├─ style.css           # Styling
│  ├─ components/
│  │  ├─ navbar.html      # Navigation component
│  │  └─ footer.html      # Footer component
│  └─ images/
│     └─ power-button.png # UI assets
├─ extra/
│  ├─ server_original.py  # Original monolithic server file (backup)
│  └─ ...                 # Other experimental files
└─ main.py                # Application entry point
```

## Running the Application

```bash
# Navigate to project directory
cd /path/to/LANCAM

# Run the application
python3 main.py
```

The application will start on `http://0.0.0.0:5000`

## API Endpoints

### Camera Control
- `GET /stream` - MJPEG video stream
- `POST /api/camera/start` - Start the camera
- `POST /api/camera/stop` - Stop the camera
- `POST /api/camera/set` - Set camera configuration (width, height, fps)
- `POST /api/camera/set_focus` - Set focus mode and position
- `POST /api/camera/get_control_range` - Get control parameter ranges
- `GET /api/camera/status` - Get camera status

### UI Routes
- `GET /` - Main application interface

## Features

- **Modular Architecture**: Clean separation of concerns with blueprints
- **Camera Streaming**: Real-time MJPEG streaming
- **Camera Controls**: Focus, resolution, and frame rate controls
- **Input Validation**: Robust parameter validation with error handling
- **Thread Safety**: Proper locking for camera operations
- **Static File Serving**: Frontend assets served efficiently

## Development

The application uses Flask blueprints for modular organization:

- **app/__init__.py**: Application factory and camera initialization
- **app/camera_routes.py**: All camera-related API endpoints
- **app/control_routes.py**: UI and control endpoints
- **app/utils.py**: Validation and utility functions

## Dependencies

- Flask
- Picamera2
- Threading (built-in)
- IO (built-in)
