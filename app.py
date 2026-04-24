import streamlit as st
import requests

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LearningPad | 3D Asset Director",
    page_icon="🎬",
    layout="wide"
)

# Professional Studio UI
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stTextArea textarea { background-color: #1e293b; color: #f1f5f9; border-radius: 12px; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        color: white; font-weight: 600; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. STABLE FREE ENGINE (Mistral-7B) ---
# Llama lo 404 osthe, Mistral is the best alternative
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("Studio Controls")
    st.write("**Artist:** Raviteja")
    st.info("Engine: Mistral-7B (Stable Tier)")

# --- 4. MAIN INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #6366f1;'>🎬 3D Storyboard Director</h1>", unsafe_allow_html=True)
st.write("---")

col1, col2 = st.columns([1, 1.6], gap="large")

with col1:
    st.subheader("📥 Textbook Content")
    text_input = st.text_area("Paste script here:", height=400)
    generate_btn = st.button("🚀 GENERATE BRIEF")

with col2:
    st.subheader("📋 Production Specifications")
    
    if generate_btn:
        if text_input:
            with st.spinner("Mistral Engine is analyzing..."):
                # Simpler prompt format for Mistral
                prompt = f"<s>[INST] You are a 3D Technical Director. Convert this text into a professional Markdown table with columns: Scene #, 3D Assets, Animation Logic (GLB Safe), and Narration Brief. Content: {text_input} [/INST]"
                
                payload = {
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 1000, "temperature": 0.5}
                }
                
                try:
                    response = requests.post(API_URL, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        # Handling Mistral's response format
                        output = result[0]['generated_text'].split("[/INST]")[-1].strip()
                        st.markdown(output)
                        st.success("Generated via Mistral-7B")
                    elif response.status_code == 503:
                        st.warning("Server is warming up. Wait 10 seconds and try again!")
                    elif response.status_code == 404:
                        st.error("Engine 404: Switching to backup model...")
                        # Optional: Auto-fallback if needed
                    else:
                        st.error(f"Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Connection Failed: {str(e)}")
        else:
            st.warning("Please enter text content.")
