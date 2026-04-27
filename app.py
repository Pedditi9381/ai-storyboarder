import streamlit as st
import requests
import PyPDF2
import json
import uuid
import base64
from datetime import datetime
import google.generativeai as genai

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
    proj = get_active_project()
    sb_id = st.session_state.active_storyboard
    if sb_id and "storyboards" in proj:
        return proj["storyboards"].get(sb_id)
    return None

def get_scene_assets(sc):
    return sc.get("assets", sc.get("required_assets", sc.get("models_3d", [])))

def save_scenes(scenes):
    pid = st.session_state.active_project
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
Rules: assets = 3-6 lowercase GLB names. labels = 2-5 short UI strings. animation = numbered steps separated by \\n within the string value (NOT literal newlines). narration = full proper sentences. CRITICAL: Return valid JSON only — all string values must be on one line, use \\n for line breaks inside strings, never embed raw newlines or tab characters inside JSON string values."""
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
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```", 2)[-1] if raw.count("```") >= 2 else raw
                raw = raw.lstrip("json").strip()
                if raw.endswith("```"):
                    raw = raw[:-3].strip()
            
            import re
            def fix_control_chars(s):
                result = []
                in_string = False
                escape_next = False
                for ch in s:
                    if escape_next:
                        result.append(ch)
                        escape_next = False
                        continue
                    if ch == '\\':
                        result.append(ch)
                        escape_next = True
                        continue
                    if ch == '"' and not escape_next:
                        in_string = not in_string
                        result.append(ch)
                        continue
                    if in_string:
                        if ch == '\n': result.append('\\n')
                        elif ch == '\r': result.append('\\r')
                        elif ch == '\t': result.append('\\t')
                        else: result.append(ch)
                    else: result.append(ch)
                return ''.join(result)

            raw = fix_control_chars(raw)
            scenes = json.loads(raw)
            return normalise_scenes(scenes)
        st.error(f"Groq error {resp.status_code}: {resp.text[:200]}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSON parse error: {e}")
        return None
    except Exception as e:
        st.error(f"Generation failed: {e}")
        return None

# ─── GEMINI IMAGE GENERATION ───────────────────────────────────────────────────
def generate_scene_image(sc):
    """
    Generate a storyboard frame using Gemini (Imagen 4.0).
    """
    if not GEMINI_API_KEY:
        st.error("Add GEMINI_API_KEY to Streamlit Secrets.")
        return None

    vd     = sc.get("visual_description", "")
    title  = sc.get("title", "")
    assets = ", ".join(get_scene_assets(sc))
    labels = ", ".join(sc.get("labels", []))
    narr   = sc.get("narration", "")[:200]

    prompt = (
        f"A professional 3D educational animation storyboard frame for '{title}'. "
        f"Visual setup: {vd}. Key objects: {assets}. UI context: {labels}. "
        f"Style: Clean high-fidelity instructional 3D render, dark studio space, "
        f"vivid neon blue and purple accent lighting, cinematic depth of field, "
        f"16:9 aspect ratio, high resolution, no watermarks, no text overlays."
    )

    try:
        # Initialize the Imagen 4.0 model
        model = genai.ImageGenerationModel("imagen-4.0-generate-001")
        
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="16:9",
            safety_filter_level="block_some",
            person_generation="allow_adult"
        )

        if response.images:
            img_bytes = response.images[0]._image_bytes
            return base64.b64encode(img_bytes).decode("utf-8")
        else:
            st.error("Gemini returned no images. Check safety filters.")
            return None

    except Exception as e:
        st.error(f"Gemini Generation failed: {str(e)}")
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
        new_proj_name = st.text_input("Project name", placeholder="e.g. Biology Ch3", key="new_proj_input")
        if st.button("Create Project", key="create_proj_btn"):
            if new_proj_name.strip():
                pid = str(uuid.uuid4())
                st.session_state.projects[pid] = {
                    "name": new_proj_name.strip(),
                    "created": datetime.now().strftime("%b %d, %Y"),
                    "storyboards": {}
                }
                st.session_state.active_project = pid
                st.session_state.active_storyboard = None
                st.session_state.active_tab = 0
                st.rerun()

    for pid, proj in st.session_state.projects.items():
        is_active = pid == st.session_state.active_project
        sb_count = len(proj.get("storyboards", {}))
        lbl = f"{'▸ ' if is_active else ''}{proj['name']}  [{sb_count}]"
        if st.button(lbl, key=f"proj_btn_{pid}", use_container_width=True):
            st.session_state.active_project = pid
            st.session_state.active_storyboard = None
            st.session_state.active_tab = 0
            st.rerun()

    if len(st.session_state.projects) > 1:
        st.markdown("---")
        with st.expander("🗑 Delete Active Project"):
            st.warning(f"Delete **{get_active_project().get('name','')}**?")
            if st.button("Confirm Delete", key="del_proj_confirm"):
                del st.session_state.projects[st.session_state.active_project]
                st.session_state.active_project = list(st.session_state.projects.keys())[0]
                st.session_state.active_storyboard = None
                st.session_state.active_tab = 0
                st.rerun()

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:11px;color:#334155;padding:4px 0 8px 0;">
      Groq &nbsp;<span style="color:{'#4ade80' if GROQ_API_KEY else '#f87171'};">
        {'✓ Connected' if GROQ_API_KEY else '✗ Missing key'}</span><br>
      Gemini <span style="color:{'#4ade80' if GEMINI_API_KEY else '#f87171'};">
        {'✓ Connected' if GEMINI_API_KEY else '✗ Missing key'}</span>
    </div>
    <div style="font-size:11px;color:#334155;text-align:center;">© 2026 LearningPad</div>
    """, unsafe_allow_html=True)

# ─── MAIN ──────────────────────────────────────────────────────────────────────
proj = get_active_project()
proj_name = proj.get("name", "Untitled")
storyboards = proj.get("storyboards", {})
active_sb = get_active_storyboard()
active_sb_id = st.session_state.active_storyboard

st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:0.6rem 0;border-bottom:1px solid #1e1e3a;margin-bottom:1rem;">
  <div style="display:flex;align-items:center;gap:10px;">
    <span style="font-size:14px;font-weight:600;color:#94a3b8;">{proj_name}</span>
    <span style="color:#334155;">›</span>
    <span style="font-size:14px;font-weight:700;color:#f1f5f9;">
      {active_sb["name"] if active_sb else 'Select a Storyboard'}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["📋 Storyboards", "🎬 Editor", "📦 Export / Import"])

# TAB 0 — STORYBOARD LIST
with tabs[0]:
    col_form, _ = st.columns([3, 5])
    with col_form:
        new_sb_name = st.text_input("New storyboard name", placeholder="Untitled Storyboard", key="new_sb_name")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("＋ New Storyboard", key="new_sb_btn", use_container_width=True):
                name = new_sb_name.strip() or f"Storyboard {len(storyboards)+1}"
                sbid = str(uuid.uuid4())
                st.session_state.projects[st.session_state.active_project]["storyboards"][sbid] = {
                    "name": name, "created": datetime.now().strftime("%b %d, %Y"), "scenes": []
                }
                st.session_state.active_storyboard = sbid
                st.rerun()

    st.markdown("---")
    if not storyboards:
        st.markdown('<div style="text-align:center;padding:3rem;color:#334155;">No storyboards yet.</div>', unsafe_allow_html=True)
    else:
        for sbid, sb in storyboards.items():
            is_open = sbid == active_sb_id
            ci, co, cd = st.columns([6, 1.5, 1])
            with ci:
                st.markdown(f"<div style='color:{'#93c5fd' if is_open else '#e2e8f0'};'>{sb['name']}</div>", unsafe_allow_html=True)
            with co:
                if st.button("Open →", key=f"open_{sbid}"):
                    st.session_state.active_storyboard = sbid
                    st.rerun()
            with cd:
                if st.button("🗑", key=f"del_{sbid}"):
                    del st.session_state.projects[st.session_state.active_project]["storyboards"][sbid]
                    st.rerun()

# TAB 1 — EDITOR
with tabs[1]:
    if not active_sb:
        st.info("Open a storyboard from the first tab.")
    else:
        with st.expander("⚙️ Generation Controls", expanded=not active_sb.get("scenes")):
            num_scenes = st.slider("Scenes", 3, 12, 6)
            input_type = st.radio("Source", ["Plain Text", "PDF Document"], horizontal=True)
            final_text = ""
            if input_type == "Plain Text":
                final_text = st.text_area("Paste content", key="plain_input")
            else:
                pdf_up = st.file_uploader("Upload PDF", type=["pdf"])
                if pdf_up:
                    reader = PyPDF2.PdfReader(pdf_up)
                    for pg in reader.pages: final_text += (pg.extract_text() or "")

            if st.button("🚀 Generate Scenes"):
                if final_text:
                    with st.spinner("Generating with Groq..."):
                        new_sc = generate_scenes_groq(final_text, num_scenes)
                        if new_sc:
                            save_scenes(new_sc)
                            st.rerun()

        scenes = active_sb.get("scenes", [])
        for i, sc in enumerate(scenes):
            editing = (st.session_state.editing_scene == i)
            snum = sc.get("scene_number", i + 1)
            
            h_num, h_title, h_edit, h_img = st.columns([0.1, 0.5, 0.2, 0.2])
            with h_num: st.markdown(f"**{snum:02d}**")
            with h_title: st.markdown(f"**{sc.get('title')}**")
            with h_edit: 
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state.editing_scene = None if editing else i
                    st.rerun()
            with h_img:
                if st.button("🖼", key=f"gen_img_{i}"):
                    with st.spinner("Gemini Imagen 4.0 generating..."):
                        b64 = generate_scene_image(sc)
                        if b64:
                            scenes[i]["scene_image"] = b64
                            save_scenes(scenes)
                            st.rerun()

            if not editing:
                img_col, ca, cb, cn = st.columns([1, 1, 1, 2])
                with img_col:
                    if sc.get("scene_image"):
                        st.markdown(f'<img class="scene-img" src="data:image/png;base64,{sc["scene_image"]}" />', unsafe_allow_html=True)
                    else:
                        st.caption("No image")
                with ca: st.info(f"Assets: {', '.join(get_scene_assets(sc))}")
                with cb: st.success(f"Labels: {', '.join(sc.get('labels', []))}")
                with cn: st.write(sc.get("narration"))
            else:
                with st.form(f"edit_form_{i}"):
                    new_t = st.text_input("Title", value=sc.get("title"))
                    new_n = st.text_area("Narration", value=sc.get("narration"))
                    if st.form_submit_button("Save"):
                        scenes[i]["title"] = new_t
                        scenes[i]["narration"] = new_n
                        save_scenes(scenes)
                        st.session_state.editing_scene = None
                        st.rerun()

# TAB 2 — EXPORT
with tabs[2]:
    if active_sb:
        st.download_button("📥 Download JSON", data=json.dumps(active_sb, indent=2), 
                           file_name=f"{active_sb['name']}.json")
