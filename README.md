# AI Hand Drawing Recognition

An advanced real-time hand gesture drawing application powered by AI recognition. Draw with your hands, get instant AI feedback! It is designed to track your fingerprints in real-time, while allowing for better preceision in drawing mid-air. We will most likely turn this into a tool for video calls, but open to contributions!

## Features

### Hand Gesture Control
- **Draw**: Point with index finger to draw on canvas
- **Clear**: Thumbs up to clear the canvas
- **AI Recognize**: Hold up four fingers for AI analysis
- **Save**: Peace sign to save your drawing
- **Stop**: Closed fist to stop drawing

### AI-Powered Recognition
- Real-time drawing recognition using Google Gemini AI
- Multiple analysis modes (Simple, Detailed, Creative, Educational)
- Recognition history and caching
- Performance analytics and statistics

### Advanced Drawing Features
- Customizable brush colors and thickness
- Visual effects (blur, glow, shadow)
- Multiple drawing modes
- Undo/redo functionality
- Auto-save capabilities

### Analytics & Performance
- Real-time FPS and latency monitoring
- Gesture usage analytics
- Drawing complexity analysis
- Session performance reports
- Export functionality

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Webcam/camera access
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-hand-drawing-recognition
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```
   This will:
   - Check system requirements
   - Install dependencies
   - Create necessary directories
   - Set up configuration files
   - Test camera access

3. **Add your API key**
   - Edit the `.env` file and add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
   - Or enter it directly in the app's sidebar

4. **Launch the application**
   ```bash
   streamlit run main.py
   ```
   Or use the generated launch scripts:
   - Windows: Double-click `run_app.bat`
   - Linux/macOS: Run `./run_app.sh`

## Requirements

Create a `requirements.txt` file with the following dependencies:

```
streamlit>=1.28.0
opencv-python>=4.8.0
cvzone>=1.6.1
google-generativeai>=0.3.0
Pillow>=10.0.0
numpy>=1.24.0
mediapipe>=0.10.0
protobuf>=3.20.0
```

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Project Structure

```
ai-hand-drawing-recognition/
├── main.py                     # Main Streamlit application
├── hand_gesture_manager.py     # Hand detection and gesture recognition
├── canvas_manager.py           # Drawing canvas management
├── ai_manager.py              # AI recognition and analysis
├── advanced_features.py       # Additional advanced features
├── utils.py                   # Utility functions
├── setup.py                   # Installation and setup script
├── requirements.txt           # Python dependencies
├── config.yaml               # Configuration file
├── README.md                 # This file
├── saved_drawings/           # Directory for saved drawings
├── logs/                     # Application logs
├── cache/                    # AI recognition cache
└── sessions/                 # Session data
```

## Configuration

### Camera Settings
- Adjust camera index in sidebar (0, 1, 2...)
- Resolution and FPS can be configured in `config.yaml`

### Hand Detection
- **Detection Confidence**: Minimum confidence for hand detection (0.1-1.0)
- **Tracking Confidence**: Minimum confidence for hand tracking (0.1-1.0)
- **Gesture Stability**: Time to hold gesture before confirmation

### Drawing Settings
- **Brush Color**: Choose any color for drawing
- **Brush Thickness**: Adjust stroke width (1-20px)
- **Canvas Effects**: Enable blur, glow, or shadow effects

### AI Settings
- **Analysis Depth**: Choose between Basic, Detailed, Creative, or Educational
- **Auto Recognition**: Automatically analyze drawings after inactivity
- **Caching**: Enable/disable result caching for performance

## Usage Guide

### Basic Drawing
1. Start the camera by checking "Run Camera"
2. Point your index finger to start drawing
3. Move your hand to create strokes
4. Make a fist to stop drawing without lifting

### AI Recognition
1. Draw something on the canvas
2. Hold up four fingers (all except pinky)
3. Wait for AI analysis to appear
4. View results in the "AI Recognition" panel

### Saving and Exporting
1. Use peace sign gesture or click "Save Drawing"
2. Drawings are saved in the `saved_drawings/` directory
3. Export session reports from the advanced features panel

### Performance Monitoring
- Enable FPS counter and latency monitoring in sidebar
- View gesture analytics and usage statistics
- Monitor drawing complexity and canvas utilization

## Troubleshooting

### Camera Issues
- **Camera not detected**: Try different camera indices (0, 1, 2...)
- **Permission denied**: Grant camera access in system settings
- **Poor detection**: Ensure good lighting and clear background

### Hand Detection Issues
- **Gestures not recognized**: Adjust detection confidence settings
- **Unstable tracking**: Increase tracking confidence
- **False positives**: Reduce detection sensitivity

### AI Recognition Issues
- **No recognition**: Check API key configuration
- **Slow responses**: Enable caching or reduce image quality
- **Poor accuracy**: Try different analysis modes

### Performance Issues
- **Low FPS**: Reduce camera resolution or disable effects
- **High latency**: Close other applications using camera
- **Memory usage**: Clear cache periodically

## Advanced Configuration

### Custom Gestures
Edit `config.yaml` to modify gesture patterns:
```yaml
gestures:
  patterns:
    draw: [0, 1, 0, 0, 0]      # Index finger up
    clear: [1, 0, 0, 0, 0]     # Thumb up
    # Add your custom patterns here
```

### AI Prompts
Customize AI analysis prompts in `ai_manager.py`:
```python
self.custom_prompts = {
    'custom': "Your custom prompt here",
    # Add more prompt types
}
```

### Performance Tuning
Adjust settings in `config.yaml`:
```yaml
performance:
  max_frame_rate: 30
  processing_threads: 2
  enable_gpu_acceleration: false
```

## Analytics Dashboard

The application provides comprehensive analytics:

### Gesture Analytics
- Total gestures used
- Most frequently used gestures
- Gestures per minute
- Usage distribution charts

### Drawing Statistics
- Canvas coverage percentage
- Drawing complexity metrics
- Total drawing points
- Session duration

### AI Performance
- Recognition accuracy
- Processing times
- Cache hit rates
- API usage statistics

## Contributing

We welcome contributions! Here's how to help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 *.py

# Format code
black *.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
