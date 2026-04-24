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
# Replace with your active Gemini 3 API Key
API_KEY = "AIzaSyBxgHlVyOWCxx9itHzGY_V7E-pgjpuDxM0"
genai.configure(api_key=API_KEY)

# --- 3. SIDEBAR / INFO ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Production Settings")
    st.info("""
    **Pipeline:** 3D Educational Animation  
    **Target Format:** GLB / Web-3D  
    **Optimization:** Low-Poly / Skeletal Animation
    """)
    st.divider()
    st.caption("Developed for LearningPad 3D Production Team")

# --- 4. MAIN INTERFACE ---
st.title("🎬 3D Storyboard Director")
st.write("Convert textbook chapters into technical 3D artist briefs instantly.")
st.divider()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📥 Source Content")
    text_input = st.text_area(
        "Paste Textbook Text or Script:", 
        height=450, 
        placeholder="e.g., Structure of the Atom, Laws of Motion, etc."
    )
    generate_btn = st.button("GENERATE PRODUCTION BRIEF")

with col2:
    st.subheader("📋 3D Technical Storyboard")
    
    if generate_btn:
        if text_input:
            with st.spinner("Analyzing content and generating technical specs..."):
                try:
                    # Invoking Gemini 3 Flash capability
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    master_prompt = f"""
                    Act as a Senior 3D Technical Director for LearningPad. 
                    Your task is to convert the provided textbook text into a technical storyboard 
                    specifically for a 3D Artist.

                    Requirements:
                    1. Tone: Professional, technical, and concise.
                    2. Animation: Suggest GLB-safe methods only (Bones, Shape Keys, UV Scrolling).
                    3. Format: Must be a clean Markdown Table.

                    Columns:
                    | Scene # | Visuals & 3D Assets | Animation Logic | Labels & UI | Narration Script |
                    
                    Textbook Content: {text_input}
                    """
                    
                    response = model.generate_content(master_prompt)
                    
                    if response.text:
                        st.markdown(response.text)
                        st.success("Brief generated successfully. Copy to production docs.")
                    else:
                        st.error("Model returned an empty response. Please check the input.")
                        
                except Exception as e:
                    st.error(f"System Error: {str(e)}")
                    st.info("Check your API Key status in Google AI Studio if this persists.")
        else:
            st.warning("Please enter source content to proceed.")

# --- 5. FOOTER ---
st.divider()
st.caption("© 2026 LearningPad AI Suite | Gemini 3 Flash Engine")
