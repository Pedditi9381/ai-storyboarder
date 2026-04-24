import streamlit as st
import requests
import json

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad | 3D Storyboard AI",
    page_icon="🎬",
    layout="wide"
)

# Professional Studio Styling (Inter font & Studio Blue)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #0f172a; color: #f8fafc; }
    
    /* Input Area */
    .stTextArea textarea { 
        background-color: #1e293b; 
        color: #f1f5f9; 
        border: 1px solid #334155;
        border-radius: 12px;
        font-size: 16px;
    }
    
    /* Studio Button */
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
    }
    
    .stButton>button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
    }

    /* Output Card */
    .output-container {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIGURATION ---
# Assumes GROQ_API_KEY is saved in Streamlit Secrets
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
    st.markdown("---")
    st.write("**Artist:** Raviteja")
    st.write("**Workflow:** 3D Generalist")
    st.write("**Target:** GLB/Web Engine")
    st.divider()
    st.success("Engine: Groq LPU (Online)")

# --- 4. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🎬 3D Storyboard Director</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>Production-Ready Asset Planning & Animation Briefs</p>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 1.6], gap="large")

with col1:
    st.subheader("📥 Textbook Content")
    text_input = st.text_area(
        "Paste textbook chapter or script content here:", 
        height=450, 
        placeholder="Example: Structure of an atom with protons, neutrons, and electrons..."
    )
    generate_btn = st.button("🚀 GENERATE STORYBOARD")

with col2:
    st.subheader("📋 Production Specifications")
    
    if generate_btn:
        if text_input:
            with st.spinner("Groq LPU is calculating technical specifications..."):
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
                                "You are a Senior 3D Technical Director for an educational media house. "
                                "Output a professional Markdown table. "
                                "Columns: Scene # | 3D Assets (Models) | Animation Logic (GLB Safe) | Labels/UI | Narration Script. "
                                "Focus on high-quality visuals and technical feasibility. English only."
                            )
                        },
                        {
                            "role": "user", 
                            "content": f"Create a production storyboard for: {text_input}"
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
                        st.success("Brief Generated at Light Speed!")
                        st.balloons()
                    else:
                        st.error(f"Engine Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection Failed: {str(e)}")
        else:
            st.warning("Input content is empty.")

# --- 5. FOOTER ---
st.write("---")
st.caption("© 2026 LearningPad | 3D Production Intelligence | Powered by Groq")
