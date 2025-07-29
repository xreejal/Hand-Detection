import cv2
import numpy as np
import json
import os
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

def create_banner():
    try:
        width, height = 800, 150
        banner = Image.new('RGB', (width, height), color='#1f77b4')
        draw = ImageDraw.Draw(banner)
        
        try:
            font = ImageFont.truetype("arial.ttf", 48)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        title = "AI Hand Drawing Recognition"
        subtitle = "Draw with gestures, recognize with AI"
        
        title_bbox = draw.textbbox((0, 0), title, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=small_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        
        draw.text((title_x, 30), title, fill='white', font=font)
        draw.text((subtitle_x, 90), subtitle, fill='lightblue', font=small_font)
        
        draw.ellipse([50, 50, 100, 100], fill='orange')
        draw.ellipse([700, 50, 750, 100], fill='orange')
        
        banner.save('banner.png')
        return True
        
    except Exception as e:
        print(f"Banner creation error: {e}")
        return False

def load_config(config_file='config.json'):
    default_config = {
        'camera_index': 0,
        'brush_color': '#FF00FF',
        'brush_thickness': 10,
        'detection_confidence': 0.7,
        'tracking_confidence': 0.5,
        'canvas_alpha': 0.3,
        'gesture_threshold': 0.5,
        'auto_save': False,
        'save_interval': 30
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
    except Exception as e:
        print(f"Config load error: {e}")
    
    return default_config

def save_config(config, config_file='config.json'):
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Config save error: {e}")
        return False

def validate_camera_access(camera_index=0):
    try:
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            return ret and frame is not None
        return False
    except:
        return False

def get_available_cameras():
    available_cameras = []
    for i in range(5):
        if validate_camera_access(i):
            available_cameras.append(i)
    return available_cameras

def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])

def bgr_to_hex(bgr_color):
    return f"#{bgr_color[2]:02x}{bgr_color[1]:02x}{bgr_color[0]:02x}"

def resize_image_to_fit(image, max_width=800, max_height=600):
    height, width = image.shape[:2]
    
    scale_w = max_width / width
    scale_h = max_height / height
    scale = min(scale_w, scale_h, 1.0)
    
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return image

def add_watermark(image, text="AI Hand Drawing", position='bottom-right'):
    try:
        h, w = image.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 255, 255)
        thickness = 1
        
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        
        if position == 'bottom-right':
            x = w - text_width - 10
            y = h - 10
        elif position == 'bottom-left':
            x = 10
            y = h - 10
        elif position == 'top-right':
            x = w - text_width - 10
            y = text_height + 10
        else:
            x = 10
            y = text_height + 10
        
        overlay = image.copy()
        cv2.rectangle(overlay, (x-5, y-text_height-5), (x+text_width+5, y+5), (0, 0, 0), -1)
        image = cv2.addWeighted(image, 0.8, overlay, 0.2, 0)
        
        cv2.putText(image, text, (x, y), font, font_scale, color, thickness)
        
        return image
        
    except Exception as e:
        print(f"Watermark error: {e}")
        return image

def create_gesture_guide():
    guide_data = {
        "gestures": [
            {
                "name": "Draw",
                "fingers": [0, 1, 0, 0, 0],
                "description": "Point with index finger to draw"
            },
            {
                "name": "Clear",
                "fingers": [1, 0, 0, 0, 0],
                "description": "Thumbs up to clear canvas"
            },
            {
                "name": "Recognize",
                "fingers": [1, 1, 1, 1, 0],
                "description": "Four fingers up for AI recognition"
            },
            {
                "name": "Save",
                "fingers": [0, 1, 1, 0, 0],
                "description": "Peace sign to save drawing"
            },
            {
                "name": "Stop",
                "fingers": [0, 0, 0, 0, 0],
                "description": "Closed fist to stop drawing"
            }
        ]
    }
    
    return guide_data

def log_performance_metrics(func_name, execution_time, additional_data=None):
    try:
        log_entry = {
            'timestamp': str(pd.Timestamp.now()),
            'function': func_name,
            'execution_time': execution_time,
            'additional_data': additional_data or {}
        }
        
        log_file = 'performance_log.json'
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
    except Exception as e:
        print(f"Logging error: {e}")

def create_tutorial_overlay():
    tutorial_steps = [
        {
            "title": "Welcome to AI Hand Drawing!",
            "content": "This app recognizes your hand gestures to draw and interact with AI.",
            "image": None
        },
        {
            "title": "Camera Setup",
            "content": "Make sure your camera is working and you have good lighting.",
            "image": None
        },
        {
            "title": "Hand Gestures",
            "content": "Use different finger positions to control the app. Check the sidebar for details.",
            "image": None
        },
        {
            "title": "Drawing",
            "content": "Point with your index finger to draw on the canvas.",
            "image": None
        },
        {
            "title": "AI Recognition",
            "content": "Hold up four fingers to let AI recognize your drawing.",
            "image": None
        }
    ]
    
    return tutorial_steps

def calculate_drawing_metrics(canvas):
    if canvas is None:
        return {}
    
    try:
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        
        total_pixels = gray.shape[0] * gray.shape[1]
        drawn_pixels = np.count_nonzero(gray)
        coverage_percentage = (drawn_pixels / total_pixels) * 100
        
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        num_objects = len(contours)
        
        if contours:
            all_points = np.vstack(contours)
            x, y, w, h = cv2.boundingRect(all_points)
            drawing_area = w * h
            drawing_density = drawn_pixels / drawing_area if drawing_area > 0 else 0
        else:
            drawing_area = 0
            drawing_density = 0
        
        return {
            'coverage_percentage': round(coverage_percentage, 2),
            'drawn_pixels': drawn_pixels,
            'num_objects': num_objects,
            'drawing_area': drawing_area,
            'drawing_density': round(drawing_density, 4),
            'canvas_utilization': 'High' if coverage_percentage > 25 else 'Medium' if coverage_percentage > 10 else 'Low'
        }
        
    except Exception as e:
        print(f"Metrics calculation error: {e}")
        return {}
