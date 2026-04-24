import streamlit as st
import google.generativeai as genai
import PyPDF2
from PIL import Image
import io

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="LearningPad | 3D Scene Director", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.5em; 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white; font-weight: 700; border: none;
    }
    .stTextArea textarea { background-color: #1e293b; color: #f1f5f9; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIG ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Please add 'GEMINI_API_KEY' in Streamlit Secrets.")
    st.stop()

# --- 3. MAIN UI ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🎬 3D Scene Director (Multimodal)</h1>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 1.6], gap="large")

with col1:
    st.subheader("📥 Input Source")
    input_type = st.radio("Choose Input Type:", ["Text", "Image (Textbook Scan)", "PDF Document"])
    
    user_content = None
    
    if input_type == "Text":
        user_content = st.text_area("Paste Content:", height=250)
    elif input_type == "Image (Textbook Scan)":
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            user_content = Image.open(uploaded_file)
            st.image(user_content, caption="Uploaded Scan", width=300)
    elif input_type == "PDF Document":
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_pdf:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            user_content = ""
            for page in pdf_reader.pages:
                user_content += page.extract_text()
            st.success("PDF Content Extracted!")

    generate_btn = st.button("🚀 GENERATE 5-6 SCENES")

with col2:
    st.subheader("📋 Production Specifications")
    
    if generate_btn:
        if user_content:
            with st.spinner("Analyzing content and designing scenes..."):
                prompt = """
                Act as a Senior 3D Technical Director. 
                Task: Convert the provided content into exactly 5 to 6 scenes for a 3D educational video.
                Output Format: A Markdown table with:
                1. Scene #
                2. 3D Assets (Required models)
                3. Animation Logic (GLB/Web friendly)
                4. Visual Description
                5. Narration Script
                
                Keep the logic optimized for mobile/web GLB export. Use technical 3D terms.
                """
                
                try:
                    # Gemini handles both text and images automatically
                    response = model.generate_content([prompt, user_content] if input_type == "Image (Textbook Scan)" else [prompt, user_content])
                    st.markdown(response.text)
                    st.success("Production Brief Ready!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please provide input content first.")

st.divider()
st.caption("© 2026 LearningPad | Professional 3D Multimodal Pipeline")
