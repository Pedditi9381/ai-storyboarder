import streamlit as st
import requests
import json

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad AI | Storyboard Director",
    page_icon="🎬",
    layout="wide"
)

# Professional Studio UI Styling
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stTextArea textarea { font-family: 'Inter', sans-serif; font-size: 14px; border-radius: 8px; }
    .stButton>button { 
        width: 100%; 
        border-radius: 6px; 
        height: 3.5em; 
        background-color: #1a73e8; 
        color: white; 
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover { background-color: #1557b0; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIGURATION ---
API_KEY = "AIzaSyC00GP4p153fnGdrywn60AONQuueLKnF7c"

# CHANGED: Using v1beta endpoint which explicitly supports gemini-1.5-flash
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# --- 3. SIDEBAR / INFO ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Admin Console")
    st.info("**Environment:** Production\n\n**Engine:** Gemini 3 Flash (v1beta)\n\n**Pipeline:** 3D Asset Creation")
    st.divider()
    st.caption("Developed for LearningPad 3D Production")

# --- 4. MAIN INTERFACE ---
st.title("🎬 3D Storyboard Director")
st.write("Instant conversion of textbook content into technical 3D production briefs.")
st.divider()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📥 Source Content")
    text_input = st.text_area(
        "Enter Textbook/Script Text:", 
        height=400, 
        placeholder="e.g., Describe the process of Mitosis..."
    )
    generate_btn = st.button("GENERATE PRODUCTION BRIEF")

with col2:
    st.subheader("📋 Technical Production Brief")
    
    if generate_btn:
        if text_input:
            with st.spinner("Processing through Gemini 3 Engine (v1beta)..."):
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": (
                                "Act as a Senior 3D Technical Director. Convert the following text into a technical storyboard. "
                                "Focus on educational accuracy and GLB-safe animation (Bones/Shape keys). "
                                "Format the output as a Markdown Table with columns: Scene #, Visuals & 3D Assets, "
                                "Animation Logic, Labels & UI, Narration Script.\n\n"
                                f"Content: {text_input}"
                            )
                        }]
                    }]
                }
                headers = {'Content-Type': 'application/json'}
                
                try:
                    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
                    result = response.json()
                    
                    if response.status_code == 200:
                        try:
                            output_text = result['candidates'][0]['content']['parts'][0]['text']
                            st.markdown(output_text)
                            st.success("Generation Complete.")
                        except (KeyError, IndexError):
                            st.error("Model returned an unexpected format. Try again.")
                    else:
                        # Displaying specific error message from Google
                        error_msg = result.get('error', {}).get('message', 'Unknown API Error')
                        st.error(f"API Error {response.status_code}: {error_msg}")
                        st.info("Check if your API Key is restricted to v1beta in Google Cloud Console.")
                        
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")
        else:
            st.warning("Please enter source content first.")

st.divider()
st.caption("© 2026 LearningPad AI Suite | Gemini 3 Engine (REST v1beta)")
