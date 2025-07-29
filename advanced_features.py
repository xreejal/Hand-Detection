import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance
import time
import json
from datetime import datetime, timedelta

class AdvancedFeatures:
    
    def __init__(self):
        self.session_start_time = datetime.now()
        self.drawing_sessions = []
        self.gesture_analytics = {}
        self.performance_metrics = {}
        
    def create_advanced_sidebar(self):
        st.sidebar.markdown("---")
        st.sidebar.subheader("Advanced Features")
        
        drawing_mode = st.sidebar.selectbox(
            "Drawing Mode",
            ["Continuous", "Dots Only", "Lines Only", "Shapes"],
            help="Choose how drawing strokes are rendered"
        )
        
        st.sidebar.subheader("Canvas Effects")
        apply_blur = st.sidebar.checkbox("Blur Effect")
        apply_glow = st.sidebar.checkbox("Glow Effect")
        apply_shadow = st.sidebar.checkbox("Drop Shadow")
        
        st.sidebar.subheader("AI Analysis")
        analysis_depth = st.sidebar.select_slider(
            "Analysis Depth",
            options=["Basic", "Detailed", "Creative", "Educational"],
            value="Basic"
        )
        
        auto_recognize = st.sidebar.checkbox(
            "Auto Recognition",
            help="Automatically recognize drawings after 3 seconds of inactivity"
        )
        
        st.sidebar.subheader("Performance")
        show_fps = st.sidebar.checkbox("Show FPS")
        show_latency = st.sidebar.checkbox("Show Latency")
        
        return {
            'drawing_mode': drawing_mode,
            'apply_blur': apply_blur,
            'apply_glow': apply_glow,
            'apply_shadow': apply_shadow,
            'analysis_depth': analysis_depth.lower(),
            'auto_recognize': auto_recognize,
            'show_fps': show_fps,
            'show_latency': show_latency
        }
    
    def apply_canvas_effects(self, canvas, effects):
        if canvas is None:
            return canvas
        
        try:
            canvas_rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(canvas_rgb)
            
            if effects.get('apply_blur', False):
                pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=1))
            
            if effects.get('apply_glow', False):
                glow = pil_image.filter(ImageFilter.GaussianBlur(radius=3))
                enhancer = ImageEnhance.Brightness(glow)
                glow = enhancer.enhance(1.5)
                
                pil_image = Image.alpha_composite(
                    glow.convert('RGBA'),
                    pil_image.convert('RGBA')
                ).convert('RGB')
            
            if effects.get('apply_shadow', False):
                shadow = Image.new('RGB', pil_image.size, (0, 0, 0))
                shadow_mask = pil_image.convert('L')
                shadow.paste(pil_image, (3, 3), shadow_mask)
                
                pil_image = Image.blend(shadow, pil_image, 0.8)
            
            canvas_with_effects = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return canvas_with_effects
            
        except Exception as e:
            print(f"Effects application error: {e}")
            return canvas
    
    def create_gesture_analytics_dashboard(self):
        st.subheader("Gesture Analytics")
        
        if self.gesture_analytics:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_gestures = sum(self.gesture_analytics.values())
                st.metric("Total Gestures", total_gestures)
            
            with col2:
                most_used = max(self.gesture_analytics.items(), key=lambda x: x[1])
                st.metric("Most Used Gesture", f"{most_used[0]} ({most_used[1]})")
            
            with col3:
                session_duration = (datetime.now() - self.session_start_time).total_seconds()
                gestures_per_minute = (total_gestures / session_duration) * 60 if session_duration > 0 else 0
                st.metric("Gestures/Min", f"{gestures_per_minute:.1f}")
            
            if st.checkbox("Show Gesture Distribution"):
                import plotly.express as px
                
                df_gestures = pd.DataFrame(
                    list(self.gesture_analytics.items()),
                    columns=['Gesture', 'Count']
                )
                
                fig = px.pie(df_gestures, values='Count', names='Gesture',
                           title="Gesture Usage Distribution")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No gesture data available yet. Start using gestures to see analytics!")
    
    def track_gesture_usage(self, gesture_name):
        if gesture_name and gesture_name != 'IDLE' and gesture_name != 'UNKNOWN':
            self.gesture_analytics[gesture_name] = self.gesture_analytics.get(gesture_name, 0) + 1
    
    def calculate_fps(self, frame_times):
        if len(frame_times) < 2:
            return 0
        
        time_diffs = [frame_times[i] - frame_times[i-1] for i in range(1, len(frame_times))]
        avg_time_diff = sum(time_diffs) / len(time_diffs)
        
        return 1.0 / avg_time_diff if avg_time_diff > 0 else 0
    
    def create_performance_overlay(self, img, fps=0, latency=0):
        try:
            if fps > 0:
                fps_text = f"FPS: {fps:.1f}"
                cv2.putText(img, fps_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if latency > 0:
                latency_text = f"Latency: {latency:.0f}ms"
                cv2.putText(img, latency_text, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            return img
            
        except Exception as e:
            print(f"Performance overlay error: {e}")
            return img
    
    def auto_save_session(self, canvas_manager, ai_manager):
        try:
            session_data = {
                'timestamp': datetime.now().isoformat(),
                'session_duration': (datetime.now() - self.session_start_time).total_seconds(),
                'gesture_analytics': self.gesture_analytics,
                'drawing_stats': canvas_manager.get_drawing_statistics() if canvas_manager else {},
                'ai_stats': ai_manager.get_recognition_stats() if ai_manager else {}
            }
            
            session_file = f"session_{self.session_start_time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return True, session_file
            
        except Exception as e:
            return False, str(e)
    
    def create_drawing_templates(self):
        templates = {
            "Basic Shapes": {
                "circle": "Draw a perfect circle",
                "square": "Draw a square with equal sides",
                "triangle": "Draw a triangle with three points"
            },
            "Animals": {
                "cat": "Draw a cat with ears, whiskers, and tail",
                "dog": "Draw a dog with floppy ears",
                "bird": "Draw a bird with wings and beak"
            },
            "Objects": {
                "house": "Draw a house with roof, door, and windows",
                "car": "Draw a car with wheels and windows",
                "tree": "Draw a tree with trunk and leaves"
            }
        }
        
        return templates
    
    def create_challenge_mode(self):
        challenges = [
            {
                "name": "Speed Drawing",
                "description": "Draw the given object in under 30 seconds",
                "time_limit": 30,
                "objects": ["apple", "house", "car", "tree", "cat"]
            },
            {
                "name": "Blind Drawing",
                "description": "Draw without looking at the canvas",
                "time_limit": 60,
                "objects": ["face", "flower", "sun", "heart"]
            },
            {
                "name": "One Line Challenge",
                "description": "Draw without lifting your finger",
                "time_limit": 45,
                "objects": ["star", "envelope", "bicycle"]
            }
        ]
        
        return challenges
    
    def evaluate_drawing_challenge(self, challenge, canvas_image, ai_manager):
        if not ai_manager or not ai_manager.api_configured:
            return "Cannot evaluate - AI not configured"
        
        try:
            evaluation_prompt = f"""
            Evaluate this drawing for the challenge: {challenge['name']}
            Target object: {challenge.get('target_object', 'unknown')}
            Challenge description: {challenge['description']}
            
            Rate the drawing on:
            1. Accuracy (how well it represents the object)
            2. Creativity
            3. Challenge completion
            
            Provide a score out of 10 and brief feedback.
            """
            
            response = ai_manager.model.generate_content([evaluation_prompt, canvas_image])
            return response.text if response and response.text else "Evaluation failed"
            
        except Exception as e:
            return f"Evaluation error: {str(e)}"
    
    def create_collaborative_features(self):
        collab_features = {
            "session_sharing": {
                "description": "Share your drawing session with others",
                "implementation": "Generate shareable session codes"
            },
            "drawing_gallery": {
                "description": "Browse drawings from other users",
                "implementation": "Community gallery with rating system"
            },
            "real_time_collaboration": {
                "description": "Draw together in real-time",
                "implementation": "WebSocket-based collaborative canvas"
            }
        }
        
        return collab_features
    
    def export_session_report(self, canvas_manager, ai_manager):
        try:
            session_duration = (datetime.now() - self.session_start_time).total_seconds()
            
            report = {
                "session_info": {
                    "start_time": self.session_start_time.isoformat(),
                    "duration_minutes": round(session_duration / 60, 2),
                    "end_time": datetime.now().isoformat()
                },
                "drawing_statistics": canvas_manager.get_drawing_statistics() if canvas_manager else {},
                "gesture_analytics": {
                    "total_gestures": sum(self.gesture_analytics.values()),
                    "gesture_breakdown": self.gesture_analytics,
                    "most_used_gesture": max(self.gesture_analytics.items(), key=lambda x: x[1])[0] if self.gesture_analytics else "None"
                },
                "ai_performance": ai_manager.get_recognition_stats() if ai_manager else {},
                "productivity_metrics": {
                    "gestures_per_minute": (sum(self.gesture_analytics.values()) / session_duration) * 60 if session_duration > 0 else 0,
                    "drawing_efficiency": "High" if sum(self.gesture_analytics.values()) > 50 else "Medium" if sum(self.gesture_analytics.values()) > 20 else "Low"
                }
            }
            
            report_filename = f"session_report_{self.session_start_time.strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            return True, report_filename, report
            
        except Exception as e:
            return False, str(e), {}
    
    def create_accessibility_features(self):
        accessibility_options = {
            "high_contrast_mode": {
                "description": "High contrast colors for better visibility",
                "implementation": "Adjust color scheme for visual impairments"
            },
            "gesture_sensitivity": {
                "description": "Adjust gesture detection sensitivity",
                "implementation": "Customizable detection thresholds"
            },
            "voice_commands": {
                "description": "Control app with voice commands",
                "implementation": "Speech recognition for basic commands"
            },
            "large_ui_mode": {
                "description": "Larger UI elements for easier interaction",
                "implementation": "Scalable interface components"
            }
        }
        
        return accessibility_options
    
    def implement_gesture_customization(self):
        custom_gestures = {
            "gesture_recorder": {
                "description": "Record custom gesture patterns",
                "implementation": "Learn new finger combinations"
            },
            "gesture_sensitivity": {
                "description": "Adjust how sensitive gesture detection is",
                "implementation": "Configurable detection thresholds"
            },
            "left_handed_mode": {
                "description": "Optimize for left-handed users",
                "implementation": "Mirror gesture patterns"
            }
        }
        
        return custom_gestures
