import streamlit as st
import requests
import json

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad | 3D Storyboard AI",
    page_icon="🎬",
    layout="wide"
)

# Professional Studio Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0f172a; color: #f8fafc; }
    .stTextArea textarea { 
        background-color: #1e293b; color: #f1f5f9; 
        border: 1px solid #334155; border-radius: 12px; font-size: 16px;
    }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.8em; 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white; font-weight: 700; border: none; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIGURATION ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Setup Error: Please add 'GROQ_API_KEY' in your Streamlit Secrets.")
    st.stop()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/3d-model.png", width=70)
    st.title("Studio Panel")
    st.write("**Artist:** Raviteja")
    st.write("**Scene Limit:** 5-6 Scenes")
    st.divider()
    st.success("Groq LPU: Active")

# --- 4. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🎬 3D Storyboard Director</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Optimized 6-Scene Production Briefs</p>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 1.6], gap="large")

with col1:
    st.subheader("📥 Input Content")
    text_input = st.text_area("Paste script content:", height=400, placeholder="e.g., Photosynthesis process...")
    generate_btn = st.button("🚀 GENERATE STORYBOARD")

with col2:
    st.subheader("📋 Production Specifications")
    
    if generate_btn:
        if text_input:
            with st.spinner("Optimizing into 6 essential scenes..."):
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
                                "STRICT CONSTRAINT: Convert the input into EXACTLY 5 to 6 scenes. No more, no less. "
                                "Output a Markdown table: Scene # | 3D Assets | Animation Logic | Narration. "
                                "Make sure the entire content is summarized within these 6 scenes for a fast-paced educational video."
                            )
                        },
                        {
                            "role": "user", 
                            "content": f"Create a 6-scene production brief for: {text_input}"
                        }
                    ],
                    "temperature": 0.2
                }
                
                try:
                    response = requests.post(GROQ_URL, headers=headers, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        st.markdown(result['choices'][0]['message']['content'])
                        st.success("Concise Storyboard Generated!")
                    else:
                        st.error(f"Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection Failed: {str(e)}")
        else:
            st.warning("Input is empty.")

st.write("---")
st.caption("© 2026 LearningPad | 5-6 Scene Optimization Mode")
