#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import cv2
import yaml
from pathlib import Path


class SetupManager:
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.project_root = Path(__file__).parent
        
    def check_system_requirements(self):
        if self.python_version < (3, 8):
            print(f"Error: Python 3.8 or higher required. Current: {sys.version}")
            return False
        return True
    
    def install_dependencies(self):
        requirements = [
            "streamlit>=1.28.0",
            "opencv-python>=4.8.0", 
            "cvzone>=1.6.1",
            "google-generativeai>=0.3.0",
            "Pillow>=10.0.0",
            "numpy>=1.24.0",
            "mediapipe>=0.10.0",
            "protobuf>=3.20.0",
            "pyyaml>=6.0"
        ]
        
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            with open(req_file, 'w') as f:
                f.write('\n'.join(requirements))
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            return True
        except subprocess.CalledProcessError:
            return False
    
    def create_directories(self):
        directories = [
            "saved_drawings",
            "logs", 
            "cache",
            "sessions"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
        
        return True
    
    def setup_configuration(self):
        env_file = self.project_root / ".env"
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write("GEMINI_API_KEY=your_api_key_here\n")
                f.write("DEFAULT_CAMERA_INDEX=0\n")
        
        config_file = self.project_root / "config.yaml"
        if not config_file.exists():
            config = {
                'camera': {
                    'default_index': 0,
                    'resolution': {'width': 640, 'height': 480},
                    'fps': 30
                },
                'hand_detection': {
                    'detection_confidence': 0.7,
                    'tracking_confidence': 0.5,
                    'gesture_stability_time': 1.0
                },
                'drawing': {
                    'default_brush_thickness': 5,
                    'default_color': [0, 255, 0],
                    'canvas_size': {'width': 800, 'height': 600}
                },
                'ai': {
                    'default_analysis_mode': 'simple',
                    'enable_caching': True,
                    'cache_duration_hours': 24,
                    'auto_recognition_delay': 3.0
                },
                'gestures': {
                    'patterns': {
                        'draw': [0, 1, 0, 0, 0],
                        'clear': [1, 0, 0, 0, 0],
                        'ai_recognize': [1, 1, 1, 1, 0],
                        'save': [0, 1, 1, 0, 0],
                        'stop': [0, 0, 0, 0, 0]
                    }
                },
                'performance': {
                    'max_frame_rate': 30,
                    'processing_threads': 2,
                    'enable_gpu_acceleration': False
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        
        return True
    
    def test_camera_access(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False
            
            ret, frame = cap.read()
            cap.release()
            
            return ret and frame is not None
                
        except Exception:
            return False
    
    def create_launch_scripts(self):
        if self.system == "Windows":
            batch_file = self.project_root / "run_app.bat"
            with open(batch_file, 'w') as f:
                f.write("@echo off\n")
                f.write("streamlit run main.py\n")
                f.write("pause\n")
        else:
            shell_file = self.project_root / "run_app.sh"
            with open(shell_file, 'w') as f:
                f.write("#!/bin/bash\n")
                f.write("streamlit run main.py\n")
            
            os.chmod(shell_file, 0o755)
        
        return True
    
    def run_setup(self):
        steps = [
            ("System Requirements", self.check_system_requirements),
            ("Dependencies", self.install_dependencies),
            ("Directories", self.create_directories),
            ("Configuration", self.setup_configuration),
            ("Camera Test", self.test_camera_access),
            ("Launch Scripts", self.create_launch_scripts)
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"Setup failed at: {step_name}")
                    return False
            except Exception as e:
                print(f"Error in {step_name}: {e}")
                return False
        
        print("Setup completed. Add your API key to .env file and run: streamlit run main.py")
        return True


def main():
    try:
        setup_manager = SetupManager()
        success = setup_manager.run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"Setup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
