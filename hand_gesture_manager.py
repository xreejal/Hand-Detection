import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time

class HandGestureManager:
    
    def __init__(self):
        self.detector = HandDetector(
            staticMode=False,
            maxHands=1,
            modelComplexity=1,
            detectionCon=0.7,
            minTrackCon=0.5
        )
        self.prev_gesture = None
        self.gesture_start_time = None
        self.gesture_threshold = 0.5
        self.smoothing_buffer = []
        self.buffer_size = 5
        
        self.gesture_patterns = {
            'DRAW': [0, 1, 0, 0, 0],
            'CLEAR': [1, 0, 0, 0, 0],
            'RECOGNIZE': [1, 1, 1, 1, 0],
            'SAVE': [0, 1, 1, 0, 0],
            'STOP': [0, 0, 0, 0, 0],
            'IDLE': None
        }
    
    def update_settings(self, detection_confidence=0.7, tracking_confidence=0.5):
        self.detector = HandDetector(
            staticMode=False,
            maxHands=1,
            modelComplexity=1,
            detectionCon=detection_confidence,
            minTrackCon=tracking_confidence
        )
    
    def detect_hands(self, img):
        try:
            hands, img_annotated = self.detector.findHands(img, draw=True, flipType=True)
            
            if hands:
                hand = hands[0]
                landmarks = hand["lmList"]
                fingers = self.detector.fingersUp(hand)
                
                self.smoothing_buffer.append(fingers)
                if len(self.smoothing_buffer) > self.buffer_size:
                    self.smoothing_buffer.pop(0)
                
                smoothed_fingers = self._get_smoothed_fingers()
                gesture_name = self._classify_gesture(smoothed_fingers)
                
                stable_gesture = self._check_gesture_stability(gesture_name)
                
                return smoothed_fingers, landmarks, stable_gesture
            
            else:
                self.smoothing_buffer.clear()
                return None
                
        except Exception as e:
            print(f"Hand detection error: {e}")
            return None
    
    def _get_smoothed_fingers(self):
        if not self.smoothing_buffer:
            return [0, 0, 0, 0, 0]
        
        smoothed = []
        for i in range(5):
            finger_values = [fingers[i] for fingers in self.smoothing_buffer]
            smoothed.append(1 if sum(finger_values) > len(finger_values) // 2 else 0)
        
        return smoothed
    
    def _classify_gesture(self, fingers):
        for gesture_name, pattern in self.gesture_patterns.items():
            if pattern is not None and fingers == pattern:
                return gesture_name
        return 'UNKNOWN'
    
    def _check_gesture_stability(self, current_gesture):
        current_time = time.time()
        
        if current_gesture != self.prev_gesture:
            self.gesture_start_time = current_time
            self.prev_gesture = current_gesture
            return 'IDLE'
        
        if current_time - self.gesture_start_time >= self.gesture_threshold:
            return current_gesture
        
        return 'IDLE'
    
    def draw_gesture_info(self, img, gesture_name, fingers):
        cv2.putText(img, f"Gesture: {gesture_name}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        for i, (name, status) in enumerate(zip(finger_names, fingers)):
            color = (0, 255, 0) if status else (0, 0, 255)
            cv2.putText(img, f"{name}: {'Up' if status else 'Down'}", 
                       (10, 70 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return img
    
    def get_gesture_confidence(self):
        if len(self.smoothing_buffer) < self.buffer_size:
            return 0.0
        
        total_matches = 0
        reference = self.smoothing_buffer[-1]
        
        for fingers in self.smoothing_buffer:
            if fingers == reference:
                total_matches += 1
        
        return total_matches / len(self.smoothing_buffer)
    
    def reset(self):
        self.prev_gesture = None
        self.gesture_start_time = None
        self.smoothing_buffer.clear()
