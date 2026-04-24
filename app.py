import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="LearningPad Storyboarder", layout="wide")

# --- API CONFIG ---
# Active Gemini Key ikkada pettu
API_KEY = "AIzaSyDe7xylvvhOyjRHLFbcCydwUqMHHQAdl9w"
genai.configure(api_key=API_KEY)

# --- UI ---
st.title("🎬 LearningPad AI Storyboarder")
st.write("---")

text_input = st.text_area("Textbook content paste chey mowa:", height=300)

if st.button("Generate Storyboard"):
    if text_input:
        with st.spinner("AI processing..."):
            try:
                # TRYING GEMINI-PRO (Better stability in some regions)
                # Model name 'gemini-1.5-pro' or 'gemini-pro' try cheddam
                try:
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    st.info("Using Gemini 1.5 Pro Model")
                except:
                    model = genai.GenerativeModel('gemini-pro')
                    st.info("Using Gemini Pro Model")
                
                prompt = f"""
                Act as a 3D Art Director. Convert this text into a scene-by-scene 
                3D storyboard table in English.
                Include: Scene #, 3D Visuals, Animation Logic (GLB safe), Labels, and Narration.
                
                Content: {text_input}
                """
                
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.success("Generated!")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.write("Mowa, okavela malli 404 osthe, Google AI Studio lo 'Model' dropdown lo ఏ model work avthundo chudu.")
    else:
        st.warning("Enter some text first!")
