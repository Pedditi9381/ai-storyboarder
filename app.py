import streamlit as st
import requests
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad | 3D Asset Director",
    page_icon="🎬",
    layout="wide"
)

# Professional Studio UI (Modern Dark/Blue Theme)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    
    .main { background-color: #0f172a; color: #f8fafc; }
    
    .stTextArea textarea { 
        background-color: #1e293b; 
        color: #f1f5f9; 
        border: 1px solid #334155;
        border-radius: 12px;
        font-size: 16px;
    }
    
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white; 
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        transition: 0.3s;
    }
    
    .stButton>button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
    }
    
    .status-card {
        padding: 1.5rem;
        background-color: #1e293b;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FREE ENGINE CONFIGURATION ---
# Using Meta's Llama-3-8B (Public Inference - No Key Required for basic hits)
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/3d-model.png", width=80)
    st.title("Studio Controls")
    st.markdown("---")
    st.write("**Artist:** Raviteja")
    st.write("**Role:** 3D Generalist")
    st.write("**Pipeline:** Blender to GLB")
    st.divider()
    st.info("Engine: Llama-3 (Free Tier)")

# --- 4. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🎬 3D Storyboard Director</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Automated 3D Production Briefs for LearningPad Content</p>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 1.6], gap="large")

with col1:
    st.subheader("📥 Textbook Content")
    text_input = st.text_area(
        "Paste the chapter content or script below:", 
        height=400, 
        placeholder="Example: The structure of a human heart consists of four chambers..."
    )
    generate_btn = st.button("🚀 GENERATE PRODUCTION BRIEF")

with col2:
    st.subheader("📋 Production Specifications")
    
    if generate_btn:
        if text_input:
            with st.spinner("AI Director is analyzing assets and animation logic..."):
                # System Prompt to force the AI to act as a 3D Director
                prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
                You are a Senior 3D Technical Director for a production studio. 
                Task: Convert the user's input into a professional Markdown table. 
                Columns: Scene # | 3D Assets (Models needed) | Animation Logic (GLB/Web Safe) | Narration Brief.
                Guidelines: Suggest optimized geometry and simple bone/shape-key animations only. Use English.<|eot_id|>
                <|start_header_id|>user<|end_header_id|>
                Script: {text_input}<|eot_id|>
                <|start_header_id|>assistant<|end_header_id|>"""
                
                payload = {
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 800, "temperature": 0.4}
                }
                
                try:
                    # Direct API Call
                    response = requests.post(API_URL, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        # Extracting the assistant response
                        raw_output = result[0]['generated_text']
                        final_output = raw_output.split("<|assistant|>")[-1].strip()
                        
                        st.markdown(final_output)
                        st.success("Analysis Complete!")
                        st.balloons()
                    elif response.status_code == 503:
                        st.error("Model is currently loading on the server. Please wait 20 seconds and click again.")
                    else:
                        st.error(f"Engine Error: {response.status_code}")
                except Exception as e:
                    st.error("Server Timeout. Please try again.")
        else:
            st.warning("Please enter some text content to start.")

# --- 5. FOOTER ---
st.write("---")
st.caption("© 2026 LearningPad | Professional 3D Pipeline Tool | Optimized for GLB Workflow")
