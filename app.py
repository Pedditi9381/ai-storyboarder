import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="LearningPad Storyboarder", layout="wide")

# --- API CONFIG ---
API_KEY = "AIzaSyBxgHlVyOWCxx9itHzGY_V7E-pgjpuDxM0"
genai.configure(api_key=API_KEY)

st.title("🎬 LearningPad AI Storyboarder")
st.write("---")

text_input = st.text_area("Textbook content paste chey mowa:", height=300)

if st.button("Generate Storyboard"):
    if text_input:
        with st.spinner("AI processing..."):
            try:
                # model selection logic - 'latest' suffix fix chesi chuddam
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                prompt = f"""
                Act as a 3D Art Director. Convert this text into a scene-by-scene 
                3D storyboard table in English.
                Include: Scene #, 3D Visuals, Animation Logic (GLB safe), Labels, and Narration.
                
                Content: {text_input}
                """
                
                # Request parameters force cheyadam for safety
                response = model.generate_content(prompt)
                
                if response:
                    st.markdown(response.text)
                    st.success("Generated Successfully!")
                
            except Exception as e:
                # Okavela idi fail aythe 'gemini-1.5-flash' (no suffix) fallback
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as inner_e:
                    st.error(f"Final Error: {str(inner_e)}")
                    st.write("Mowa, logs lo 'list_models' check cheyali, leda kotha API Key try chey.")
    else:
        st.warning("Mundu text enter chey mowa!")
