# utils.py
import os
import base64

def add_background(image_path: str, blur: int = 5):
    """Adds a background image with an optional blur effect to the Streamlit app."""
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file '{image_path}' not found.")
    
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    
    css_code = f"""
    <style>
    .stApp {{
        position: relative;
    }}
    .stApp::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: url("data:image/png;base64,{encoded_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        filter: blur({blur}px);
        z-index: -1; /* Ensures the background is behind the content */
    }}
    </style>
    """
    return css_code
