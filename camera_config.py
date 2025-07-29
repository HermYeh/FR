import json
import os
from typing import Dict, Any

class CameraConfig:
    """Manages camera and face processing configuration settings"""
    
    def __init__(self):
        self.config_file = "camera_config.json"
        self.config = self.load_default_config()
        self.load_config()
    
    def load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values"""
        return {
            # Camera Hardware Settings
            "camera_index": 0,
            "frame_width": 640,
            "frame_height": 480,
            "target_fps": 20,
            "buffer_size": 1,
            "auto_exposure": 0.25,
            "brightness": 0,  # OpenCV default
            "contrast": 0,    # OpenCV default
            "saturation": 0,  # OpenCV default
            "gain": 0,        # OpenCV default
            
            # Video Processing Settings
            "face_detection_interval": 5,
            "face_cache_size": 10,
            "frame_rotation": "90_ccw",  # 90_ccw, 90_cw, 180, none
            "flip_horizontal": True,    # Horizontal mirror flip
            "flip_vertical": False,      # Vertical flip
            
            # Face Tracking Settings
            "max_track_distance": 50,
            "track_timeout": 30,
            "tracking_enabled": True,
            
            # Face Detection Settings (MTCNN)
            "min_face_size": 30,
            "detection_scale_factor": 0.5,
            "mtcnn_threshold_1": 0.7,
            "mtcnn_threshold_2": 0.8,
            "mtcnn_threshold_3": 0.8,
            "detection_confidence_threshold": 0.8,
            "min_face_region_size": 20,
            
            # Face Recognition Settings
            "recognition_threshold": 0.7,
            "recognition_interval": 3,  # Process every Nth frame
            "embedding_cache_size": 100,
            "confidence_boost_factor": 0.1,
            "confidence_decay_factor": 0.05,
            
            # Performance Settings
            "memory_cleanup_interval": 10,
            "enable_gpu": True,
            "image_quality": "medium"  # low, medium, high
        }
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in saved_config.items():
                        if key in self.config:
                            self.config[key] = value
                print(f"✅ Camera configuration loaded from {self.config_file}")
            else:
                print(f"ℹ️  Using default camera configuration")
                self.save_config()  # Save defaults
        except Exception as e:
            print(f"❌ Error loading camera config: {e}")
            print("Using default configuration")
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            # Ensure the config directory exists
            os.makedirs(os.path.dirname(self.config_file) if os.path.dirname(self.config_file) else '.', exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"✅ Camera configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving camera config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        if key in self.config:
            self.config[key] = value
            return True
        return False
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update multiple configuration values"""
        try:
            for key, value in new_config.items():
                if key in self.config:
                    self.config[key] = value
            return True
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = self.load_default_config()
        self.save_config()
    
    def get_camera_properties(self) -> Dict[str, Any]:
        """Get camera-specific properties for OpenCV"""
        return {
            "width": self.config["frame_width"],
            "height": self.config["frame_height"],
            "fps": self.config["target_fps"],
            "buffer_size": self.config["buffer_size"],
            "auto_exposure": self.config["auto_exposure"],
            "brightness": self.config["brightness"],
            "contrast": self.config["contrast"],
            "saturation": self.config["saturation"],
            "gain": self.config["gain"]
        }
    
    def get_mtcnn_config(self) -> Dict[str, Any]:
        """Get MTCNN-specific configuration"""
        return {
            "min_face_size": self.config["min_face_size"],
            "thresholds": [
                self.config["mtcnn_threshold_1"],
                self.config["mtcnn_threshold_2"],
                self.config["mtcnn_threshold_3"]
            ],
            "factor": 0.709,  # Standard MTCNN factor
            "detection_threshold": self.config["detection_confidence_threshold"]
        }
    
    def get_tracking_config(self) -> Dict[str, Any]:
        """Get face tracking configuration"""
        return {
            "enabled": self.config["tracking_enabled"],
            "max_distance": self.config["max_track_distance"],
            "timeout": self.config["track_timeout"]
        }
    
    def validate_config(self) -> bool:
        """Validate configuration values"""
        validators = {
            "frame_width": lambda x: 160 <= x <= 1920,
            "frame_height": lambda x: 120 <= x <= 1080,
            "target_fps": lambda x: 1 <= x <= 60,
            "buffer_size": lambda x: 1 <= x <= 10,
            "auto_exposure": lambda x: 0.0 <= x <= 1.0,
            "face_detection_interval": lambda x: 1 <= x <= 30,
            "min_face_size": lambda x: 10 <= x <= 320,
            "recognition_threshold": lambda x: 0.1 <= x <= 1.0,
            "detection_confidence_threshold": lambda x: 0.1 <= x <= 1.0,
        }
        
        for key, validator in validators.items():
            if key in self.config and not validator(self.config[key]):
                print(f"❌ Invalid value for {key}: {self.config[key]}")
                return False
        
        return True
    
    def get_config_description(self, key: str) -> str:
        """Get human-readable description for configuration keys"""
        descriptions = {
            # Camera Hardware
            "camera_index": "Camera device index (0=default, 1=external)",
            "frame_width": "Camera frame width in pixels (160-1920)",
            "frame_height": "Camera frame height in pixels (120-1080)",
            "target_fps": "Target frames per second (1-60)",
            "buffer_size": "Camera buffer size (1-10)",
            "auto_exposure": "Auto exposure setting (0.0-1.0)",
            "brightness": "Camera brightness adjustment (-100 to 100)",
            "contrast": "Camera contrast adjustment (-100 to 100)",
            "saturation": "Camera saturation adjustment (-100 to 100)",
            "gain": "Camera gain adjustment (0-100)",
            
            # Video Processing
            "face_detection_interval": "Face detection frequency (every N frames)",
            "face_cache_size": "Number of cached face detections",
            "frame_rotation": "Frame rotation (90_ccw, 90_cw, 180, none)",
            "flip_horizontal": "Mirror flip video horizontally (true/false)",
            "flip_vertical": "Flip video vertically (true/false)",
            
            # Face Tracking
            "max_track_distance": "Maximum distance for face tracking",
            "track_timeout": "Frames before dropping lost tracks",
            "tracking_enabled": "Enable face tracking across frames",
            
            # Face Detection
            "min_face_size": "Minimum face size for detection (pixels)",
            "detection_scale_factor": "Scale factor for detection (0.1-1.0)",
            "mtcnn_threshold_1": "MTCNN stage 1 threshold (0.1-1.0)",
            "mtcnn_threshold_2": "MTCNN stage 2 threshold (0.1-1.0)",
            "mtcnn_threshold_3": "MTCNN stage 3 threshold (0.1-1.0)",
            "detection_confidence_threshold": "Detection confidence threshold",
            "min_face_region_size": "Minimum face region size (pixels)",
            
            # Face Recognition
            "recognition_threshold": "Recognition confidence threshold",
            "recognition_interval": "Recognition frequency (every N frames)",
            "embedding_cache_size": "Size of embedding cache",
            "confidence_boost_factor": "Confidence increase rate",
            "confidence_decay_factor": "Confidence decrease rate",
            
            # Performance
            "memory_cleanup_interval": "Memory cleanup frequency (frames)",
            "enable_gpu": "Use GPU acceleration if available",
            "image_quality": "Processing quality (low/medium/high)"
        }
        return descriptions.get(key, "Configuration parameter")

# Global instance
camera_config = CameraConfig() 