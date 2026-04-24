import streamlit as st
import requests
import json

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="LearningPad AI Storyboarder", layout="wide")

# API Configuration
API_KEY = "AIzaSyBzDQ-ro7rXVgX2BGaBuzC2EOZ_pt4tt1M"

def call_gemini_api(model_name, text):
    # Trying v1beta endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Act as a Senior 3D Technical Director. Convert this to a technical 3D storyboard table in English: {text}"
            }]
        }]
    }
    headers = {'Content-Type': 'application/json'}
    return requests.post(url, headers=headers, json=payload)

# --- 2. UI ---
st.title("🎬 3D Storyboard Director")
text_input = st.text_area("Paste Textbook Content:", height=300)

if st.button("GENERATE BRIEF"):
    if text_input:
        with st.spinner("Accessing Gemini AI Engine..."):
            # STEP 1: Try Gemini 1.5 Flash
            response = call_gemini_api("gemini-1.5-flash", text_input)
            
            # STEP 2: If 404/Fail, Try Gemini Pro (Standard)
            if response.status_code != 200:
                response = call_gemini_api("gemini-pro", text_input)
            
            # STEP 3: Handle Result
            if response.status_code == 200:
                result = response.json()
                try:
                    output = result['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(output)
                    st.success("Generation Successful!")
                except:
                    st.error("Format Error. Please try again.")
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
                st.info("Mowa, check if 'Generative Language API' is enabled in your Google AI Studio settings.")
    else:
        st.warning("Please enter some text first!")
