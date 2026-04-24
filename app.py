import streamlit as st
import requests

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad | Free AI Director",
    page_icon="🎬",
    layout="wide"
)

# Professional UI Styling
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; color: #1e1e1e; }
    .stTextArea textarea { border-radius: 12px; border: 2px solid #dfe1e5; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.8em; 
        background-color: #6366f1; color: white; font-weight: 700; border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover { background-color: #4f46e5; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FREE API CONFIGURATION (Hugging Face) ---
# Using Meta's Llama 3 via Hugging Face Public Inference
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

# --- 3. MAIN INTERFACE ---
st.title("🎬 3D Storyboard Director")
st.markdown("##### Professional 3D Workflow Automation (Free Tier)")
st.write("---")

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📥 Textbook Content")
    text_input = st.text_area("Paste Content Here:", height=400, placeholder="e.g., Structure of a Plant Cell...")
    generate_btn = st.button("🚀 GENERATE STORYBOARD (FREE)")

with col2:
    st.subheader("📋 Production Ready Brief")
    
    if generate_btn:
        if text_input:
            with st.spinner("AI is thinking (Free Server)..."):
                # System Prompt for 3D logic
                prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
                You are a 3D Production Expert. Convert the input into a Markdown table.
                Columns: Scene #, 3D Assets, Animation Logic (GLB Safe), Labels, Narration Script.<|eot_id|>
                <|start_header_id|>user<|end_header_id|>
                Content: {text_input}<|eot_id|>
                <|start_header_id|>assistant<|end_header_id|>"""
                
                payload = {
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 1000, "temperature": 0.5}
                }
                
                try:
                    # Requesting the public API
                    response = requests.post(API_URL, json=payload)
                    result = response.json()
                    
                    if response.status_code == 200:
                        # Extracting the text from Llama-3 format
                        full_text = result[0]['generated_text']
                        # Getting only the assistant's part
                        output = full_text.split("<|assistant|>")[-1].strip()
                        st.markdown(output)
                        st.success("Generated using Free Llama-3 Engine")
                        st.balloons()
                    else:
                        st.error("Server Busy. Please wait 10 seconds and try again.")
                        st.info("Since this is a free server, it might take a moment to wake up.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter text content.")

st.divider()
st.caption("© 2026 LearningPad | Open Source 3D Tools")
