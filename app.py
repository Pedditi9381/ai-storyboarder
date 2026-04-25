import streamlit as st
import requests
import PyPDF2
import json
import uuid
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="LPVision Studio", layout="wide", page_icon="🎬")

# ─── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* Reset & Base */
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.main { background-color: #09090f; color: #e2e8f0; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { background: #0d0d1a; border-right: 1px solid #1e1e3a; width: 260px !important; }
section[data-testid="stSidebar"] .block-container { padding: 1rem !important; }

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar branding */
.sidebar-brand {
    display: flex; align-items: center; gap: 10px;
    padding: 0.5rem 0 1.5rem 0; border-bottom: 1px solid #1e1e3a; margin-bottom: 1rem;
}
.sidebar-brand .logo {
    width: 36px; height: 36px; border-radius: 8px;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 700;
}
.sidebar-brand .brand-text { font-size: 14px; font-weight: 600; color: #94a3b8; letter-spacing: 0.1em; }
.sidebar-brand .brand-name { font-size: 16px; font-weight: 700; color: #f1f5f9; }

/* Sidebar section labels */
.sidebar-section {
    font-size: 10px; font-weight: 600; letter-spacing: 0.15em;
    color: #475569; text-transform: uppercase; margin: 1.2rem 0 0.5rem 0;
}

/* Project cards in sidebar */
.project-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.55rem 0.75rem; border-radius: 8px; cursor: pointer;
    margin-bottom: 3px; border: 1px solid transparent; transition: all 0.15s;
}
.project-item:hover { background: #1e1e3a; border-color: #2d2d5a; }
.project-item.active { background: #1e2a4a; border-color: #3b82f6; }
.project-item .proj-name { font-size: 13px; font-weight: 500; color: #cbd5e1; flex: 1; }
.project-item.active .proj-name { color: #93c5fd; }
.project-item .proj-count { font-size: 11px; color: #475569; background: #1e1e3a; padding: 2px 6px; border-radius: 4px; }

/* Top bar */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.85rem 2rem; border-bottom: 1px solid #1e1e3a;
    background: #09090f; position: sticky; top: 0; z-index: 100;
}
.topbar-left { display: flex; align-items: center; gap: 1rem; }
.topbar-title { font-size: 15px; font-weight: 600; color: #94a3b8; }
.topbar-story { font-size: 15px; font-weight: 700; color: #f1f5f9; }
.topbar-right { display: flex; align-items: center; gap: 0.75rem; }

/* Tab nav */
.tab-nav {
    display: flex; gap: 1px; border-bottom: 1px solid #1e1e3a;
    padding: 0 2rem; background: #09090f;
}
.tab-btn {
    padding: 0.75rem 1.25rem; font-size: 13px; font-weight: 500;
    color: #475569; cursor: pointer; border-bottom: 2px solid transparent;
    transition: all 0.15s; user-select: none;
}
.tab-btn:hover { color: #94a3b8; }
.tab-btn.active { color: #f1f5f9; border-bottom-color: #3b82f6; }

/* Main content area */
.content-area { padding: 1.5rem 2rem; }

/* Two-panel layout */
.panel-row { display: flex; gap: 1.5rem; }
.panel-left { flex: 0 0 420px; }
.panel-right { flex: 1; min-width: 0; }

/* Cards */
.card {
    background: #111120; border: 1px solid #1e1e3a;
    border-radius: 12px; padding: 1.25rem;
}
.card-title {
    font-size: 11px; font-weight: 600; letter-spacing: 0.12em;
    color: #475569; text-transform: uppercase; margin-bottom: 1rem;
}

/* Scene list items */
.scene-item {
    padding: 0.75rem; border-radius: 8px; border: 1px solid #1e1e3a;
    margin-bottom: 0.5rem; cursor: pointer; transition: all 0.15s;
}
.scene-item:hover { border-color: #2d2d5a; background: #13132a; }
.scene-title { font-size: 13px; font-weight: 600; color: #e2e8f0; margin-bottom: 4px; }
.scene-narration { font-size: 12px; color: #64748b; font-style: italic; }
.scene-tags { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
.scene-tag {
    font-size: 10px; font-weight: 500; padding: 2px 7px; border-radius: 4px;
    background: #1e2a4a; color: #60a5fa; font-family: 'JetBrains Mono', monospace;
}

/* Frame grid */
.frame-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem; }
.frame-card {
    background: #111120; border: 1px solid #1e1e3a; border-radius: 12px; overflow: hidden;
}
.frame-label {
    font-size: 10px; font-weight: 700; letter-spacing: 0.12em; color: #475569;
    padding: 0.6rem 0.9rem; border-bottom: 1px solid #1e1e3a;
    font-family: 'JetBrains Mono', monospace;
}
.frame-placeholder {
    height: 160px; display: flex; align-items: center; justify-content: center;
    background: #0d0d1a; color: #2d2d5a; flex-direction: column; gap: 8px;
}
.frame-placeholder svg { opacity: 0.4; }
.frame-placeholder-text { font-size: 11px; color: #334155; }
.frame-info { padding: 0.75rem 0.9rem; }
.frame-scene-title { font-size: 12px; font-weight: 700; color: #e2e8f0; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
.frame-narration { font-size: 11px; color: #64748b; font-style: italic; margin-bottom: 8px; }
.frame-tags { display: flex; gap: 4px; flex-wrap: wrap; }

/* Toolbar */
.toolbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.9rem 2rem; border-bottom: 1px solid #1e1e3a; background: #0d0d1a;
}
.toolbar-left { display: flex; align-items: center; gap: 0.75rem; }
.toolbar-right { font-size: 12px; color: #475569; font-family: 'JetBrains Mono', monospace; }

/* Buttons */
.stButton>button {
    background: #1e1e3a !important; color: #94a3b8 !important;
    border: 1px solid #2d2d5a !important; border-radius: 8px !important;
    font-size: 13px !important; font-weight: 500 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    transition: all 0.15s !important;
}
.stButton>button:hover {
    background: #2d2d5a !important; color: #e2e8f0 !important;
    border-color: #3b4f8a !important;
}

/* Primary button */
.primary-btn>button {
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
    color: white !important; border: none !important;
}
.primary-btn>button:hover { opacity: 0.9 !important; }

/* Danger button */
.danger-btn>button {
    background: #2d1515 !important; color: #f87171 !important;
    border-color: #4a1a1a !important;
}

/* Download button */
.stDownloadButton>button {
    background: #0f2a1e !important; color: #34d399 !important;
    border: 1px solid #1a4a33 !important; border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Input fields */
.stTextArea textarea {
    background: #0d0d1a !important; color: #e2e8f0 !important;
    border: 1px solid #1e1e3a !important; border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important; font-size: 13px !important;
}
.stTextInput input {
    background: #0d0d1a !important; color: #e2e8f0 !important;
    border: 1px solid #1e1e3a !important; border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important; font-size: 13px !important;
}
.stSelectbox select {
    background: #0d0d1a !important; color: #e2e8f0 !important;
}
label { color: #64748b !important; font-size: 12px !important; font-weight: 500 !important; }

/* Slider */
.stSlider [data-baseweb="slider"] { color: #3b82f6; }

/* Radio */
.stRadio label { color: #94a3b8 !important; }
.stRadio [data-testid="stMarkdownContainer"] p { color: #94a3b8 !important; }

/* Expander */
.streamlit-expanderHeader { background: #0d0d1a !important; color: #94a3b8 !important; border: 1px solid #1e1e3a !important; border-radius: 8px !important; }

/* File uploader */
[data-testid="stFileUploadDropzone"] { background: #0d0d1a !important; border: 1px dashed #2d2d5a !important; border-radius: 8px !important; }

/* Divider */
hr { border-color: #1e1e3a !important; }

/* Alert / info */
.stAlert { background: #0d0d1a !important; border: 1px solid #1e1e3a !important; border-radius: 8px !important; color: #94a3b8 !important; }

/* Tabs fix */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 0; border-bottom: 1px solid #1e1e3a; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #475569 !important; font-family: 'Space Grotesk', sans-serif !important; font-size: 13px !important; border-bottom: 2px solid transparent !important; }
.stTabs [aria-selected="true"] { color: #f1f5f9 !important; border-bottom-color: #3b82f6 !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 0 0 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
def init_state():
    if "projects" not in st.session_state:
        default_id = str(uuid.uuid4())
        st.session_state.projects = {
            default_id: {
                "name": "My First Project",
                "created": datetime.now().strftime("%b %d, %Y"),
                "storyboards": {}
            }
        }
    if "active_project" not in st.session_state:
        st.session_state.active_project = list(st.session_state.projects.keys())[0]
    if "active_storyboard" not in st.session_state:
        st.session_state.active_storyboard = None
    if "main_view" not in st.session_state:
        st.session_state.main_view = "projects"  # "projects" | "storyboard"

init_state()

# ─── API CONFIG ────────────────────────────────────────────────────────────────
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = None

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
    """
    Unified helper to read assets from a scene dict.
    Priority: 'assets' > 'required_assets' > 'models_3d'
    Always returns a list.
    """
    return sc.get("assets", sc.get("required_assets", sc.get("models_3d", [])))

def generate_scenes_groq(text, num_scenes):
    if not GROQ_API_KEY:
        st.error("⚠️ Add `GROQ_API_KEY` to Streamlit Secrets to enable generation.")
        return None
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are a Senior 3D Technical Director. "
                    f"Convert input into EXACTLY {num_scenes} scenes. "
                    "Return ONLY a valid JSON array (no markdown, no explanation). "
                    "Each item: {\"scene_number\": int, \"title\": str, \"narration\": str, "
                    "\"context\": str, \"assets\": [str], \"animation\": str, \"visual_description\": str}"
                )
            },
            {"role": "user", "content": f"Create a detailed 3D storyboard for: {text}"}
        ],
        "temperature": 0.2
    }
    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            raw = resp.json()["choices"][0]["message"]["content"]
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            scenes = json.loads(raw)
            # Normalise: ensure every scene uses 'assets' key
            for sc in scenes:
                if "assets" not in sc:
                    sc["assets"] = sc.pop("required_assets", sc.pop("models_3d", []))
            return scenes
        else:
            st.error(f"Groq API error {resp.status_code}")
            return None
    except Exception as e:
        st.error(f"Generation failed: {e}")
        return None

def normalise_scenes(scenes):
    """
    Migrate imported / legacy scenes so every scene has an 'assets' key.
    """
    for sc in scenes:
        if "assets" not in sc:
            sc["assets"] = sc.pop("required_assets", sc.pop("models_3d", []))
    return scenes

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="sidebar-brand">
        <div class="logo">LP</div>
        <div>
            <div class="brand-text">LPVISION</div>
            <div class="brand-name">Studio</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # New Project
    st.markdown('<div class="sidebar-section">Projects</div>', unsafe_allow_html=True)
    with st.expander("＋ New Project"):
        new_proj_name = st.text_input("Project name", placeholder="e.g. Biology Chapter 3", key="new_proj_input")
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
                st.session_state.main_view = "projects"
                st.rerun()

    # Project list
    for pid, proj in st.session_state.projects.items():
        is_active = pid == st.session_state.active_project
        sb_count = len(proj.get("storyboards", {}))
        active_class = "active" if is_active else ""
        if st.button(
            f"{'▸ ' if is_active else ''}{proj['name']}  [{sb_count}]",
            key=f"proj_btn_{pid}",
            use_container_width=True
        ):
            st.session_state.active_project = pid
            st.session_state.active_storyboard = None
            st.session_state.main_view = "projects"
            st.rerun()

    # Delete project
    if len(st.session_state.projects) > 1:
        st.markdown("---")
        with st.expander("🗑 Delete Active Project"):
            st.warning(f"Delete **{get_active_project().get('name', '')}**? This cannot be undone.")
            if st.button("Confirm Delete Project", key="del_proj_confirm"):
                del st.session_state.projects[st.session_state.active_project]
                st.session_state.active_project = list(st.session_state.projects.keys())[0]
                st.session_state.active_storyboard = None
                st.session_state.main_view = "projects"
                st.rerun()

    st.markdown("---")
    st.markdown('<div style="font-size:11px; color:#334155; text-align:center;">© 2026 LearningPad</div>', unsafe_allow_html=True)

# ─── MAIN AREA ─────────────────────────────────────────────────────────────────
proj = get_active_project()
proj_name = proj.get("name", "Untitled Project")
storyboards = proj.get("storyboards", {})
active_sb = get_active_storyboard()
active_sb_id = st.session_state.active_storyboard

# ── TOP BAR
sb_title = active_sb["name"] if active_sb else "—"
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        <span class="topbar-title">{proj_name}</span>
        <span style="color:#334155;">›</span>
        <span class="topbar-story">{sb_title if active_sb else 'Select a Storyboard'}</span>
    </div>
    <div class="topbar-right" style="font-size:12px; color:#475569;">
        {len(storyboards)} storyboard{'s' if len(storyboards)!=1 else ''}
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABS
tabs = st.tabs(["📋 Storyboards", "🎬 Editor", "📦 Export / Import"])

# ════════════════════════════════════════════════════════════
# TAB 1 — STORYBOARD LIST
# ════════════════════════════════════════════════════════════
with tabs[0]:
    col_actions, col_spacer = st.columns([3, 5])
    with col_actions:
        new_sb_name = st.text_input("New storyboard name", placeholder="Untitled Storyboard", key="new_sb_name")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("＋ New Storyboard", key="new_sb_btn", use_container_width=True):
                name = new_sb_name.strip() or f"Storyboard {len(storyboards)+1}"
                sbid = str(uuid.uuid4())
                st.session_state.projects[st.session_state.active_project]["storyboards"][sbid] = {
                    "name": name,
                    "created": datetime.now().strftime("%b %d, %Y"),
                    "scenes": []
                }
                st.session_state.active_storyboard = sbid
                st.rerun()
        with c2:
            # Import JSON storyboard
            import_file = st.file_uploader("Import JSON", type=["json"], key="import_sb", label_visibility="collapsed")
            if import_file:
                try:
                    imported = json.load(import_file)
                    sbid = str(uuid.uuid4())
                    # Accept either a storyboard dict or raw scenes list
                    if isinstance(imported, list):
                        imported_scenes = normalise_scenes(imported)
                        st.session_state.projects[st.session_state.active_project]["storyboards"][sbid] = {
                            "name": import_file.name.replace(".json", ""),
                            "created": datetime.now().strftime("%b %d, %Y"),
                            "scenes": imported_scenes
                        }
                    elif isinstance(imported, dict) and "scenes" in imported:
                        imported_scenes = normalise_scenes(imported["scenes"])
                        st.session_state.projects[st.session_state.active_project]["storyboards"][sbid] = {
                            "name": imported.get("name", import_file.name.replace(".json", "")),
                            "created": datetime.now().strftime("%b %d, %Y"),
                            "scenes": imported_scenes
                        }
                    st.session_state.active_storyboard = sbid
                    st.success("Storyboard imported!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {e}")

    st.markdown("---")
    if not storyboards:
        st.markdown('<div style="text-align:center; padding:3rem; color:#334155;">No storyboards yet. Create one above.</div>', unsafe_allow_html=True)
    else:
        for sbid, sb in storyboards.items():
            n_scenes = len(sb.get("scenes", []))
            is_open = sbid == active_sb_id
            col_info, col_open, col_del = st.columns([6, 1.5, 1])
            with col_info:
                st.markdown(f"""
                <div style="padding: 0.6rem 0;">
                    <div style="font-size:14px; font-weight:600; color:{'#93c5fd' if is_open else '#e2e8f0'};">
                        {'▸ ' if is_open else ''}{sb['name']}
                    </div>
                    <div style="font-size:12px; color:#475569;">{sb.get('created','')} · {n_scenes} scene{'s' if n_scenes!=1 else ''}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_open:
                if st.button("Open", key=f"open_{sbid}", use_container_width=True):
                    st.session_state.active_storyboard = sbid
                    st.rerun()
            with col_del:
                if st.button("🗑", key=f"del_{sbid}", use_container_width=True):
                    del st.session_state.projects[st.session_state.active_project]["storyboards"][sbid]
                    if active_sb_id == sbid:
                        st.session_state.active_storyboard = None
                    st.rerun()
            st.markdown('<hr style="margin:0; border-color:#1e1e3a;">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — EDITOR
# ════════════════════════════════════════════════════════════
with tabs[1]:
    if not active_sb:
        st.info("Open or create a storyboard from the **Storyboards** tab to start editing.")
    else:
        left, right = st.columns([1, 1.8], gap="large")

        with left:
            st.markdown('<div class="card-title">Input & Controls</div>', unsafe_allow_html=True)
            num_scenes = st.slider("Number of Scenes", min_value=3, max_value=12, value=6, key="num_scenes_slider")
            input_type = st.radio("Input Source", ["Plain Text", "PDF Document"], horizontal=True, key="input_type_radio")

            final_text = ""
            if input_type == "Plain Text":
                final_text = st.text_area(
                    "Paste content here",
                    height=220,
                    placeholder="e.g., Working of a Steam Engine, steps of photosynthesis...",
                    key="plain_text_input"
                )
                st.markdown(f'<div style="font-size:11px; color:#475569; text-align:right;">{len(final_text)} chars</div>', unsafe_allow_html=True)
            else:
                uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_uploader")
                if uploaded_pdf:
                    pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
                    for page in pdf_reader.pages:
                        final_text += (page.extract_text() or "")
                    st.success(f"PDF extracted · {len(final_text)} chars")

            st.markdown("---")
            gen_col, clear_col = st.columns(2)
            with gen_col:
                generate_btn = st.button(f"🚀 Generate {num_scenes} Scenes", key="gen_btn", use_container_width=True)
            with clear_col:
                clear_btn = st.button("✕ Clear Scenes", key="clear_btn", use_container_width=True)

            if clear_btn and active_sb_id:
                st.session_state.projects[st.session_state.active_project]["storyboards"][active_sb_id]["scenes"] = []
                st.rerun()

            if generate_btn and final_text:
                with st.spinner(f"Generating {num_scenes} scenes with Groq..."):
                    scenes = generate_scenes_groq(final_text, num_scenes)
                    if scenes:
                        st.session_state.projects[st.session_state.active_project]["storyboards"][active_sb_id]["scenes"] = scenes
                        st.success(f"✓ {len(scenes)} scenes generated!")
                        st.rerun()
            elif generate_btn and not final_text:
                st.warning("Add some content first.")

            # Scene list (editable)
            scenes = active_sb.get("scenes", [])
            if scenes:
                st.markdown("---")
                st.markdown('<div class="card-title">Scene List</div>', unsafe_allow_html=True)
                for i, sc in enumerate(scenes):
                    with st.expander(f"Scene {sc.get('scene_number', i+1)}: {sc.get('title', 'Untitled')}"):
                        st.markdown(f'<div class="scene-narration">🎙 {sc.get("narration","")}</div>', unsafe_allow_html=True)
                        assets = get_scene_assets(sc)
                        if assets:
                            tags_html = " ".join([f'<span class="scene-tag">{a}</span>' for a in assets])
                            st.markdown(f'<div style="margin-top:4px; font-size:10px; color:#475569; font-weight:600; text-transform:uppercase; letter-spacing:0.1em;">Assets</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="scene-tags">{tags_html}</div>', unsafe_allow_html=True)
                        st.caption(f"Animation: {sc.get('animation','—')}")
                        # Delete individual scene
                        if st.button(f"Delete Scene {i+1}", key=f"del_scene_{i}"):
                            st.session_state.projects[st.session_state.active_project]["storyboards"][active_sb_id]["scenes"].pop(i)
                            st.rerun()

        with right:
            scenes = active_sb.get("scenes", [])
            # Toolbar
            render_count = 0  # placeholder; real rendering would call image API
            st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
                <div style="font-size:13px; font-weight:600; color:#64748b; letter-spacing:0.08em; text-transform:uppercase;">Storyboard — {active_sb['name']}</div>
                <div style="font-size:12px; color:#475569; font-family:'JetBrains Mono',monospace;">
                    {len(scenes)} Scenes · {render_count} Rendered
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not scenes:
                st.markdown("""
                <div style="text-align:center; padding:4rem; color:#334155; border:1px dashed #1e1e3a; border-radius:12px;">
                    <div style="font-size:2rem;">🎞</div>
                    <div style="margin-top:0.5rem; font-size:14px;">No scenes yet. Generate or import to begin.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Frame grid — 3 per row
                rows = [scenes[i:i+3] for i in range(0, len(scenes), 3)]
                for row in rows:
                    cols = st.columns(3)
                    for col, sc in zip(cols, row):
                        with col:
                            assets = get_scene_assets(sc)
                            tags_html = " ".join([f'<span class="scene-tag">{a}</span>' for a in assets[:3]])
                            st.markdown(f"""
                            <div class="frame-card">
                                <div class="frame-label">FRAME {sc.get('scene_number', '?'):02d}</div>
                                <div class="frame-placeholder">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                        <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
                                        <path d="M21 15l-5-5L5 21"/>
                                    </svg>
                                    <span class="frame-placeholder-text">NO FRAME YET</span>
                                </div>
                                <div class="frame-info">
                                    <div class="frame-scene-title">{sc.get('title','Untitled')}</div>
                                    <div class="frame-narration">"{sc.get('narration','')[:70]}{'...' if len(sc.get('narration',''))>70 else ''}"</div>
                                    <div class="frame-tags">{tags_html}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 3 — EXPORT / IMPORT
# ════════════════════════════════════════════════════════════
with tabs[2]:
    if not active_sb:
        st.info("Open a storyboard first to export it.")
    else:
        scenes = active_sb.get("scenes", [])
        col_exp, col_imp = st.columns(2)
        with col_exp:
            st.markdown('<div class="card-title">Export</div>', unsafe_allow_html=True)
            if scenes:
                # ── Build export payload: normalise every scene to use 'assets' key ──
                export_scenes = []
                for sc in scenes:
                    sc_export = dict(sc)
                    # Ensure the exported key is always 'assets'
                    if "assets" not in sc_export:
                        sc_export["assets"] = sc_export.pop("required_assets", sc_export.pop("models_3d", []))
                    # Remove legacy keys if present alongside 'assets'
                    sc_export.pop("required_assets", None)
                    sc_export.pop("models_3d", None)
                    export_scenes.append(sc_export)

                export_payload = {
                    "name": active_sb["name"],
                    "created": active_sb.get("created", ""),
                    "scenes": export_scenes
                }
                st.download_button(
                    label="📥 Download Storyboard JSON",
                    data=json.dumps(export_payload, indent=2),
                    file_name=f"{active_sb['name'].replace(' ','_')}_storyboard.json",
                    mime="application/json",
                    use_container_width=True
                )
                # Markdown table preview
                st.markdown("---")
                st.markdown("**Scene Table Preview**")
                header = "| # | Title | Narration | Assets | Animation |"
                sep    = "|---|-------|-----------|--------|-----------|"
                rows_md = [
                    f"| {s.get('scene_number','?')} | {s.get('title','')} | {s.get('narration','')[:60]} | {', '.join(get_scene_assets(s))} | {s.get('animation','')} |"
                    for s in scenes
                ]
                st.markdown("\n".join([header, sep] + rows_md))
            else:
                st.info("No scenes to export yet.")

        with col_imp:
            st.markdown('<div class="card-title">Import into Active Storyboard</div>', unsafe_allow_html=True)
            st.caption("Upload a JSON file exported from LPVision Studio or a raw scenes array.")
            imp = st.file_uploader("Choose JSON file", type=["json"], key="export_tab_import")
            if imp:
                try:
                    data = json.load(imp)
                    if isinstance(data, list):
                        imported_scenes = normalise_scenes(data)
                    elif isinstance(data, dict) and "scenes" in data:
                        imported_scenes = normalise_scenes(data["scenes"])
                    else:
                        st.error("Unrecognized format.")
                        imported_scenes = []
                    if imported_scenes:
                        if st.button("⬆ Apply Imported Scenes", key="apply_import"):
                            st.session_state.projects[st.session_state.active_project]["storyboards"][active_sb_id]["scenes"] = imported_scenes
                            st.success(f"Imported {len(imported_scenes)} scenes!")
                            st.rerun()
                except Exception as e:
                    st.error(f"Parse error: {e}")
