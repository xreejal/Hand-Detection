# AI Air Drawing Recognition App

A real-time hand gesture-controlled drawing application that uses computer vision to detect hand movements and AI to recognize drawn shapes. Draw in the air with your finger and get instant AI-powered recognition of what you've drawn!

## Features

- **Air Drawing**: Draw in the air using your index finger
- **Real-time Hand Detection**: Detects hand landmarks and finger positions using MediaPipe
- **AI Recognition**: Uses Google's Gemini AI to identify drawn shapes and objects
- **Interactive Web Interface**: Built with Streamlit for easy use
- **Gesture Controls**:
  - Index finger up: Draw mode
  - Thumb up: Clear canvas
  - Four fingers up (except thumb): Trigger AI recognition

## Prerequisites

- Python 3.7+
- Webcam/Camera
- Google Gemini API key

## Installation

1. Clone this repository or download the code files

2. Install required packages:
```bash
pip install opencv-python
pip install cvzone
pip install numpy
pip install google-generativeai
pip install Pillow
pip install streamlit
```

3. Get a Google Gemini API key:
   - Visit [Google AI Studio](https://makersuite.google.com/)
   - Create an account and generate an API key
   - Replace `"YOUR_API_KEY"` in the code with your actual API key

4. Add a banner image:
   - Place a `banner.png` file in the same directory as the script
   - This will be displayed at the top of the app

## Usage

1. Run the application:
```bash
streamlit run app.py
```

2. The app will open in your web browser

3. Make sure your webcam is working and you're visible in the frame

4. Use hand gestures to interact:
   - **Draw**: Raise only your index finger and move it to draw
   - **Clear**: Raise only your thumb to clear the canvas
   - **Recognize**: Raise four fingers (index, middle, ring, pinky) to ask AI what you drew

## How It Works

1. **Hand Detection**: Uses CVZone's HandTrackingModule (based on MediaPipe) to detect hand landmarks
2. **Gesture Recognition**: Analyzes finger positions to determine current gesture
3. **Drawing System**: Tracks index finger movement to create lines on a virtual canvas
4. **AI Integration**: Sends canvas image to Google Gemini AI for object recognition
5. **Real-time Display**: Combines webcam feed with drawing overlay using Streamlit

## File Structure

```
├── app.py              # Main application file
├── banner.png          # Banner image for the app
└── README.md           # This file
```

## Configuration Options

You can modify these parameters in the code:

- `maxHands=1`: Maximum number of hands to detect
- `detectionCon=0.7`: Hand detection confidence threshold
- `minTrackCon=0.5`: Hand tracking confidence threshold
- Drawing line thickness: Currently set to 10 pixels
- Canvas opacity: 30% overlay on webcam feed

## Troubleshooting

**Camera not working:**
- Check if another application is using the camera
- Try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` for external cameras

**Hand detection issues:**
- Ensure good lighting
- Keep hand clearly visible in frame
- Adjust detection confidence if needed

**API errors:**
- Verify your Gemini API key is correct
- Check your internet connection
- Ensure you haven't exceeded API rate limits

**Performance issues:**
- Close other applications using the camera
- Reduce image resolution if needed
- Check CPU usage

## Dependencies

- `opencv-python`: Computer vision operations
- `cvzone`: Hand tracking and detection
- `numpy`: Array operations
- `google-generativeai`: Gemini AI integration
- `Pillow`: Image processing
- `streamlit`: Web interface

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Acknowledgments

- CVZone for the hand tracking module
- Google for the Gemini AI API
- MediaPipe for hand landmark detection
- Streamlit for the web interface
