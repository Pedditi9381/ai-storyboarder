import streamlit as st
import google.generativeai as genai

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad | AI Storyboarder",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stTextArea textarea { font-size: 16px !important; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        background-color: #007bff; 
        color: white; 
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIGURATION ---
# Mowa, ikkada nee Gemini API Key correct ga pettu
genai.configure(api_key="AIzaSyDe7xylvvhOyjRHLFbcCydwUqMHHQAdl9w")

# --- 3. UI LAYOUT ---
st.title("🎬 LearningPad AI: 3D Storyboard Director")
st.write("Textbook content ni 3D Artist ki arthamayye **Technical Production Brief** ga marchu.")
st.write("---")

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.header("📖 Input Content")
    text_input = st.text_area(
        "Textbook Page Content Paste Chey:", 
        height=400, 
        placeholder="Example: The internal structure of Mitochondria and its energy production..."
    )
    generate_btn = st.button("Generate Technical Storyboard")

with col2:
    st.header("📋 3D Artist Brief (English)")
    
    if generate_btn:
        if text_input:
            with st.spinner("Gemini is analyzing the content for 3D production..."):
                try:
                    # UPDATED: Use stable model string 'gemini-1.5-flash'
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Technical TD Prompt for the best output
                    master_prompt = f"""
                    Act as a Senior 3D Technical Director. Convert the following textbook content into a 
                    detailed, scene-by-scene production storyboard for a 3D Artist.
                    
                    Rules:
                    1. Output MUST be in English.
                    2. Instructions must be technical (mention mesh types, animations, etc.).
                    3. Animation Logic: Must be GLB compatible (Use Bones/Skeletal animation or Shape Keys). 
                       Avoid complex particle simulations.
                    
                    Format: Provide a Markdown Table with these columns:
                    | Scene # | Visuals & 3D Assets | Animation Logic (Technical) | Labels & UI | Narration (Voiceover) |
                    
                    Content to analyze: {text_input}
                    """
                    
                    response = model.generate_content(master_prompt)
                    
                    # Final result rendering
                    st.markdown(response.text)
                    st.success("Successfully Generated! Artist can start working now.")
                    st.balloons() # Deployment success feeling kosam
                    
                except Exception as e:
                    # 404 Fix check: if it still fails, tell them to check API key status
                    st.error(f"Error: {e}")
                    st.info("Tip: API Key active ga undho ledho Google AI Studio lo check chey mowa.")
        else:
            st.warning("Mowa, mundu textbook text enter chey!")

# --- 4. FOOTER ---
st.markdown("---")
st.caption("LearningPad Internal Tool | Optimized for GLB Pipeline")
