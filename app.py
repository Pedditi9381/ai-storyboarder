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
    .stTextArea textarea { font-family: 'Inter', sans-serif; font-size: 14px; border-radius: 8px; border: 1px solid #d1d1d1; }
    .stButton>button { 
        width: 100%; 
        border-radius: 6px; 
        height: 3.5em; 
        background-color: #1a73e8; 
        color: white; 
        font-weight: 600;
        border: none;
    }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIGURATION ---
# Using your new AI Studio Key
API_KEY = "AIzaSyAm5-eoRL24iN8cLfz97riLdKhw9pRNq8U"
# Using v1beta for maximum compatibility with Gemini 3 Flash
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Control Panel")
    st.info("**Engine:** Gemini 3 Flash\n\n**Mode:** High-Speed Production\n\n**Target:** 3D Artist Brief")
    st.divider()
    st.caption("LearningPad Internal Tool")

# --- 4. MAIN INTERFACE ---
st.title("🎬 3D Storyboard Director")
st.write("Instant Technical Storyboarding for 3D Production")
st.divider()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📥 Source Content")
    text_input = st.text_area(
        "Paste Textbook Content Here:", 
        height=450, 
        placeholder="Example: Explain the working principle of an Electric Motor..."
    )
    generate_btn = st.button("GENERATE TECHNICAL BRIEF")

with col2:
    st.subheader("📋 3D Artist production Table")
    
    if generate_btn:
        if text_input:
            with st.spinner("Gemini 3 Flash is analyzing technical requirements..."):
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": (
                                "Act as a Senior 3D Technical Director. Convert the following text into a technical storyboard for a 3D Artist. "
                                "Focus on GLB-safe animation (Bones/Shape keys). Use professional English. "
                                "Format: Markdown Table with columns: Scene #, Visuals & Assets, Animation Logic, Labels, Narration.\n\n"
                                f"Content: {text_input}"
                            )
                        }]
                    }]
                }
                headers = {'Content-Type': 'application/json'}
                
                try:
                    response = requests.post(API_URL, headers=headers, json=payload)
                    result = response.json()
                    
                    if response.status_code == 200:
                        output_text = result['candidates'][0]['content']['parts'][0]['text']
                        st.markdown(output_text)
                        st.success("Generation Successful!")
                        st.balloons()
                    else:
                        error_msg = result.get('error', {}).get('message', 'Unknown Error')
                        st.error(f"API Error: {error_msg}")
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")
        else:
            st.warning("Please enter text content first.")

st.divider()
st.caption("Powered by Gemini 3 Flash | Developed by Raviteja")
