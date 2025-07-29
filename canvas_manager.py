import cv2
import numpy as np
from datetime import datetime
import os
from PIL import Image

class CanvasManager:
    
    def __init__(self):
        self.canvas = None
        self.prev_pos = None
        self.brush_color = (255, 0, 255)
        self.brush_thickness = 10
        self.canvas_alpha = 0.3
        self.frame_alpha = 0.7
        self.total_points = 0
        self.drawing_history = []
        self.undo_stack = []
        self.max_undo_steps = 10
        
        self.drawings_dir = "saved_drawings"
        os.makedirs(self.drawings_dir, exist_ok=True)
    
    def initialize_canvas(self, shape):
        self.canvas = np.zeros(shape, dtype=np.uint8)
        self.canvas_shape = shape
    
    def update_settings(self, brush_color="#FF00FF", brush_thickness=10, canvas_alpha=0.3):
        brush_color = brush_color.lstrip('#')
        rgb = tuple(int(brush_color[i:i+2], 16) for i in (0, 2, 4))
        self.brush_color = (rgb[2], rgb[1], rgb[0])
        self.brush_thickness = brush_thickness
        self.canvas_alpha = canvas_alpha
        self.frame_alpha = 1.0 - canvas_alpha
    
    def draw_point(self, current_pos, force_draw=False):
        if self.canvas is None:
            return
        
        try:
            current_pos = tuple(map(int, current_pos))
            
            if self.prev_pos is not None or force_draw:
                if self.prev_pos is not None:
                    cv2.line(self.canvas, self.prev_pos, current_pos, 
                            self.brush_color, self.brush_thickness)
                else:
                    cv2.circle(self.canvas, current_pos, 
                              self.brush_thickness // 2, self.brush_color, -1)
                
                self.total_points += 1
                self.drawing_history.append({
                    'action': 'draw',
                    'from': self.prev_pos,
                    'to': current_pos,
                    'color': self.brush_color,
                    'thickness': self.brush_thickness
                })
            
            self.prev_pos = current_pos
            
        except Exception as e:
            print(f"Drawing error: {e}")
    
    def stop_drawing(self):
        self.prev_pos = None
    
    def clear_canvas(self):
        if self.canvas is not None:
            self._save_undo_state()
            
            self.canvas = np.zeros_like(self.canvas)
            self.prev_pos = None
            self.total_points = 0
            self.drawing_history.append({'action': 'clear'})
    
    def _save_undo_state(self):
        if self.canvas is not None:
            self.undo_stack.append(self.canvas.copy())
            if len(self.undo_stack) > self.max_undo_steps:
                self.undo_stack.pop(0)
    
    def undo_last_action(self):
        if self.undo_stack:
            self.canvas = self.undo_stack.pop()
            return True
        return False
    
    def get_canvas(self):
        if self.canvas is None:
            return None
        
        try:
            canvas_rgb = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2RGB)
            return Image.fromarray(canvas_rgb)
        except Exception as e:
            print(f"Canvas conversion error: {e}")
            return None
    
    def combine_with_frame(self, frame):
        if self.canvas is None:
            return frame
        
        try:
            if self.canvas.shape != frame.shape:
                self.canvas = cv2.resize(self.canvas, (frame.shape[1], frame.shape[0]))
            
            combined = cv2.addWeighted(frame, self.frame_alpha, 
                                     self.canvas, self.canvas_alpha, 0)
            
            self._add_info_overlay(combined)
            
            return combined
            
        except Exception as e:
            print(f"Frame combination error: {e}")
            return frame
    
    def _add_info_overlay(self, img):
        info_text = f"Points: {self.total_points} | Brush: {self.brush_thickness}px"
        cv2.putText(img, info_text, (10, img.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.circle(img, (img.shape[1] - 50, 30), 20, self.brush_color, -1)
        cv2.circle(img, (img.shape[1] - 50, 30), 20, (255, 255, 255), 2)
    
    def save_drawing(self, filename=None):
        if self.canvas is None or self.total_points == 0:
            return False, "Nothing to save"
        
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"drawing_{timestamp}.png"
            
            filepath = os.path.join(self.drawings_dir, filename)
            
            canvas_rgb = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(canvas_rgb)
            pil_image.save(filepath)
            
            return True, filepath
            
        except Exception as e:
            return False, f"Save error: {str(e)}"
    
    def load_drawing(self, filepath):
        try:
            if os.path.exists(filepath):
                pil_image = Image.open(filepath)
                canvas_rgb = np.array(pil_image)
                self.canvas = cv2.cvtColor(canvas_rgb, cv2.COLOR_RGB2BGR)
                
                self.total_points = np.count_nonzero(cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY))
                
                return True, "Drawing loaded successfully"
            else:
                return False, "File not found"
                
        except Exception as e:
            return False, f"Load error: {str(e)}"
    
    def get_drawing_statistics(self):
        if self.canvas is None:
            return {}
        
        gray_canvas = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        total_pixels = gray_canvas.shape[0] * gray_canvas.shape[1]
        drawn_pixels = np.count_nonzero(gray_canvas)
        coverage = (drawn_pixels / total_pixels) * 100
        
        return {
            'total_points': self.total_points,
            'drawn_pixels': drawn_pixels,
            'canvas_coverage': round(coverage, 2),
            'drawing_actions': len(self.drawing_history),
            'canvas_size': f"{self.canvas.shape[1]}x{self.canvas.shape[0]}"
        }
    
    def export_canvas_data(self):
        if self.canvas is None:
            return None
        
        try:
            canvas_rgb = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(canvas_rgb)
            
            from io import BytesIO
            import base64
            
            buffer = BytesIO()
            pil_image.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            return img_data
            
        except Exception as e:
            print(f"Export error: {e}")
            return None
