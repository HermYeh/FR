# Face Recognition Attendance System - Setup Instructions

## Prerequisites

- Python 3.8 or higher
- Webcam or USB camera
- Minimum 4GB RAM (8GB+ recommended for GPU acceleration)

## Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd FR
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

**For Production Use:**
```bash
pip install -r requirements.txt
```

**For Development:**
```bash
pip install -r requirements-dev.txt
```

### 4. GPU Support (Optional)

If you have a CUDA-compatible GPU, install PyTorch with CUDA support:
```bash
# For CUDA 11.7
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu117

# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For latest CUDA version, check: https://pytorch.org/get-started/locally/
```

## Running the Application

### Desktop Application
```bash
python face_recognition_attendance_ui.py
```

### Web Interface
```bash
python attendance_web_server.py
```

### Command Line Interface
```bash
python attendance_cli.py
```

### Combined System (Desktop + Web)
```bash
python start_combined_system.py
```

## Configuration

1. **Camera Settings**: Access through "System Settings" → "Camera" in the menu
2. **Recognition Settings**: Adjust detection thresholds and processing parameters
3. **Database**: SQLite database is created automatically on first run

## Troubleshooting

### Common Issues:

1. **Camera not detected**:
   - Check camera index in settings (usually 0 or 1)
   - Ensure no other applications are using the camera

2. **Poor face recognition accuracy**:
   - Ensure good lighting conditions
   - Adjust recognition threshold in settings
   - Capture multiple training images per person

3. **Performance issues**:
   - Enable GPU acceleration if available
   - Reduce camera resolution in settings
   - Increase face detection interval

4. **Virtual keyboard not working**:
   - Ensure tkinter is properly installed
   - Check display scaling settings

### Package Installation Issues:

**If you get errors installing PyTorch/facenet-pytorch:**
```bash
# Try installing PyTorch first
pip install torch torchvision
# Then install facenet-pytorch
pip install facenet-pytorch
```

**If opencv-python installation fails:**
```bash
# Try headless version
pip install opencv-python-headless
```

## System Requirements

### Minimum:
- CPU: Dual-core 2.0GHz
- RAM: 4GB
- Storage: 1GB free space
- Camera: USB 2.0 compatible

### Recommended:
- CPU: Quad-core 3.0GHz
- RAM: 8GB
- GPU: CUDA-compatible (GTX 1060 or better)
- Storage: 5GB free space
- Camera: USB 3.0 with 720p+ resolution

## Files Overview

- `face_recognition_attendance_ui.py` - Main desktop application
- `attendance_web_server.py` - Web interface
- `attendance_cli.py` - Command line interface
- `camera_config.json` - Camera and processing settings
- `attendance.db` - SQLite database (created automatically)
- `known_faces/` - Directory for training images
- `checkin_photos/` - Directory for check-in photos