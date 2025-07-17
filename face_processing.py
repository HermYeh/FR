import cv2
import numpy as np
import torch
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import time

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
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f"Using device: {device}")
            
            # Optimized MTCNN settings
            self.mtcnn = MTCNN(
                image_size=160,
                margin=0,
                min_face_size=30,  # Increased for better performance
                thresholds=[0.7, 0.8, 0.8],  # Higher thresholds for better accuracy
                factor=0.709,
                post_process=True,
                device=device,
                keep_all=False  # Keep only best face for better performance
            )
            
            # Initialize FaceNet model
            self.facenet_model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
            
            self.load_face_embeddings()
            print("Optimized FaceNet initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize FaceNet: {e}")
            return False
    
    def detect_faces_optimized(self, frame):
        """Optimized face detection with MTCNN"""
        try:
            if not self.mtcnn:
                return []
            
            # Resize frame for faster processing
            scale_factor = 0.5
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
                    for box, prob in zip(boxes, probs):
                        if prob > 0.8:  # Higher threshold for better accuracy
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
        return (0 <= x < frame_width and 0 <= y < frame_height and 
                x + w <= frame_width and y + h <= frame_height and 
                w > 20 and h > 20)
    
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
                    if len(self.embedding_cache) > 100:
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
    
    def recognize_face_embedding_optimized(self, face_embedding, threshold=0.7):
        """Optimized face recognition with vectorized operations"""
        try:
            if face_embedding is None or not self.face_embeddings:
                return "Unknown", 0
            
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