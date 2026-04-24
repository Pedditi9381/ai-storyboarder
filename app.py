import streamlit as st
import requests
import PyPDF2

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="LearningPad | Custom 3D Director", layout="wide")

# Custom UI Styling
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        color: white; font-weight: 700; border: none;
    }
    .stTextArea textarea { background-color: #1e293b; color: #f1f5f9; border-radius: 12px; }
    /* Slider Color */
    .stSlider [data-baseweb="slider"] { color: #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIG ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Setup Error: Please add 'GROQ_API_KEY' in Streamlit Secrets.")
    st.stop()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- 3. MAIN UI ---
st.title("🎬 Custom 3D Scene Director")
st.write("---")

col1, col2 = st.columns([1, 1.8], gap="large")

with col1:
    st.subheader("📥 Input & Controls")
    
    # Scene Selection Option
    num_scenes = st.slider("Select Number of Scenes:", min_value=3, max_value=12, value=6)
    
    input_type = st.radio("Input Source:", ["Manual Text", "PDF Document"])
    
    final_text = ""
    if input_type == "Manual Text":
        final_text = st.text_area("Paste Content:", height=250, placeholder="e.g., Working of a Steam Engine...")
    else:
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_pdf:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in pdf_reader.pages:
                final_text += page.extract_text()
            st.success("PDF Content Extracted!")

    generate_btn = st.button(f"🚀 GENERATE {num_scenes} SCENES")

with col2:
    st.subheader(f"📋 {num_scenes}-Scene Production Brief")
    
    if generate_btn and final_text:
        with st.spinner(f"Groq is designing {num_scenes} scenes..."):
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
                            f"You are a Senior 3D Technical Director. "
                            f"Task: Convert input into EXACTLY {num_scenes} scenes. "
                            "Output a Markdown table with columns: "
                            "Scene # | Required 3D Assets | Labels (UI Text) | Animation Logic (GLB Safe) | Visual Description | Narration. "
                            "After the table, provide one main keyword for a visual reference image."
                        )
                    },
                    {
                        "role": "user", 
                        "content": f"Create a detailed 3D storyboard for: {final_text}"
                    }
                ],
                "temperature": 0.2
            }
            
            try:
                response = requests.post(GROQ_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    result_text = response.json()['choices'][0]['message']['content']
                    st.markdown(result_text)
                    
                    # --- DYNAMIC IMAGE LOGIC ---
                    st.write("---")
                    st.subheader("🖼️ Visual Asset Reference")
                    # Extracting a keyword for the image (fallback to input)
                    img_keyword = final_text[:20].split()[0] if final_text else "3D"
                    # Using Pollinations.ai for reliable image generation
                    img_url = f"https://image.pollinations.ai/prompt/3d%20model%20of%20{img_keyword}%20educational%20style%20high%20detail?width=1080&height=600&nologo=true"
                    st.image(img_url, caption=f"AI Generated Reference for: {img_keyword}")
                    
                    st.success(f"Production brief for {num_scenes} scenes ready!")
                    st.balloons()
                else:
                    st.error("Engine Error. Please check API Key.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()
st.caption("© 2026 LearningPad | AI 3D Pipeline Tools")
