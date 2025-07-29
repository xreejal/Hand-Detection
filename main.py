import cv2
import cvzone
import numpy as np
import google.generativeai as genai
from cvzone.HandTrackingModule import HandDetector
from PIL import Image
import streamlit as st
import os
import time
from datetime import datetime
import json
import base64
from io import BytesIO

from hand_gesture_manager import HandGestureManager
from canvas_manager import CanvasManager
from ai_manager import AIManager
from utils import create_banner, load_config, save_config

st.set_page_config(
    page_title="AI Hand Drawing Recognition",
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5em;
        margin-bottom: 20px;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .status-connected {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .status-disconnected {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .gesture-info {
        background-color: #e2e3f3;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if 'canvas_manager' not in st.session_state:
        st.session_state.canvas_manager = CanvasManager()
    if 'hand_manager' not in st.session_state:
        st.session_state.hand_manager = HandGestureManager()
    if 'ai_manager' not in st.session_state:
        st.session_state.ai_manager = AIManager()
    if 'camera_initialized' not in st.session_state:
        st.session_state.camera_initialized = False
    if 'recognition_history' not in st.session_state:
        st.session_state.recognition_history = []
    if 'drawing_mode' not in st.session_state:
        st.session_state.drawing_mode = True

def sidebar_controls():
    st.sidebar.title("Controls")
    
    st.sidebar.subheader("Camera Settings")
    camera_index = st.sidebar.selectbox("Camera Index", [0, 1, 2], index=0)
    
    st.sidebar.subheader("Drawing Settings")
    brush_color = st.sidebar.color_picker("Brush Color", "#FF00FF")
    brush_thickness = st.sidebar.slider("Brush Thickness", 1, 20, 10)
    
    st.sidebar.subheader("Hand Detection")
    detection_confidence = st.sidebar.slider("Detection Confidence", 0.1, 1.0, 0.7, 0.1)
    tracking_confidence = st.sidebar.slider("Tracking Confidence", 0.1, 1.0, 0.5, 0.1)
    
    st.sidebar.subheader("AI Settings")
    api_key = st.sidebar.text_input("Gemini API Key", type="password", 
                                   help="Enter your Google Gemini API key")
    
    st.sidebar.subheader("Gesture Instructions")
    st.sidebar.markdown("""
    <div class="gesture-info">
    <b>Gestures:</b><br>
    • <b>Index finger up:</b> Draw<br>
    • <b>Thumb up:</b> Clear canvas<br>
    • <b>Four fingers up:</b> AI recognize<br>
    • <b>Peace sign:</b> Save drawing<br>
    • <b>Fist:</b> Stop drawing
    </div>
    """, unsafe_allow_html=True)
    
    return {
        'camera_index': camera_index,
        'brush_color': brush_color,
        'brush_thickness': brush_thickness,
        'detection_confidence': detection_confidence,
        'tracking_confidence': tracking_confidence,
        'api_key': api_key
    }

def main():
    initialize_session_state()
    
    st.markdown('<h1 class="main-header">AI Hand Drawing Recognition</h1>', 
                unsafe_allow_html=True)
    
    settings = sidebar_controls()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Live Feed")
        
        button_col1, button_col2, button_col3 = st.columns(3)
        with button_col1:
            run = st.checkbox('Run Camera', value=False)
        with button_col2:
            save_drawing = st.button('Save Drawing')
        with button_col3:
            clear_history = st.button('Clear History')
        
        FRAME_WINDOW = st.empty()
        
        status_placeholder = st.empty()
    
    with col2:
        st.subheader("AI Recognition")
        output_text_area = st.empty()
        
        st.subheader("Recognition History")
        history_container = st.container()
        
        st.subheader("Statistics")
        stats_container = st.empty()
    
    if settings['api_key']:
        st.session_state.ai_manager.configure_api(settings['api_key'])
    
    st.session_state.hand_manager.update_settings(
        detection_confidence=settings['detection_confidence'],
        tracking_confidence=settings['tracking_confidence']
    )
    
    st.session_state.canvas_manager.update_settings(
        brush_color=settings['brush_color'],
        brush_thickness=settings['brush_thickness']
    )
    
    if run:
        if not st.session_state.camera_initialized:
            try:
                cap = cv2.VideoCapture(settings['camera_index'])
                if not cap.isOpened():
                    st.error("Cannot access camera. Please check camera index.")
                    return
                st.session_state.cap = cap
                st.session_state.camera_initialized = True
                
                ret, frame = cap.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    st.session_state.canvas_manager.initialize_canvas(frame.shape)
                    
            except Exception as e:
                st.error(f"Camera initialization failed: {str(e)}")
                return
        
        if st.session_state.camera_initialized:
            cap = st.session_state.cap
            ret, frame = cap.read()
            
            if ret:
                frame = cv2.flip(frame, 1)
                
                hand_info = st.session_state.hand_manager.detect_hands(frame)
                
                if hand_info:
                    fingers, landmarks, gesture_name = hand_info
                    
                    if gesture_name == "DRAW":
                        st.session_state.canvas_manager.draw_point(landmarks[8][:2])
                    elif gesture_name == "CLEAR":
                        st.session_state.canvas_manager.clear_canvas()
                    elif gesture_name == "RECOGNIZE":
                        if settings['api_key']:
                            canvas_image = st.session_state.canvas_manager.get_canvas()
                            result = st.session_state.ai_manager.recognize_drawing(canvas_image)
                            if result:
                                timestamp = datetime.now().strftime("%H:%M:%S")
                                st.session_state.recognition_history.append({
                                    'timestamp': timestamp,
                                    'result': result
                                })
                    elif gesture_name == "SAVE":
                        if save_drawing:
                            st.session_state.canvas_manager.save_drawing()
                
                combined_frame = st.session_state.canvas_manager.combine_with_frame(frame)
                
                FRAME_WINDOW.image(combined_frame, channels="BGR", use_column_width=True)
                
                if hand_info:
                    status_html = f'<div class="status-box status-connected">Hand detected - Gesture: {gesture_name}</div>'
                else:
                    status_html = '<div class="status-box status-disconnected">No hand detected</div>'
                status_placeholder.markdown(status_html, unsafe_allow_html=True)
                
                if st.session_state.recognition_history:
                    latest_result = st.session_state.recognition_history[-1]['result']
                    output_text_area.markdown(f"### {latest_result}")
                
                with history_container:
                    if st.session_state.recognition_history:
                        for i, item in enumerate(reversed(st.session_state.recognition_history[-5:])):
                            st.text(f"[{item['timestamp']}] {item['result']}")
                
                with stats_container:
                    total_recognitions = len(st.session_state.recognition_history)
                    st.metric("Total Recognitions", total_recognitions)
                    if st.session_state.canvas_manager.total_points > 0:
                        st.metric("Drawing Points", st.session_state.canvas_manager.total_points)
            
            else:
                st.error("Failed to read from camera")
    
    else:
        if st.session_state.camera_initialized:
            st.session_state.cap.release()
            st.session_state.camera_initialized = False
    
    if clear_history:
        st.session_state.recognition_history.clear()
        st.rerun()

if __name__ == "__main__":
    main()
