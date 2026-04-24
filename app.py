import streamlit as st
import requests
import PyPDF2

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="LearningPad | 3D Scene Director", layout="wide")

# Studio Styling
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.5em; 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white; font-weight: 700; border: none;
    }
    .stTextArea textarea { background-color: #1e293b; color: #f1f5f9; border-radius: 12px; }
    table { background-color: #1e293b; color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GROQ API CONFIG ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Please add 'GROQ_API_KEY' in Streamlit Secrets.")
    st.stop()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- 3. MAIN UI ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🎬 3D Scene Director Pro</h1>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📥 Input Source")
    input_type = st.radio("Input Type:", ["Direct Text", "PDF Document"])
    
    final_text = ""
    if input_type == "Direct Text":
        final_text = st.text_area("Paste Production Script:", height=350)
    else:
        uploaded_pdf = st.file_uploader("Upload Chapter PDF", type=["pdf"])
        if uploaded_pdf:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in pdf_reader.pages:
                final_text += page.extract_text()
            st.success("PDF Data Extracted Successfully!")

    generate_btn = st.button("🚀 GENERATE 6-SCENE PRODUCTION BRIEF")

with col2:
    st.subheader("📋 Production Storyboard & Assets")
    
    if generate_btn and final_text:
        with st.spinner("Calculating 3D assets, labels, and visual references..."):
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
                            "Convert input into exactly 6 production scenes. "
                            "Output a Markdown table with these columns: "
                            "Scene # | Required Assets (Models/Props) | Labels (UI Text Overlays) | Animation Logic (GLB Safe) | Visual Reference (Description for Artist) | Narration. "
                            "Ensure 'Labels' column lists exactly what text should appear on screen (e.g., 'Nucleus', 'Mitochondria'). "
                            "The 'Visual Reference' should describe lighting, colors, and camera angles for the 3D artist."
                        )
                    },
                    {
                        "role": "user", 
                        "content": f"Create a technical storyboard for: {final_text}"
                    }
                ],
                "temperature": 0.2
            }
            
            try:
                response = requests.post(GROQ_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    st.markdown(response.json()['choices'][0]['message']['content'])
                    st.success("Production Brief with Labels & References Generated!")
                    st.balloons()
                else:
                    st.error("API Error. Please check your Groq Key.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()
st.caption("© 2026 LearningPad | 3D Generalist Pipeline Tool | Optimized for GLB/Web")
