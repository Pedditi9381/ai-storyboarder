import streamlit as st
import requests
import json

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad | 3D Asset Director",
    page_icon="🎬",
    layout="wide"
)

# Professional Studio UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #0f172a; color: #f8fafc; }
    
    /* Input Area Styling */
    .stTextArea textarea { 
        background-color: #1e293b; 
        color: #f1f5f9; 
        border: 1px solid #334155;
        border-radius: 12px;
    }
    
    /* Button Styling - Studio Blue */
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
        height: 3.8em; 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white; 
        font-weight: 700;
        border: none;
        transition: 0.3s;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIGURATION ---
# Make sure you have 'GROQ_API_KEY' in your Streamlit Secrets
try:
    GROQ_API_KEY = st.secrets["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"]
except Exception:
    st.error("Setup Error: Please add 'GROQ_API_KEY' in your Streamlit Secrets dashboard.")
    st.stop()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/3d-model.png", width=70)
    st.title("Studio Panel")
    st.markdown("---")
    st.write("**Artist:** Raviteja")
    st.write("**Pipeline:** 3D Generalist")
    st.divider()
    st.success("Engine: Groq LPU (Active)")

# --- 4. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🎬 3D Storyboard Director</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Transform Educational Content into Technical 3D Production Briefs</p>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📥 Textbook Content")
    text_input = st.text_area(
        "Paste script or textbook text here:", 
        height=450, 
        placeholder="e.g., The internal combustion engine works in four strokes..."
    )
    generate_btn = st.button("🚀 GENERATE STORYBOARD")

with col2:
    st.subheader("📋 Production Specifications")
    
    if generate_btn:
        if text_input:
            with st.spinner("Analyzing assets and animation logic..."):
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
                                "You are a Senior 3D Technical Director for LearningPad. "
                                "Task: Convert input text into a detailed Markdown table. "
                                "Columns: Scene # | 3D Assets (Models) | Animation Logic (GLB Safe) | Labels/UI | Narration Script. "
                                "Constraint: Suggest high-quality, optimized 3D workflows only. English language."
                            )
                        },
                        {
                            "role": "user", 
                            "content": f"Create a technical 3D storyboard for: {text_input}"
                        }
                    ],
                    "temperature": 0.2
                }
                
                try:
                    response = requests.post(GROQ_URL, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        output = result['choices'][0]['message']['content']
                        st.markdown(output)
                        st.success("Brief Generated Successfully!")
                        st.balloons()
                    else:
                        st.error(f"Engine Error: {response.status_code}")
                        st.info("Check if your Groq API key is valid.")
                except Exception as e:
                    st.error(f"Connection Failed: {str(e)}")
        else:
            st.warning("Please enter content to continue.")

# --- 5. FOOTER ---
st.write("---")
st.caption("© 2026 LearningPad | Professional 3D Pipeline Tool | Powered by Groq LPU")
