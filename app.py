import streamlit as st
import requests
import PyPDF2
import json
import uuid
import base64
import google.generativeai as genai
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="LPVision Studio", layout="wide", page_icon="🎬")

# ─── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.main { background-color: #06060f; color: #e2e8f0; }
.block-container { padding: 1rem 1.5rem !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: #080814; border-right: 1px solid #1a1a35; width: 250px !important; }
section[data-testid="stSidebar"] .block-container { padding: 1rem !important; }
#MainMenu, footer, header { visibility: hidden; }

.sidebar-brand { display:flex; align-items:center; gap:10px; padding:0.5rem 0 1.5rem 0; border-bottom:1px solid #1e1e3a; margin-bottom:1rem; }
.sidebar-brand .logo { width:36px; height:36px; border-radius:8px; background:linear-gradient(135deg,#3b82f6,#8b5cf6); display:flex; align-items:center; justify-content:center; font-size:18px; font-weight:700; color:white; }
.sidebar-brand .brand-text { font-size:13px; font-weight:600; color:#94a3b8; letter-spacing:0.1em; }
.sidebar-brand .brand-name { font-size:16px; font-weight:700; color:#f1f5f9; }
.sidebar-section { font-size:10px; font-weight:600; letter-spacing:0.15em; color:#475569; text-transform:uppercase; margin:1.2rem 0 0.5rem 0; }

.stButton>button { background:#1e1e3a !important; color:#94a3b8 !important; border:1px solid #2d2d5a !important; border-radius:8px !important; font-size:13px !important; font-weight:500 !important; font-family:'Space Grotesk',sans-serif !important; transition:all 0.15s !important; }
.stButton>button:hover { background:#2d2d5a !important; color:#e2e8f0 !important; border-color:#3b4f8a !important; }

.stTextArea textarea { background:#0d0d1a !important; color:#e2e8f0 !important; border:1px solid #2d2d5a !important; border-radius:8px !important; font-family:'Space Grotesk',sans-serif !important; font-size:13px !important; }
.stTextInput input { background:#0d0d1a !important; color:#e2e8f0 !important; border:1px solid #2d2d5a !important; border-radius:8px !important; font-family:'Space Grotesk',sans-serif !important; font-size:13px !important; }
label { color:#64748b !important; font-size:12px !important; font-weight:500 !important; }

.stDownloadButton>button { background:#0f2a1e !important; color:#34d399 !important; border:1px solid #1a4a33 !important; border-radius:8px !important; }

.stTabs [data-baseweb="tab-list"] { background:transparent !important; gap:0; border-bottom:1px solid #1e1e3a; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#475569 !important; font-family:'Space Grotesk',sans-serif !important; font-size:13px !important; border-bottom:2px solid transparent !important; }
.stTabs [aria-selected="true"] { color:#f1f5f9 !important; border-bottom-color:#3b82f6 !important; }
.stTabs [data-baseweb="tab-panel"] { padding:1.25rem 0 0 0 !important; }

.streamlit-expanderHeader { background:#0d0d1a !important; color:#94a3b8 !important; border:1px solid #1e1e3a !important; border-radius:8px !important; }
[data-testid="stFileUploadDropzone"] { background:#0d0d1a !important; border:1px dashed #2d2d5a !important; border-radius:8px !important; }
.stAlert { background:#0d0d1a !important; border:1px solid #1e1e3a !important; border-radius:8px !important; color:#94a3b8 !important; }
hr { border-color:#1e1e3a !important; }
.stRadio label { color:#94a3b8 !important; }
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
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0
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
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    GEMINI_API_KEY = None

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def get_active_project():
    return st.session_state.projects.get(st.session_state.active_project, {})

def get_active_storyboard():
    proj  = get_active_project()
    sb_id = st.session_state.active_storyboard
    if sb_id and "storyboards" in proj:
        return proj["storyboards"].get(sb_id)
    return None

def get_scene_assets(sc):
    return sc.get("assets", sc.get("required_assets", sc.get("models_3d", [])))

def save_scenes(scenes):
    pid   = st.session_state.active_project
    sb_id = st.session_state.active_storyboard
    st.session_state.projects[pid]["storyboards"][sb_id]["scenes"] = scenes

def normalise_scenes(scenes):
    for sc in scenes:
        if "assets" not in sc:
            sc["assets"] = sc.pop("required_assets", sc.pop("models_3d", []))
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
    system_prompt = f"""You are a Senior 3D Instructional Animator and Technical Director.
Convert the input into EXACTLY {num_scenes} storyboard scenes.
Return ONLY a valid JSON array — no markdown, no explanation.
Each item MUST have these keys:
{{
  "scene_number": <int>,
  "title": "<3-6 word title>",
  "assets": ["<glb_model_name>", ...],
  "labels": ["<UI caption>", ...],
  "animation": "<numbered step-by-step, what moves, how, when — GLB safe>",
  "visual_description": "<2-3 sentences: camera, lighting, layout, colours>",
  "narration": "<full narrator script 2-4 sentences explaining the concept>"
}}
Rules: assets = 3-6 lowercase GLB names. labels = 2-5 short UI strings. animation = numbered steps separated by \\n inside the string. narration = full proper sentences. CRITICAL: Return valid JSON only."""
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": f"3D educational storyboard for:\n\n{text}"}
        ],
        "temperature": 0.3,
        "max_tokens": 4096
    }
    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            raw = resp.json()["choices"][0]["message"]["content"]
            raw = raw.strip().lstrip("```json").rstrip("```").strip()
            scenes = json.loads(raw)
            return normalise_scenes(scenes)
        return None
    except Exception as e:
        st.error(f"Generation failed: {e}")
        return None

# ─── GEMINI IMAGE GENERATION (IMAGEN 4.0) ──────────────────────────────────────
def generate_scene_image(sc):
    if not GEMINI_API_KEY:
        st.error("Add GEMINI_API_KEY to Streamlit Secrets.")
        return None

    vd     = sc.get("visual_description", "")
    title  = sc.get("title", "")
    assets = ", ".join(get_scene_assets(sc))
    
    prompt = (
        f"A cinematic 3D educational animation storyboard frame for '{title}'. "
        f"Visual setup: {vd}. Key 3D elements visible: {assets}. "
        f"Style: clean high-end 3D render, dark tech studio background, neon lighting accents, "
        f"16:9 widescreen, professional instructional design, no text overlays, high detail."
    )

    try:
        model = genai.ImageGenerationModel("imagen-4.0-generate-001")
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="16:9",
            safety_filter_level="block_some"
        )

        if response.images:
            img_bytes = response.images[0]._image_bytes
            return base64.b64encode(img_bytes).decode("utf-8")
        else:
            st.warning("No image generated. Check safety filters or prompt.")
            return None
    except Exception as e:
        st.error(f"Gemini Imagen Error: {e}")
        return None

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <div class="logo">LP</div>
      <div>
        <div class="brand-text">LPVISION</div>
        <div class="brand-name">Studio</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Projects</div>', unsafe_allow_html=True)
    with st.expander("＋ New Project"):
        new_proj_name = st.text_input("Project name", key="new_proj_input")
        if st.button("Create Project"):
            if new_proj_name.strip():
                pid = str(uuid.uuid4())
                st.session_state.projects[pid] = {
                    "name": new_proj_name.strip(),
                    "created": datetime.now().strftime("%b %d, %Y"),
                    "storyboards": {}
                }
                st.session_state.active_project = pid
                st.rerun()

    for pid, proj in st.session_state.projects.items():
        is_active = pid == st.session_state.active_project
        lbl = f"{'▸ ' if is_active else ''}{proj['name']}"
        if st.button(lbl, key=f"p_{pid}", use_container_width=True):
            st.session_state.active_project = pid
            st.session_state.active_storyboard = None
            st.rerun()

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:11px;color:#334155;">
      Groq <span style="color:{'#4ade80' if GROQ_API_KEY else '#f87171'};">{'✓' if GROQ_API_KEY else '✗'}</span> | 
      Gemini <span style="color:{'#4ade80' if GEMINI_API_KEY else '#f87171'};">{'✓' if GEMINI_API_KEY else '✗'}</span>
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN UI ───────────────────────────────────────────────────────────────────
proj = get_active_project()
active_sb = get_active_storyboard()
tabs = st.tabs(["📋 Storyboards", "🎬 Editor", "📦 Export"])

# TAB 0: List
with tabs[0]:
    new_sb_name = st.text_input("New storyboard name")
    if st.button("＋ Create Storyboard"):
        sbid = str(uuid.uuid4())
        proj["storyboards"][sbid] = {"name": new_sb_name or "New Storyboard", "scenes": []}
        st.session_state.active_storyboard = sbid
        st.rerun()
    
    st.markdown("---")
    for sid, sb in proj.get("storyboards", {}).items():
        c1, c2 = st.columns([4, 1])
        c1.write(sb['name'])
        if c2.button("Open", key=f"open_{sid}"):
            st.session_state.active_storyboard = sid
            st.rerun()

# TAB 1: Editor
with tabs[1]:
    if not active_sb:
        st.info("Select a storyboard first.")
    else:
        with st.expander("⚙️ Controls"):
            n_scenes = st.slider("Scenes", 3, 12, 5)
            txt_in = st.text_area("Content Source")
            if st.button("🚀 Generate"):
                new_sc = generate_scenes_groq(txt_in, n_scenes)
                if new_sc:
                    save_scenes(new_sc)
                    st.rerun()

        scenes = active_sb.get("scenes", [])
        for i, sc in enumerate(scenes):
            st.markdown(f"### Scene {i+1}: {sc['title']}")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if sc.get("scene_image"):
                    st.markdown(f'<img class="scene-img" src="data:image/png;base64,{sc["scene_image"]}" />', unsafe_allow_html=True)
                else:
                    st.info("No image.")
                
                if st.button(f"🖼 Generate Image {i}", key=f"img_btn_{i}"):
                    with st.spinner("Imagen 4.0 generating..."):
                        b64 = generate_scene_image(sc)
                        if b64:
                            scenes[i]["scene_image"] = b64
                            save_scenes(scenes)
                            st.rerun()
            
            with col2:
                st.write("**Narration:**", sc.get("narration"))
                st.write("**Animation:**", sc.get("animation"))
                st.caption(f"Assets: {', '.join(sc.get('assets', []))}")
            st.divider()

# TAB 2: Export
with tabs[2]:
    if active_sb:
        st.download_button("📥 Download JSON", data=json.dumps(active_sb, indent=2), file_name="storyboard.json")
