import streamlit as st
import requests
import PyPDF2

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="LearningPad | 3D Storyboard Pro", layout="wide")

# Studio Styling
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.5em; 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white; font-weight: 700; border: none;
    }
    .stTextArea textarea { background-color: #1e293b; color: #f1f5f9; border-radius: 12px; }
    th { background-color: #3b82f6 !important; color: white !important; }
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
st.title("🎬 3D Scene Director & Asset Planner")
st.write("---")

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📥 Source Material")
    input_type = st.radio("Input Mode:", ["Text Snippet", "PDF Document"])
    
    final_text = ""
    if input_type == "Text Snippet":
        final_text = st.text_area("Paste Content:", height=300, placeholder="e.g., Structure of the solar system...")
    else:
        uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_pdf:
            pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
            for page in pdf_reader.pages:
                final_text += page.extract_text()
            st.success("PDF Content Loaded!")

    generate_btn = st.button("🚀 GENERATE 6-SCENE PRODUCTION BRIEF")

with col2:
    st.subheader("📋 Production Storyboard")
    
    if generate_btn and final_text:
        with st.spinner("LPU Engine is designing your 3D pipeline..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Prompting for exactly 6 scenes + technical details
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system", 
                        "content": (
                            "You are a Senior 3D Technical Director. "
                            "Convert input into exactly 6 production scenes. "
                            "Output a Markdown table with these columns: "
                            "Scene # | Required 3D Assets | Labels (UI Text) | Animation Logic (GLB Safe) | Visual Description | Narration. "
                            "Also, after the table, provide a 'Visual Keywords' list for each scene to fetch reference images."
                        )
                    },
                    {
                        "role": "user", 
                        "content": f"Analyze this content for a 3D video: {final_text}"
                    }
                ],
                "temperature": 0.2
            }
            
            try:
                response = requests.post(GROQ_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    output = response.json()['choices'][0]['message']['content']
                    st.markdown(output)
                    
                    # --- IMAGE REFERENCE LOGIC ---
                    st.write("---")
                    st.subheader("🖼️ Visual Reference Gallery")
                    # Simple automated keyword search display (Placeholder logic)
                    search_query = final_text[:30].split()[0] if final_text else "3D Art"
                    img_url = f"https://source.unsplash.com/featured/800x450?{search_query}"
                    st.image(img_url, caption=f"Reference Inspiration for: {search_query}")
                    
                    st.success("Full Production Brief Generated!")
                    st.balloons()
                else:
                    st.error("API Connection Error.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()
st.caption("© 2026 LearningPad | Professional 3D Pipeline Tool")
