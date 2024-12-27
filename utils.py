# utils.py
import base64

def add_background(image_path: str, blur: int = 5):
    """Adds a background image with an optional blur effect to the Streamlit app."""
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    css_code = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        filter: blur({blur}px); /* Apply the blur effect */
    }}
    </style>
    """
    return css_code
