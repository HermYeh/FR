import cv2
import numpy as np
import torch
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import time
from camera_config import camera_config

# FaceNet imports
FACENET_AVAILABLE = False
try:
    from facenet_pytorch import MTCNN, InceptionResnetV1
    FACENET_AVAILABLE = True
    print("FaceNet modules loaded successfully")
except ImportError:
    FACENET_AVAILABLE = False
    print("FaceNet not available. Install with: pip install facenet-pytorch torch scikit-learn")

class FaceProcessor:
    """Handles face detection, recognition, and embedding operations"""
    
    def __init__(self):
        self.mtcnn = None
        self.facenet_model = None
        self.face_embeddings = {}
        self.embedding_cache = {}
        
    def initialize_face_recognition_optimized(self):
        """Optimized FaceNet initialization"""
        if not FACENET_AVAILABLE:
            return False
        
        try:
            # Use GPU if enabled and available
            use_gpu = camera_config.get("enable_gpu", True)
            device = torch.device('cuda' if (torch.cuda.is_available() and use_gpu) else 'cpu')
            print(f"Using device: {device}")
            
            # Dynamic MTCNN settings
            mtcnn_config = camera_config.get_mtcnn_config()
            self.mtcnn = MTCNN(
                image_size=160,
                margin=0,
                min_face_size=mtcnn_config["min_face_size"],
                thresholds=mtcnn_config["thresholds"],
                factor=mtcnn_config["factor"],
                post_process=True,
                device=device,
                keep_all=False  # Keep only best face for better performance
            )
            
            # Initialize FaceNet model
            self.facenet_model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
            
            self.load_face_embeddings()
            print(f"✅ FaceNet initialized: Device={device}, Min Face Size={mtcnn_config['min_face_size']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize FaceNet: {e}")
            return False
    
    def detect_faces_optimized(self, frame):
        """Optimized face detection with MTCNN"""
        try:
            if not self.mtcnn:
                return []
            
            # Dynamic scale factor for faster processing
            scale_factor = camera_config.get("detection_scale_factor", 0.5)
            small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
            
            # Convert to PIL
            frame_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            
            # Detect faces
            with torch.no_grad():
                detection_result = self.mtcnn.detect(frame_pil)
            
            faces = []
            if detection_result and len(detection_result) >= 2:
                boxes, probs = detection_result[0], detection_result[1]
                if boxes is not None and probs is not None:
                    # Dynamic detection threshold
                    detection_threshold = camera_config.get("detection_confidence_threshold", 0.8)
                    for box, prob in zip(boxes, probs):
                        if prob > detection_threshold:
                            # Scale back to original size
                            x, y, x2, y2 = (box / scale_factor).astype(int)
                            w, h = x2 - x, y2 - y
                            
                            # Validate coordinates
                            if self.is_valid_face_region(x, y, w, h, frame.shape):
                                faces.append((x, y, w, h))
            
            return faces
            
        except Exception as e:
            print(f"Face detection error: {e}")
            return []
    
    def is_valid_face_region(self, x, y, w, h, frame_shape):
        """Validate face region coordinates"""
        frame_height, frame_width = frame_shape[:2]
        min_size = camera_config.get("min_face_region_size", 20)
        return (0 <= x < frame_width and 0 <= y < frame_height and 
                x + w <= frame_width and y + h <= frame_height and 
                w > min_size and h > min_size)
    
    def process_face_recognition_optimized(self, frame, x, y, w, h):
        """Optimized face recognition processing - returns (name, confidence)"""
        try:
            face_roi = frame[y:y+h, x:x+w]
            if face_roi.size == 0:
                return "Unknown", 0.0
            
            # Generate cache key
            cache_key = hash(face_roi.tobytes())
            
            # Check embedding cache
            if cache_key in self.embedding_cache:
                face_embedding = self.embedding_cache[cache_key]
            else:
                face_embedding = self.get_face_embedding_optimized(face_roi)
                if face_embedding is not None:
                    self.embedding_cache[cache_key] = face_embedding
                    # Limit cache size
                    max_cache_size = camera_config.get("embedding_cache_size", 100)
                    if len(self.embedding_cache) > max_cache_size:
                        self.embedding_cache.pop(next(iter(self.embedding_cache)))
            
            if face_embedding is not None:
                name, similarity = self.recognize_face_embedding_optimized(face_embedding)
                return name, similarity
            else:
                return "Unknown", 0.0
                    
        except Exception as e:
            print(f"Recognition error: {e}")
            return "Unknown", 0.0
    
    def get_face_embedding_optimized(self, face_image):
        """Optimized face embedding extraction"""
        try:
            if not self.facenet_model:
                return None
            
            # Resize and preprocess
            face_resized = cv2.resize(face_image, (160, 160))
            face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            face_pil = Image.fromarray(face_rgb)
            
            # Get aligned face
            face_tensor = None
            if self.mtcnn is not None:
                face_tensor = self.mtcnn(face_pil)
            
            if face_tensor is not None:
                if face_tensor.dim() == 3:
                    face_tensor = face_tensor.unsqueeze(0)
                
                with torch.no_grad():
                    embedding = self.facenet_model(face_tensor).cpu().numpy()
                return embedding.flatten()
            
            return None
            
        except Exception as e:
            print(f"Embedding error: {e}")
            return None
    
    def recognize_face_embedding_optimized(self, face_embedding, threshold=None):
        """Optimized face recognition with vectorized operations"""
        try:
            if face_embedding is None or not self.face_embeddings:
                return "Unknown", 0
            
            # Use dynamic recognition threshold if not provided
            if threshold is None:
                threshold = camera_config.get("recognition_threshold", 0.7)
            
            best_match = "Unknown"
            best_similarity = 0
            
            face_embedding_normalized = face_embedding / np.linalg.norm(face_embedding)
            
            for name, stored_embeddings in self.face_embeddings.items():
                if stored_embeddings:
                    # Vectorized similarity calculation
                    embeddings_array = np.array(stored_embeddings)
                    embeddings_normalized = embeddings_array / np.linalg.norm(embeddings_array, axis=1, keepdims=True)
                    
                    similarities = np.dot(embeddings_normalized, face_embedding_normalized)
                    max_similarity = np.max(similarities)
                    
                    if max_similarity > best_similarity:
                        best_similarity = max_similarity
                        best_match = name
            
            return (best_match, best_similarity) if best_similarity > threshold else ("Unknown", best_similarity)
            
        except Exception as e:
            print(f"Recognition error: {e}")
            return "Unknown", 0
    
    def load_face_embeddings(self):
        """Load face embeddings efficiently"""
        try:
            embeddings_file = 'trainer/face_embeddings.pkl'
            if os.path.exists(embeddings_file):
                with open(embeddings_file, 'rb') as f:
                    self.face_embeddings = pickle.load(f)
                print(f"Loaded {len(self.face_embeddings)} face embeddings")
            else:
                self.face_embeddings = {}
                print("No face embeddings found")
        except Exception as e:
            print(f"Error loading face embeddings: {e}")
            self.face_embeddings = {}
    
    def save_face_embeddings(self):
        """Save face embeddings efficiently"""
        try:
            os.makedirs('trainer', exist_ok=True)
            with open('trainer/face_embeddings.pkl', 'wb') as f:
                pickle.dump(self.face_embeddings, f)
            print(f"Saved {len(self.face_embeddings)} face embeddings")
        except Exception as e:
            print(f"Error saving face embeddings: {e}")
    
    def clear_embedding_cache(self):
        """Clear embedding cache to force fresh calculations"""
        self.embedding_cache.clear()
    
    def process_training_image(self, image_path):
        """Process a single training image"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Get user info from path structure
            # Path format: dataset/clean_name/clean_name_number.jpg
            path_parts = image_path.split(os.sep)
            if len(path_parts) >= 3:
                user_dir = path_parts[-2]  # Get the user directory name
                
                # Try to find the corresponding .txt file with the actual name
                txt_file = os.path.join(os.path.dirname(image_path), f"{user_dir}.txt")
                if os.path.exists(txt_file):
                    with open(txt_file, 'r') as f:
                        user_name = f.read().strip()
                else:
                    # Fallback to directory name if no txt file found
                    user_name = user_dir.replace('_', ' ')
            else:
                # Fallback for unexpected path format
                filename = os.path.basename(image_path)
                user_name = filename[:-4].replace('_', ' ')
            
            # Extract embedding
            embedding = self.get_face_embedding_optimized(img)
            
            return (user_name, embedding) if embedding is not None else None
            
        except Exception as e:
            print(f"Error processing training image {image_path}: {e}")
            return None 

    def apply_config_changes(self):
        """Apply configuration changes to face processing"""
        try:
            print("🔄 Applying face processing configuration changes...")
            
            # Check if MTCNN reinitialize is needed
            if self.mtcnn is not None:
                # Get current and new MTCNN config
                new_mtcnn_config = camera_config.get_mtcnn_config()
                
                # Reinitialize MTCNN with new settings
                use_gpu = camera_config.get("enable_gpu", True)
                device = self.mtcnn.device if hasattr(self.mtcnn, 'device') else None
                
                if device is None:
                    device = torch.device('cuda' if (torch.cuda.is_available() and use_gpu) else 'cpu')
                
                try:
                    self.mtcnn = MTCNN(
                        image_size=160,
                        margin=0,
                        min_face_size=new_mtcnn_config["min_face_size"],
                        thresholds=new_mtcnn_config["thresholds"],
                        factor=new_mtcnn_config["factor"],
                        post_process=True,
                        device=device,
                        keep_all=False
                    )
                    print(f"✅ MTCNN updated with new settings: Min Face Size={new_mtcnn_config['min_face_size']}")
                except Exception as e:
                    print(f"❌ Failed to update MTCNN: {e}")
                    return False
            
            # Clear embedding cache to apply new cache size
            max_cache_size = camera_config.get("embedding_cache_size", 100)
            if len(self.embedding_cache) > max_cache_size:
                # Keep only the most recent entries
                items = list(self.embedding_cache.items())
                self.embedding_cache = dict(items[-max_cache_size:])
                print(f"🗑️  Trimmed embedding cache to {max_cache_size} entries")
            
            print("✅ Face processing configuration updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error applying face processing configuration: {e}")
            return False 