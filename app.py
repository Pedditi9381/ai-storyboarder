import streamlit as st
import requests
import PyPDF2
import json
import uuid
import base64
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="LPVision Studio", layout="wide", page_icon="🎬")

# ─── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] { font-family: sans-serif; }
.main { background-color: #06060f; color: #e2e8f0; }
.block-container { padding: 1rem 1.5rem !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: #080814; border-right: 1px solid #1a1a35; width: 250px !important; }
#MainMenu, footer, header { visibility: hidden; }

.scene-img { width:100%; border-radius:8px; object-fit:cover; border:1px solid #2d2d5a; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
def init_state():
    if "projects" not in st.session_state:
        did = str(uuid.uuid4())
        st.session_state.projects = {
            did: {"name": "My First Project", "created": datetime.now().strftime("%b %d, %Y"), "storyboards": {}}
        }

    if "active_project" not in st.session_state:
        st.session_state.active_project = list(st.session_state.projects.keys())[0]

    if "active_storyboard" not in st.session_state:
        st.session_state.active_storyboard = None

    if "editing_scene" not in st.session_state:
        st.session_state.editing_scene = None


init_state()

# ─── API CONFIG ────────────────────────────────────────────────────────────────
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = None

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = None

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def get_active_project():
    return st.session_state.projects.get(st.session_state.active_project, {})


def get_active_storyboard():
    proj = get_active_project()
    sb_id = st.session_state.active_storyboard
    if sb_id and "storyboards" in proj:
        return proj["storyboards"].get(sb_id)
    return None


def save_scenes(scenes):
    pid = st.session_state.active_project
    sb_id = st.session_state.active_storyboard
    st.session_state.projects[pid]["storyboards"][sb_id]["scenes"] = scenes


def normalise_scenes(scenes):
    for sc in scenes:
        if "assets" not in sc:
            sc["assets"] = []
        if "labels" not in sc:
            sc["labels"] = []
        if "scene_image" not in sc:
            sc["scene_image"] = None
    return scenes


# ─── GROQ SCENE GENERATION ─────────────────────────────────────────────────────
def generate_scenes_groq(text, num_scenes):
    if not GROQ_API_KEY:
        st.error("Add GROQ_API_KEY to Streamlit Secrets.")
        return None

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    system_prompt = f"""
Convert the input text into EXACTLY {num_scenes} storyboard scenes.

Return ONLY a JSON array.

Each scene must contain:

scene_number
title
assets
labels
animation
visual_description
narration
"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.3,
        "max_tokens": 4096
    }

    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)

        if resp.status_code == 200:
            raw = resp.json()["choices"][0]["message"]["content"]
            scenes = json.loads(raw)
            return normalise_scenes(scenes)

        st.error(resp.text)
        return None

    except Exception as e:
        st.error(f"Generation failed: {e}")
        return None


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:

    st.title("LPVision Studio")

    st.subheader("Projects")

    for pid, proj in st.session_state.projects.items():

        if st.button(proj["name"], key=pid):
            st.session_state.active_project = pid
            st.session_state.active_storyboard = None
            st.rerun()

    st.markdown("---")

    st.caption("API Status")

    st.write("Groq:", "✅" if GROQ_API_KEY else "❌")
    st.write("Gemini:", "✅" if GEMINI_API_KEY else "❌")


# ─── MAIN ──────────────────────────────────────────────────────────────────────
proj = get_active_project()
proj_name = proj.get("name", "Untitled")
storyboards = proj.get("storyboards", {})

st.title(proj_name)

# ─── CREATE STORYBOARD ─────────────────────────────────────────────────────────
st.subheader("Create Storyboard")

sb_name = st.text_input("Storyboard name")

if st.button("Create"):

    sbid = str(uuid.uuid4())

    st.session_state.projects[st.session_state.active_project]["storyboards"][sbid] = {
        "name": sb_name,
        "created": datetime.now().strftime("%b %d, %Y"),
        "scenes": []
    }

    st.session_state.active_storyboard = sbid
    st.rerun()


# ─── SELECT STORYBOARD ─────────────────────────────────────────────────────────
active_sb = get_active_storyboard()

if active_sb:

    st.header(active_sb["name"])

    num_scenes = st.slider("Scenes", 3, 12, 6)

    text = st.text_area("Input text")

    if st.button("Generate Scenes"):

        with st.spinner("Generating scenes..."):

            scenes = generate_scenes_groq(text, num_scenes)

            if scenes:
                save_scenes(scenes)
                st.success("Scenes generated")


    scenes = active_sb.get("scenes", [])

    for i, sc in enumerate(scenes):

        st.markdown("---")

        st.subheader(f"Scene {sc.get('scene_number', i+1)}")

        st.write("Title:", sc.get("title"))

        st.write("Assets:", ", ".join(sc.get("assets", [])))

        st.write("Labels:", ", ".join(sc.get("labels", [])))

        st.write("Narration:", sc.get("narration"))

        st.write("Visual:", sc.get("visual_description"))

        st.write("Animation:", sc.get("animation"))

        if sc.get("scene_image"):
            st.image(base64.b64decode(sc["scene_image"]))

# ─── EXPORT ────────────────────────────────────────────────────────────────────
if active_sb:

    st.markdown("---")

    export_payload = {
        "name": active_sb["name"],
        "created": active_sb["created"],
        "scenes": active_sb.get("scenes", [])
    }

    st.download_button(
        "Download Storyboard JSON",
        data=json.dumps(export_payload, indent=2),
        file_name="storyboard.json",
        mime="application/json"
    )
