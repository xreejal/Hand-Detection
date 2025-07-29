import google.generativeai as genai
from PIL import Image
import time
import json
import os
from datetime import datetime

class AIManager:
    
    def __init__(self):
        self.model = None
        self.api_configured = False
        self.recognition_cache = {}
        self.recognition_history = []
        self.custom_prompts = {
            'simple': "What is this drawing? Respond with just the name of the object.",
            'detailed': "Analyze this drawing and provide a detailed description including what it might be, artistic style, and confidence level.",
            'creative': "Look at this drawing and tell me what creative story or idea it represents.",
            'educational': "Identify this drawing and provide educational information about the subject."
        }
        self.current_prompt_type = 'simple'
        self.confidence_threshold = 0.7
        
        self.history_file = "recognition_history.json"
        self._load_history()
    
    def configure_api(self, api_key):
        try:
            if api_key and api_key.strip():
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.api_configured = True
                return True, "API configured successfully"
            else:
                return False, "Invalid API key"
        except Exception as e:
            self.api_configured = False
            return False, f"API configuration error: {str(e)}"
    
    def set_prompt_type(self, prompt_type):
        if prompt_type in self.custom_prompts:
            self.current_prompt_type = prompt_type
            return True
        return False
    
    def recognize_drawing(self, pil_image, custom_prompt=None):
        if not self.api_configured or not self.model:
            return "AI not configured. Please provide API key."
        
        if pil_image is None:
            return "No image to analyze"
        
        try:
            cache_key = self._generate_cache_key(pil_image)
            if cache_key in self.recognition_cache:
                cached_result = self.recognition_cache[cache_key]
                return f"{cached_result['result']} (cached)"
            
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = self.custom_prompts[self.current_prompt_type]
            
            enhanced_prompt = f"""
            {prompt}
            
            Additional context:
            - This is a hand-drawn sketch
            - It may be simple or rough
            - Focus on the main recognizable elements
            - If uncertain, provide your best guess with confidence level
            """
            
            start_time = time.time()
            response = self.model.generate_content([enhanced_prompt, pil_image])
            processing_time = time.time() - start_time
            
            if response and response.text:
                result = response.text.strip()
                
                self.recognition_cache[cache_key] = {
                    'result': result,
                    'timestamp': datetime.now().isoformat(),
                    'processing_time': processing_time
                }
                
                self._add_to_history(result, processing_time)
                
                return f"{result}"
            else:
                return "No response from AI"
                
        except Exception as e:
            error_msg = f"AI recognition error: {str(e)}"
            print(error_msg)
            return f"{error_msg}"
    
    def _generate_cache_key(self, pil_image):
        try:
            import hashlib
            img_bytes = pil_image.tobytes()
            return hashlib.md5(img_bytes).hexdigest()
        except:
            return str(time.time())
    
    def _add_to_history(self, result, processing_time):
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'result': result,
            'processing_time': round(processing_time, 2),
            'prompt_type': self.current_prompt_type
        }
        
        self.recognition_history.append(history_entry)
        
        if len(self.recognition_history) > 100:
            self.recognition_history = self.recognition_history[-100:]
        
        self._save_history()
    
    def _load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.recognition_history = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            self.recognition_history = []
    
    def _save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.recognition_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def get_recognition_stats(self):
        if not self.recognition_history:
            return {}
        
        total_recognitions = len(self.recognition_history)
        avg_processing_time = sum(entry['processing_time'] for entry in self.recognition_history) / total_recognitions
        
        prompt_counts = {}
        for entry in self.recognition_history:
            prompt_type = entry.get('prompt_type', 'unknown')
            prompt_counts[prompt_type] = prompt_counts.get(prompt_type, 0) + 1
        
        return {
            'total_recognitions': total_recognitions,
            'average_processing_time': round(avg_processing_time, 2),
            'cache_size': len(self.recognition_cache),
            'prompt_type_usage': prompt_counts,
            'api_configured': self.api_configured
        }
    
    def clear_cache(self):
        self.recognition_cache.clear()
        return "Cache cleared successfully"
    
    def clear_history(self):
        self.recognition_history.clear()
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
        except:
            pass
        return "History cleared successfully"
    
    def export_results(self, format='json'):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format == 'json':
                filename = f"recognition_export_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump({
                        'export_timestamp': datetime.now().isoformat(),
                        'total_entries': len(self.recognition_history),
                        'history': self.recognition_history,
                        'stats': self.get_recognition_stats()
                    }, f, indent=2)
                return True, filename
            
            elif format == 'csv':
                import csv
                filename = f"recognition_export_{timestamp}.csv"
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Result', 'Processing Time', 'Prompt Type'])
                    for entry in self.recognition_history:
                        writer.writerow([
                            entry['timestamp'],
                            entry['result'],
                            entry['processing_time'],
                            entry.get('prompt_type', 'unknown')
                        ])
                return True, filename
            
            else:
                return False, "Unsupported format"
                
        except Exception as e:
            return False, f"Export error: {str(e)}"
    
    def analyze_drawing_complexity(self, pil_image):
        if not self.api_configured or not self.model:
            return "AI not configured"
        
        try:
            complexity_prompt = """
            Analyze this drawing and rate its complexity on a scale of 1-10 where:
            1-3: Very simple (basic shapes, stick figures)
            4-6: Moderate (recognizable objects with some detail)
            7-10: Complex (detailed, artistic, multiple elements)
            
            Provide the rating and a brief explanation.
            """
            
            response = self.model.generate_content([complexity_prompt, pil_image])
            if response and response.text:
                return response.text.strip()
            else:
                return "Unable to analyze complexity"
                
        except Exception as e:
            return f"Complexity analysis error: {str(e)}"
    
    def get_drawing_suggestions(self, pil_image):
        if not self.api_configured or not self.model:
            return "AI not configured"
        
        try:
            suggestion_prompt = """
            Look at this drawing and provide 3 constructive suggestions for improvement.
            Focus on:
            1. Adding details that would make it more recognizable
            2. Improving proportions or structure
            3. Enhancing artistic elements
            
            Keep suggestions encouraging and specific.
            """
            
            response = self.model.generate_content([suggestion_prompt, pil_image])
            if response and response.text:
                return response.text.strip()
            else:
                return "Unable to generate suggestions"
                
        except Exception as e:
            return f"Suggestion error: {str(e)}"
