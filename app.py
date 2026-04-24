import streamlit as st
import google.generativeai as genai

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
    .stTextArea textarea { font-family: 'Inter', sans-serif; font-size: 14px; }
    .stButton>button { 
        width: 100%; 
        border-radius: 4px; 
        height: 3em; 
        background-color: #2c3e50; 
        color: white; 
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover { background-color: #34495e; color: #ecf0f1; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIGURATION ---
API_KEY = "AIzaSyBxgHlVyOWCxx9itHzGY_V7E-pgjpuDxM0"
genai.configure(api_key=API_KEY)

# --- 3. SIDEBAR / INFO ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Production Settings")
    st.info("**Pipeline:** 3D Educational Animation\n\n**Target:** GLB / Web-3D")
    st.divider()
    st.caption("LearningPad 3D Production Suite")

# --- 4. MAIN INTERFACE ---
st.title("🎬 3D Storyboard Director")
st.write("Generate technical 3D briefs from textbook content.")
st.divider()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📥 Source Content")
    text_input = st.text_area(
        "Paste Textbook Text:", 
        height=450, 
        placeholder="e.g., The working of a DC Motor..."
    )
    generate_btn = st.button("GENERATE BRIEF")

with col2:
    st.subheader("📋 3D Technical Storyboard")
    
    if generate_btn:
        if text_input:
            with st.spinner("Accessing Gemini AI engine..."):
                # FALLBACK LOGIC: Try different model strings to bypass 404
                success = False
                # Priority: Stable Pro -> Flash (no prefix) -> Latest
                model_names = ['gemini-pro', 'gemini-1.5-flash', 'gemini-1.5-pro']
                
                for model_name in model_names:
                    if success: break
                    try:
                        model = genai.GenerativeModel(model_name)
                        
                        master_prompt = f"""
                        Act as a Senior 3D Technical Director. 
                        Convert the text into a 3D storyboard table.
                        - Animation: Suggest GLB-safe methods.
                        - Format: Markdown Table.
                        - Columns: | Scene # | Visuals & Assets | Animation Logic | Labels | Narration |
                        
                        Content: {text_input}
                        """
                        
                        response = model.generate_content(master_prompt)
                        
                        if response.text:
                            st.markdown(response.text)
                            st.success(f"Generated using {model_name}")
                            success = True
                    except Exception as e:
                        continue # Try the next model if 404 occurs
                
                if not success:
                    st.error("API Connection Error: All models returned 404. Please check if your API Key is restricted to a specific region or project.")
        else:
            st.warning("Please enter source content.")

st.divider()
st.caption("© 2026 LearningPad AI Suite")
