import cv2
import cvzone
import numpy as np
import google.generativeai as genai
from cvzone.HandTrackingModule import HandDetector
from PIL import Image
import streamlit as st

# Streamlit app configuration
st.set_page_config(layout='wide')
st.image('banner.png')

# Create columns for layout
col1, col2 = st.columns([2, 1])
with col1:
    run = st.checkbox('Run', value=True)
    FRAME_WINDOW = st.image([])

with col2:
    st.title("Answer")
    output_text_area = st.subheader("")

# Configure Gemini AI model
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize webcam and hand detector
cap = cv2.VideoCapture(0)
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.7, minTrackCon=0.5)

def get_hand_info(img):
    """Detect hand landmarks and finger positions."""
    hands, img = detector.findHands(img, draw=True, flipType=True)
    if hands:
        hand = hands[0]  # Get the first detected hand
        lmList = hand["lmList"]  # List of 21 landmarks
        fingers = detector.fingersUp(hand)  # Count fingers up
        return fingers, lmList
    return None

def draw_on_canvas(info, prev_pos, canvas):
    """Draw on the canvas based on finger positions."""
    fingers, lmList = info
    current_pos = None
    if fingers == [0, 1, 0, 0, 0]:  # Index finger up
        current_pos = tuple(map(int, lmList[8][0:2]))  # Get index finger tip position
        if prev_pos:
            cv2.line(canvas, prev_pos, current_pos, (255, 0, 255), 10)  # Draw line
    elif fingers == [1, 0, 0, 0, 0]:  # Thumb up (clear canvas)
        canvas = np.zeros_like(img)
    return current_pos, canvas

def query_ai(model, canvas, fingers):
    """Send canvas image to AI for analysis."""
    if fingers == [1, 1, 1, 1, 0]:  # All fingers except thumb up
        pil_image = Image.fromarray(canvas)
        response = model.generate_content(["Identify this image using format It's a [image_name]", pil_image])
        return response.text
    return ""

# Main loop
prev_pos = None
canvas = None
output_text = ""

while run:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Flip image for mirror effect

    if canvas is None:
        canvas = np.zeros_like(img)  # Initialize canvas

    hand_info = get_hand_info(img)
    if hand_info:
        fingers, _ = hand_info
        prev_pos, canvas = draw_on_canvas(hand_info, prev_pos, canvas)
        output_text = query_ai(model, canvas, fingers)

    # Combine webcam feed and canvas
    combined_image = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)
    FRAME_WINDOW.image(combined_image, channels="BGR")

    # Display AI response
    output_text_area.markdown(f"<h2>{output_text}</h2>", unsafe_allow_html=True)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()