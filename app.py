import streamlit as st
import requests
import json

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad | 3D Storyboard AI",
    page_icon="🎬",
    layout="wide"
)

# Professional English UI Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; color: #1d1d1f; }
    .stTextArea textarea { border-radius: 10px; border: 1px solid #d2d2d7; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3.5em; 
        background-color: #0071e3; color: white; font-weight: 700; border: none; 
    }
    .stButton>button:hover { background-color: #005bb5; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIGURATION (SECURE) ---
# Key will be pulled from Streamlit Secrets
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Setup Error: Please add 'OPENAI_API_KEY' in your Streamlit Secrets dashboard.")
    st.stop()

OPENAI_URL = "https://api.openai.com/v1/chat/completions"

# --- 3. MAIN INTERFACE ---
st.title("🎬 3D Storyboard Director")
st.write("Convert textbook chapters into production-ready 3D Artist briefs.")
st.divider()

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📥 Input Content")
    text_input = st.text_area("Paste Textbook Content or Script:", height=450, placeholder="e.g., Structure of the Human Heart...")
    generate_btn = st.button("🚀 GENERATE PRODUCTION BRIEF")

with col2:
    st.subheader("📋 Technical 3D Storyboard")
    
    if generate_btn:
        if text_input:
            with st.spinner("AI is generating technical 3D specifications..."):
                headers = {
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": "You are a Senior 3D Technical Director. Convert text into a professional Markdown table. Columns: Scene #, 3D Assets & Visuals, Animation Logic (GLB Safe), Labels/UI, Narration Script. Use English only."},
                        {"role": "user", "content": f"Create a technical storyboard for: {text_input}"}
                    ]
                }
                
                try:
                    response = requests.post(OPENAI_URL, headers=headers, json=payload)
                    result = response.json()
                    
                    if response.status_code == 200:
                        output = result['choices'][0]['message']['content']
                        st.markdown(output)
                        st.success("Successfully Generated via GPT-4o")
                        st.balloons()
                    else:
                        st.error(f"Error: {result.get('error', {}).get('message')}")
                except Exception as e:
                    st.error(f"Connection Failed: {str(e)}")
        else:
            st.warning("Please enter content to proceed.")

st.divider()
st.caption("© 2026 LearningPad | Professional 3D Pipeline Tool")
