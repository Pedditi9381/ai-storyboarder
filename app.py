import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="LearningPad AI Storyboarder", page_icon="🎬", layout="wide")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# API Configuration
# Dashboard lo "Secrets" lo pettadam better, leda ikkada direct ga pettu (Demo kabatti)
genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")

st.title("🎬 LearningPad AI: 3D Storyboard Director")
st.write("---")

# Main Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📖 Input Content")
    text_input = st.text_area("Textbook Page Content Paste Chey:", height=400, 
                              placeholder="Example: The internal structure of a Mitochondria...")
    generate_btn = st.button("Generate Technical Brief")

with col2:
    st.header("📋 3D Artist Brief (English)")
    if generate_btn:
        if text_input:
            with st.spinner("Analyzing Technical Requirements..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Act as a Senior 3D Technical Director. Convert the following textbook content 
                    into a detailed production storyboard for a 3D Artist.
                    
                    Output Language: English.
                    Animation Logic: GLB Compatible (Bones/ShapeKeys).
                    
                    Format: Markdown Table with columns:
                    | Scene # | Visuals & Assets | Animation Logic | Labels | Narration |
                    
                    Content: {text_input}
                    """
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.success("Successfully Generated!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Mundu textbook content enter chey mowa!")

# Footer
st.markdown("---")
st.caption("LearningPad Internal AI Tool v1.0 | Developed for 3D Production Pipeline")