"""
Model Manager for Air Mouse Backend

Handles sequential loading and unloading of MediaPipe models (Face Mesh and Hands)
to ensure optimal performance and memory usage.
"""

import gc
import sys
from typing import Optional

# Robust import strategy for MediaPipe solutions
try:
    import mediapipe.python.solutions.face_mesh as mp_face_mesh
    import mediapipe.python.solutions.hands as mp_hands
    print("Imported mediapipe.python.solutions")
except ImportError:
    try:
        import mediapipe.solutions.face_mesh as mp_face_mesh
        import mediapipe.solutions.hands as mp_hands
        print("Imported mediapipe.solutions")
    except ImportError:
        # Fallback: import mediapipe and try to access attributes dynamically
        import mediapipe as mp
        try:
            mp_face_mesh = mp.solutions.face_mesh
            mp_hands = mp.solutions.hands
            print("Imported mediapipe.solutions via mp")
        except AttributeError:
            print("CRITICAL ERROR: Could not import mediapipe solutions.")
            print("Please ensure mediapipe is installed correctly.")
            # Mock objects to prevent crash, but functionality will fail
            class MockModel:
                def __init__(self, **kwargs): pass
                def process(self, img): return None
                def close(self): pass
            
            class MockModule:
                FaceMesh = MockModel
                Hands = MockModel
            
            mp_face_mesh = MockModule()
            mp_hands = MockModule()

class ModelManager:
    def __init__(self):
        self.face_mesh = None
        self.hands = None
        
        # Use imported modules
        self.mp_face_mesh = mp_face_mesh
        self.mp_hands = mp_hands

    def load_face_mesh(self) -> bool:
        """Load Face Mesh model and unload Hands model if active."""
        if self.hands:
            self.unload_hands()
            
        if not self.face_mesh:
            print("Loading Face Mesh model...")
            try:
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.6,
                    min_tracking_confidence=0.6
                )
                return True
            except Exception as e:
                print(f"Error loading Face Mesh: {e}")
                return False
        return True

    def unload_face_mesh(self) -> None:
        """Unload Face Mesh model and free memory."""
        if self.face_mesh:
            print("Unloading Face Mesh model...")
            self.face_mesh.close()
            self.face_mesh = None
            gc.collect()

    def load_hands(self) -> bool:
        """Load Hands model and unload Face Mesh model if active."""
        if self.face_mesh:
            self.unload_face_mesh()
            
        if not self.hands:
            print("Loading Hands model...")
            try:
                self.hands = self.mp_hands.Hands(
                    max_num_hands=1,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.7
                )
                return True
            except Exception as e:
                print(f"Error loading Hands: {e}")
                return False
        return True

    def unload_hands(self) -> None:
        """Unload Hands model and free memory."""
        if self.hands:
            print("Unloading Hands model...")
            self.hands.close()
            self.hands = None
            gc.collect()

    def get_face_mesh(self):
        """Get active Face Mesh instance."""
        return self.face_mesh

    def get_hands(self):
        """Get active Hands instance."""
        return self.hands
