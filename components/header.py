import streamlit as st
import os
import base64

def display_header():
    """Display Roy's logo, header and subtitle"""
    # Assuming your assets folder is at the root of your project
    image_path = "assets/roy.png"  # Update this path to match your image's location
    
    # Check if the image exists
    if os.path.exists(image_path):
        # Use HTML/CSS for more precise control over the image size and centering
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; margin-bottom: 30px;">
                <img src="data:image/png;base64,{get_base64_encoded_image(image_path)}" 
                     style="width: 250px; height: auto;" alt="Roy - AI Launch Advisor">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Fallback to the placeholder if image not found
        roy_image_html = """
        <div style="display: flex; justify-content: center; margin-bottom: 30px;">
            <div style="width: 250px; height: 250px; background-color: #2C3E50; border-radius: 50%; 
                    display: flex; justify-content: center; align-items: center; color: white; font-weight: bold; font-size: 36px;">
                Roy
            </div>
        </div>
        """
        st.markdown(roy_image_html, unsafe_allow_html=True)
    
    # Header and subtitle
    st.markdown('<div class="main-header">Launch Smarter with Roy</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">I\'ve studied the strategies behind thousands of launches. Let\'s create one that gets your startup seen, trusted, and funded.</div>', unsafe_allow_html=True)

def get_base64_encoded_image(image_path):
    """Convert an image to base64 encoding for embedding in HTML"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

def display_footer():
    """Display footer with credit"""
    st.markdown("<div style='text-align: right; color: #888; font-size: 0.8rem; margin-top: 20px;'>Stephanie LaFlora</div>", unsafe_allow_html=True)