import streamlit as st
import requests
import PyPDF2

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
    .card { background-color: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6; }
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
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🎬 3D Scene Director</h1>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 1.8], gap="large")

with col1:
    st.subheader("📥 Input Content")
    input_type = st.radio("Input Source:", ["Manual Text", "PDF Document"])
    
    final_text = ""
    if input_type == "Manual Text":
        final_text = st.text_area("Paste Content:", height=300)
    else:
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_pdf:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in pdf_reader.pages:
                final_text += page.extract_text()
            st.success("PDF Content Extracted!")

    generate_btn = st.button("🚀 GENERATE 3D PRODUCTION BRIEF")

with col2:
    st.subheader("📋 5-6 Scene Production Table")
    
    if generate_btn and final_text:
        with st.spinner("Analyzing assets and workflow..."):
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
                            "Convert input into exactly 5-6 scenes. "
                            "Output a Markdown table with these EXACT columns: "
                            "Scene # | REQUIRED 3D ASSETS (Detailed list of models/props) | Animation Logic (GLB/Web) | Visual Description | Narration. "
                            "Ensure the 'Required 3D Assets' column lists specific models like 'Low-poly Heart Mesh', 'Procedural Blood Cells', etc."
                        )
                    },
                    {
                        "role": "user", 
                        "content": f"Create a detailed 3D asset-heavy storyboard for: {final_text}"
                    }
                ],
                "temperature": 0.2
            }
            
            try:
                response = requests.post(GROQ_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    st.markdown(response.json()['choices'][0]['message']['content'])
                    st.success("Asset List & Storyboard Ready!")
                else:
                    st.error("API Error. Please check your Groq Key.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()
st.caption("© 2026 LearningPad | Professional 3D Pipeline Tool")
