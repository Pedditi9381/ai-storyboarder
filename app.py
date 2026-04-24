import streamlit as st
import requests
import PyPDF2

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="LearningPad | 3D Asset Director", layout="wide")

# Studio Styling
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3em; 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white; font-weight: 600; border: none;
    }
    .img-box { border: 2px solid #334155; border-radius: 12px; padding: 10px; background: #1e293b; }
    .stTextArea textarea { background-color: #1e293b; color: #f1f5f9; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIG ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Please add 'GROQ_API_KEY' in Streamlit Secrets.")
    st.stop()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- 3. SESSION STATE FOR IMAGES ---
if 'scene_images' not in st.session_state:
    st.session_state.scene_images = {}

# --- 4. MAIN INTERFACE ---
st.title("🎬 3D Scene Director & Visualizer")
st.write("---")

col_in, col_out = st.columns([1, 2], gap="large")

with col_in:
    st.subheader("⚙️ Production Controls")
    num_scenes = st.slider("Total Scenes:", 3, 10, 6)
    input_type = st.radio("Source:", ["Text", "PDF"])
    
    raw_text = ""
    if input_type == "Text":
        raw_text = st.text_area("Input Script:", height=250)
    else:
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_pdf:
            reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in reader.pages:
                raw_text += page.extract_text()

    if st.button(f"🚀 ANALYZE & GENERATE {num_scenes} SCENES"):
        if raw_text:
            with st.spinner("LPU Engine is architecting scenes..."):
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": f"You are a 3D Director. Convert content into exactly {num_scenes} JSON-formatted scenes. Each scene MUST have: 'scene_no', 'assets', 'labels', 'animation', 'visual_prompt', 'narration'."},
                        {"role": "user", "content": f"Return ONLY a JSON list of {num_scenes} scenes for: {raw_text}"}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.1
                }
                
                res = requests.post(GROQ_URL, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    # Groq might wrap the list in a key like 'scenes'
                    st.session_state.storyboard = data.get('scenes', list(data.values())[0])
                    st.session_state.scene_images = {} # Reset images
                else:
                    st.error("API Error.")

# --- 5. VISUALIZATION OUTPUT ---
with col_out:
    if 'storyboard' in st.session_state:
        st.subheader(f"📋 Storyboard Pipeline ({len(st.session_state.storyboard)} Scenes)")
        
        for idx, scene in enumerate(st.session_state.storyboard):
            with st.container():
                s_col1, s_col2 = st.columns([2, 1])
                
                with s_col1:
                    st.markdown(f"### Scene {scene['scene_no']}")
                    st.write(f"**📦 Assets:** {scene['assets']}")
                    st.write(f"**🏷️ Labels:** {scene['labels']}")
                    st.write(f"**⚙️ Logic:** {scene['animation']}")
                    st.info(f"🎙️ {scene['narration']}")
                
                with s_col2:
                    st.write(" ") # Padding
                    prompt = scene.get('visual_prompt', '3D educational model')
                    if st.button(f"🎨 Generate Preview {idx+1}", key=f"btn_{idx}"):
                        img_url = f"https://image.pollinations.ai/prompt/3d%20scientific%20model%20of%20{prompt.replace(' ', '%20')}%20educational%20style%20blender%20render?width=600&height=400&nologo=true"
                        st.session_state.scene_images[idx] = img_url
                    
                    if idx in st.session_state.scene_images:
                        st.image(st.session_state.scene_images[idx], use_container_width=True)
                
                st.write("---")
    else:
        st.info("Input content and click Generate to see the storyboard.")

st.caption("© 2026 LearningPad | 3D Pipeline Visualizer")
