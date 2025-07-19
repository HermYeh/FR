import cv2
import numpy as np
import time
import gc
from PIL import Image, ImageTk
from collections import deque
from typing import Optional
from camera_config import camera_config

class CameraHandler:
    """Handles camera operations and video processing"""
    
    def __init__(self):
        self.camera = None
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.canvas_size = None
        self.current_frame_tk = None
        self.last_display_frame: Optional[np.ndarray] = None
        self.video_paused = False
        
        # Face tracking for persistent recognition
        self.tracked_faces = {}
        self.face_track_id = 0
        self.current_frame_faces = []
        
        # Load dynamic configuration
        self.update_config()
    
    def update_config(self):
        """Update configuration from camera_config"""
        self.target_fps = camera_config.get("target_fps", 10)
        self.frame_interval = 1000 // self.target_fps
        self.face_detection_interval = camera_config.get("face_detection_interval", 5)
        self.face_cache = deque(maxlen=camera_config.get("face_cache_size", 10))
        self.max_track_distance = camera_config.get("max_track_distance", 50)
        self.track_timeout = camera_config.get("track_timeout", 30)
        
        # Update frame interval when FPS changes
        self.frame_interval = 1000 // self.target_fps
        
        print(f"📷 Camera config updated: FPS={self.target_fps}, Detection Interval={self.face_detection_interval}")
    
    def start_camera_optimized(self):
        """Start camera with optimized settings"""
        try:
            # Try primary camera first, then fallback
            camera_index = camera_config.get("camera_index", 0)
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                # Try alternative camera
                alt_index = 1 if camera_index == 0 else 0
                self.camera = cv2.VideoCapture(alt_index)
                if not self.camera.isOpened():
                    return False
            
            # Apply dynamic camera settings
            cam_props = camera_config.get_camera_properties()
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, cam_props["width"])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_props["height"])
            self.camera.set(cv2.CAP_PROP_FPS, cam_props["fps"])
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, cam_props["buffer_size"])
            self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, cam_props["auto_exposure"])
            
            # Apply additional camera properties if supported
            try:
                if cam_props["brightness"] != 0:
                    self.camera.set(cv2.CAP_PROP_BRIGHTNESS, cam_props["brightness"])
                if cam_props["contrast"] != 0:
                    self.camera.set(cv2.CAP_PROP_CONTRAST, cam_props["contrast"])
                if cam_props["saturation"] != 0:
                    self.camera.set(cv2.CAP_PROP_SATURATION, cam_props["saturation"])
                if cam_props["gain"] != 0:
                    self.camera.set(cv2.CAP_PROP_GAIN, cam_props["gain"])
            except Exception as e:
                print(f"Some camera properties not supported: {e}")
            
            print(f"✅ Camera started with settings: {cam_props['width']}x{cam_props['height']} @ {cam_props['fps']}fps")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start camera: {e}")
            return False
    
    def get_cached_faces(self, frame, face_processor):
        """Get faces with intelligent caching"""
        # Use cached faces if available and recent
        if len(self.face_cache) > 0 and self.frame_count % self.face_detection_interval != 0:
            return self.face_cache[-1] if self.face_cache else []
        
        # Detect new faces
        faces = face_processor.detect_faces_optimized(frame)
        
        # Cache the result
        self.face_cache.append(faces)
        
        return faces
    
    def display_frame_optimized(self, frame, canvas, root):
        """Optimized frame display with better memory management"""
        try:
            # Validate frame
            if frame is None or frame.size == 0:
                return
            
            # Cache canvas size with validation
            if not self.canvas_size:
                win_w = root.winfo_width()
                win_h = root.winfo_height()
                
                # Ensure minimum window size
                if win_w <= 0 or win_h <= 0:
                    return  # Window not ready yet
                
                self.canvas_size = (win_w, win_h)
            
            win_w, win_h = self.canvas_size
            
            # Validate window dimensions
            if win_w <= 0 or win_h <= 0:
                return
            
            # Convert and resize efficiently
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            
            # Validate frame dimensions
            if frame_pil.width <= 0 or frame_pil.height <= 0:
                return
            
            # Calculate optimal size with validation
            frame_aspect = frame_pil.width / frame_pil.height
            window_aspect = win_w / win_h
            
            if frame_aspect > window_aspect:
                new_width = win_w
                new_height = int(win_w / frame_aspect)
            else:
                new_height = win_h
                new_width = int(win_h * frame_aspect)
            
            # Ensure minimum dimensions
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            
            # Validate final dimensions
            if new_width <= 0 or new_height <= 0:
                return
            
            # Resize with optimized method
            frame_pil = frame_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            frame_tk = ImageTk.PhotoImage(frame_pil)
            
            # Update canvas
            canvas.delete("all")
            x_offset = (win_w - new_width) // 2
            y_offset = (win_h - new_height) // 2
            canvas.create_image(x_offset, y_offset, anchor='nw', image=frame_tk)
            
            # Keep reference
            self.current_frame_tk = frame_tk
            
        except Exception as e:
            print(f"Display error: {e}")
    
    def calculate_rectangle_distance(self, rect1, rect2):
        """Calculate distance between two rectangles (center-to-center)"""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        # Calculate centers
        center1_x = x1 + w1 // 2
        center1_y = y1 + h1 // 2
        center2_x = x2 + w2 // 2
        center2_y = y2 + h2 // 2
        
        # Euclidean distance
        distance = ((center1_x - center2_x) ** 2 + (center1_y - center2_y) ** 2) ** 0.5
        return distance
    
    def match_faces_to_tracks(self, current_faces):
        """Match current face rectangles to existing tracks"""
        matched_pairs = []
        unmatched_faces = list(range(len(current_faces)))
        unmatched_tracks = list(self.tracked_faces.keys())
        
        # Find best matches based on distance
        for face_idx, face_rect in enumerate(current_faces):
            best_track_id = None
            best_distance = float('inf')
            
            for track_id in unmatched_tracks:
                track_data = self.tracked_faces[track_id]
                track_rect = track_data['rectangle']
                
                distance = self.calculate_rectangle_distance(face_rect, track_rect)
                
                if distance < self.max_track_distance and distance < best_distance:
                    best_distance = distance
                    best_track_id = track_id
            
            if best_track_id is not None:
                matched_pairs.append((face_idx, best_track_id))
                unmatched_faces.remove(face_idx)
                unmatched_tracks.remove(best_track_id)
        
        return matched_pairs, unmatched_faces, unmatched_tracks
    
    def update_face_tracking(self, current_faces, face_names):
        """Update face tracking data with current frame information"""
        # Match current faces to existing tracks
        matched_pairs, unmatched_faces, unmatched_tracks = self.match_faces_to_tracks(current_faces)
        
        # Update matched tracks
        for face_idx, track_id in matched_pairs:
            track_data = self.tracked_faces[track_id]
            track_data['rectangle'] = current_faces[face_idx]
            track_data['last_seen'] = self.frame_count
            
            # Update name if recognition was successful
            if face_idx < len(face_names) and face_names[face_idx] != "Unknown":
                track_data['name'] = face_names[face_idx]
                boost_factor = camera_config.get("confidence_boost_factor", 0.1)
                track_data['confidence'] = min(track_data['confidence'] + boost_factor, 1.0)  # Increase confidence
            else:
                decay_factor = camera_config.get("confidence_decay_factor", 0.05)
                track_data['confidence'] = max(track_data['confidence'] - decay_factor, 0.1)  # Decrease confidence
        
        # Create new tracks for unmatched faces
        for face_idx in unmatched_faces:
            self.face_track_id += 1
            track_id = self.face_track_id
            
            name = face_names[face_idx] if face_idx < len(face_names) else "Unknown"
            confidence = 0.8 if name != "Unknown" else 0.1
            
            self.tracked_faces[track_id] = {
                'rectangle': current_faces[face_idx],
                'name': name,
                'confidence': confidence,
                'last_seen': self.frame_count,
                'created_frame': self.frame_count
            }
        
        # Remove old tracks that haven't been seen
        tracks_to_remove = []
        for track_id in unmatched_tracks:
            track_data = self.tracked_faces[track_id]
            if self.frame_count - track_data['last_seen'] > self.track_timeout:
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.tracked_faces[track_id]
    
    def get_tracked_face_info(self, face_rect):
        """Get tracking information for a face rectangle"""
        for track_id, track_data in self.tracked_faces.items():
            if self.calculate_rectangle_distance(face_rect, track_data['rectangle']) < 10:
                return track_data['name'], track_data['confidence']
        return "Unknown", 0.0
    
    def draw_face_with_tracking(self, frame, x, y, w, h, name, confidence, track_id=None):
        """Draw face rectangle with tracking information"""
        # Choose color based on recognition confidence
        if name != "Unknown" and confidence > 0.7:
            color = (0, 255, 0)  # Green for high confidence
        elif name != "Unknown" and confidence > 0.3:
            color = (0, 255, 255)  # Yellow for medium confidence
        else:
            color = (255, 0, 0)  # Blue for unknown/low confidence
        
        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        # Display name and confidence
        confidence_text = f"{round(confidence * 100)}%"
        cv2.putText(frame, name, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, confidence_text, (x+5, y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        
        # Display track ID if available
        if track_id is not None:
            cv2.putText(frame, f"ID:{track_id}", (x+w-40, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
    
    def cleanup_camera(self):
        """Clean up camera resources"""
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()
    
    def get_frame(self):
        """Get current frame from camera"""
        if not self.camera:
            return None, None
        
        try:
            ret, frame = self.camera.read()
            if ret and frame is not None:
                # Apply dynamic frame rotation
                rotation = camera_config.get("frame_rotation", "90_ccw")
                if rotation == "90_ccw":
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                elif rotation == "90_cw":
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                elif rotation == "180":
                    frame = cv2.rotate(frame, cv2.ROTATE_180)
                # "none" - no rotation
                
                # Validate frame dimensions
                if frame.shape[0] > 0 and frame.shape[1] > 0:
                    return ret, frame
            
            return False, None
            
        except Exception as e:
            print(f"Error getting frame: {e}")
            return False, None
    
    def is_time_for_next_frame(self):
        """Check if it's time for the next frame based on target FPS"""
        current_time = time.time()
        if (current_time - self.last_frame_time) < (self.frame_interval / 1000.0):
            return False
        
        self.last_frame_time = current_time
        self.frame_count += 1
        return True
    
    def should_process_face_detection(self):
        """Check if face detection should be processed this frame"""
        return self.frame_count % self.face_detection_interval == 0
    
    def cleanup_memory(self):
        """Perform memory cleanup"""
        cleanup_interval = camera_config.get("memory_cleanup_interval", 10)
        if self.frame_count % cleanup_interval == 0:
            gc.collect()
            # Reset canvas size cache to handle window resizing
            self.canvas_size = None 

    def apply_config_changes(self):
        """Apply configuration changes and restart camera if needed"""
        try:
            print("🔄 Applying camera configuration changes...")
            
            # Update internal configuration
            old_fps = self.target_fps
            old_resolution = (camera_config.get("frame_width", 640), camera_config.get("frame_height", 480))
            
            self.update_config()
            
            # Check if camera restart is needed
            new_resolution = (camera_config.get("frame_width", 640), camera_config.get("frame_height", 480))
            restart_needed = (old_fps != self.target_fps or old_resolution != new_resolution)
            
            if restart_needed and self.camera is not None:
                print("📹 Restarting camera with new settings...")
                self.cleanup_camera()
                success = self.start_camera_optimized()
                if success:
                    print("✅ Camera restarted successfully with new configuration")
                    return True
                else:
                    print("❌ Failed to restart camera with new settings")
                    return False
            else:
                print("✅ Configuration updated (no camera restart needed)")
                return True
                
        except Exception as e:
            print(f"❌ Error applying camera configuration: {e}")
            return False 