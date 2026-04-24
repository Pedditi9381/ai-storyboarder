import streamlit as st
import requests
import PyPDF2
import json

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad | 3D Scene Director",
    page_icon="🎬",
    layout="wide"
)

# Professional UI Styling
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stTextArea textarea { background-color: #1e293b; color: #f1f5f9; border-radius: 12px; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.5em; 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white; font-weight: 700; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GROQ API CONFIG ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Setup Error: Please add 'GROQ_API_KEY' in Streamlit Secrets.")
    st.stop()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- 3. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🎬 3D Scene Director</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Transform Content into 5-6 Production Scenes</p>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 1.6], gap="large")

with col1:
    st.subheader("📥 Input Content")
    input_type = st.radio("Choose Input Type:", ["Text/Script", "PDF Document"])
    
    final_text = ""
    
    if input_type == "Text/Script":
        final_text = st.text_area("Paste Content:", height=300, placeholder="e.g., How an electric motor works...")
    
    elif input_type == "PDF Document":
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_pdf:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text()
            final_text = extracted_text
            st.success("PDF Content Extracted!")

    generate_btn = st.button("🚀 GENERATE STORYBOARD")

with col2:
    st.subheader("📋 Production Specifications")
    
    if generate_btn:
        if final_text:
            with st.spinner("Groq LPU is analyzing and designing scenes..."):
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {
                            "role": "system", 
                            "content": (
                                "You are a Senior 3D Technical Director. "
                                "Task: Convert the input into exactly 5 to 6 scenes for a 3D educational video. "
                                "Output Format: A Markdown table with columns: "
                                "Scene # | 3D Assets | Animation Logic (GLB Safe) | Visual Description | Narration Script. "
                                "Keep logic optimized for web-based GLB export. Use English only."
                            )
                        },
                        {
                            "role": "user", 
                            "content": f"Create a 3D storyboard for: {final_text}"
                        }
                    ],
                    "temperature": 0.3
                }
                
                try:
                    response = requests.post(GROQ_URL, headers=headers, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        st.markdown(result['choices'][0]['message']['content'])
                        st.success("Storyboard Ready!")
                        st.balloons()
                    else:
                        st.error(f"Engine Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection Failed: {str(e)}")
        else:
            st.warning("Please provide input content.")

st.divider()
st.caption("© 2026 LearningPad | Professional 3D Pipeline Tool | Powered by Groq")
