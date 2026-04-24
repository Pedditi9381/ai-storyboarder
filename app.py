import streamlit as st
import requests
import json

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad | 3D Storyboard AI",
    page_icon="🎬",
    layout="wide"
)

# Professional Studio UI Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #0e1117; color: #ffffff; }
    .stTextArea textarea { 
        background-color: #161b22; 
        color: #e6edf3; 
        border: 1px solid #30363d;
        border-radius: 10px;
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        background: linear-gradient(90deg, #1f6feb 0%, #114ba8 100%);
        color: white; 
        font-weight: 700;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { 
        background: linear-gradient(90deg, #388bfd 0%, #1f6feb 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.3);
    }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #161b22;
        border-left: 5px solid #1f6feb;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIGURATION ---
# Using your new key
API_KEY = "AIzaSyBzDQ-ro7rXVgX2BGaBuzC2EOZ_pt4tt1M"
# Standardizing to v1beta for Gemini 1.5 Flash
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/3d-model.png", width=70)
    st.title("Production Control")
    st.markdown("---")
    st.write("**Artist:** Raviteja")
    st.write("**Project:** LearningPad v3.0")
    st.write("**Engine:** Gemini 3 Flash")
    st.divider()
    st.success("API Status: Connected")

# --- 4. MAIN INTERFACE ---
st.markdown("# 🎬 AI Storyboard Director")
st.markdown("##### Transform Educational Text into Production-Ready 3D Briefs")
st.write("---")

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📥 Textbook Content")
    text_input = st.text_area(
        "Paste the chapter content or script here:", 
        height=400, 
        placeholder="e.g., Working of the Human Heart, Layers of the Earth..."
    )
    generate_btn = st.button("🚀 GENERATE STORYBOARD")

with col2:
    st.subheader("📋 3D Artist Specifications")
    
    if generate_btn:
        if text_input:
            with st.spinner("Analyzing geometry and animation logic..."):
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": (
                                "Act as a Senior 3D Technical Director for LearningPad. "
                                "Task: Convert the provided educational text into a technical 3D storyboard table. "
                                "Constraint: Suggest GLB-safe animations only (Shape keys/Skeletal). "
                                "Language: English. "
                                "Format: Markdown Table with columns: [Scene #] | [3D Assets & Visuals] | [Animation Logic] | [Labels/UI] | [Narration Script]"
                                f"\n\nContent: {text_input}"
                            )
                        }]
                    }]
                }
                
                try:
                    response = requests.post(API_URL, json=payload)
                    result = response.json()
                    
                    if response.status_code == 200:
                        output = result['candidates'][0]['content']['parts'][0]['text']
                        st.markdown(output)
                        st.balloons()
                    else:
                        error_msg = result.get('error', {}).get('message', 'Unknown API Error')
                        st.error(f"Engine Error: {error_msg}")
                        st.info("Check if your API key has the 'Generative Language API' enabled in AI Studio.")
                except Exception as e:
                    st.error(f"Connection Failed: {str(e)}")
        else:
            st.warning("Please input textbook content to begin.")

# --- 5. FOOTER ---
st.write("---")
st.caption("© 2026 LearningPad | Professional 3D Pipeline Tool | Powered by Gemini 3")
