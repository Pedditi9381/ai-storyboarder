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
except Exception:
    GEMINI_API_KEY = None

GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"

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
            # Strip markdown fences
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```", 2)[-1] if raw.count("```") >= 2 else raw
                raw = raw.lstrip("json").strip()
                if raw.endswith("```"):
                    raw = raw[:-3].strip()
            # Fix control characters inside JSON strings:
            # Replace literal newlines/tabs inside the JSON text with escaped versions
            import re
            def fix_control_chars(s):
                # Find all string values and escape control chars within them
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
                        if ch == '\n':
                            result.append('\\n')
                        elif ch == '\r':
                            result.append('\\r')
                        elif ch == '\t':
                            result.append('\\t')
                        else:
                            result.append(ch)
                    else:
                        result.append(ch)
                return ''.join(result)

            raw = fix_control_chars(raw)
            scenes = json.loads(raw)
            return normalise_scenes(scenes)
        st.error(f"Groq error {resp.status_code}: {resp.text[:200]}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSON parse error: {e}")
        # Show a snippet around the error location for debugging
        char = e.pos
        snippet = raw[max(0, char-40):char+40] if 'raw' in dir() else ""
        st.code(f"...{snippet}...", language="text")
        return None
    except Exception as e:
        st.error(f"Generation failed: {e}")
        return None

# ─── GEMINI IMAGE GENERATION ───────────────────────────────────────────────────
def generate_scene_image(sc):
    if not GEMINI_API_KEY:
        st.error("Add GEMINI_API_KEY to Streamlit Secrets.")
        return None
    vd     = sc.get("visual_description", "")
    title  = sc.get("title", "")
    assets = ", ".join(get_scene_assets(sc))
    labels = ", ".join(sc.get("labels", []))
    narr   = sc.get("narration", "")[:200]
    prompt = (
        f"3D educational animation storyboard frame. Scene: '{title}'. "
        f"Visual: {vd} "
        f"3D models present: {assets}. On-screen labels: {labels}. Context: {narr}. "
        "Style: dark studio background, clean instructional 3D render, "
        "vivid neon accent lighting, high detail, no text overlays."
    )
    headers = {"Content-Type": "application/json"}
    # Imagen 3 uses the :predict endpoint with instances/parameters format
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9",
            "safetyFilterLevel": "block_few",
            "personGeneration": "allow_adult"
        }
    }
    try:
        resp = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload, timeout=90)
        if resp.status_code == 200:
            data = resp.json()
            predictions = data.get("predictions", [])
            if predictions and "bytesBase64Encoded" in predictions[0]:
                return predictions[0]["bytesBase64Encoded"]
            st.warning("Imagen returned no image in response.")
            return None
        st.error(f"Gemini error {resp.status_code}: {resp.text[:400]}")
        return None
    except Exception as e:
        st.error(f"Image generation failed: {e}")
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
                st.session_state.active_project    = pid
                st.session_state.active_storyboard = None
                st.session_state.active_tab        = 0
                st.rerun()

    for pid, proj in st.session_state.projects.items():
        is_active = pid == st.session_state.active_project
        sb_count  = len(proj.get("storyboards", {}))
        lbl       = f"{'▸ ' if is_active else ''}{proj['name']}  [{sb_count}]"
        if st.button(lbl, key=f"proj_btn_{pid}", use_container_width=True):
            st.session_state.active_project    = pid
            st.session_state.active_storyboard = None
            st.session_state.active_tab        = 0
            st.rerun()

    if len(st.session_state.projects) > 1:
        st.markdown("---")
        with st.expander("🗑 Delete Active Project"):
            st.warning(f"Delete **{get_active_project().get('name','')}**?")
            if st.button("Confirm Delete", key="del_proj_confirm"):
                del st.session_state.projects[st.session_state.active_project]
                st.session_state.active_project    = list(st.session_state.projects.keys())[0]
                st.session_state.active_storyboard = None
                st.session_state.active_tab        = 0
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
proj         = get_active_project()
proj_name    = proj.get("name", "Untitled")
storyboards  = proj.get("storyboards", {})
active_sb    = get_active_storyboard()
active_sb_id = st.session_state.active_storyboard

# Top bar
sb_title = active_sb["name"] if active_sb else "—"
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:0.6rem 0;border-bottom:1px solid #1e1e3a;margin-bottom:1rem;">
  <div style="display:flex;align-items:center;gap:10px;">
    <span style="font-size:14px;font-weight:600;color:#94a3b8;">{proj_name}</span>
    <span style="color:#334155;">›</span>
    <span style="font-size:14px;font-weight:700;color:#f1f5f9;">
      {sb_title if active_sb else 'Select a Storyboard'}
    </span>
  </div>
  <div style="font-size:12px;color:#475569;font-family:'JetBrains Mono',monospace;">
    {len(storyboards)} storyboard{'s' if len(storyboards)!=1 else ''}
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
# We use st.session_state.active_tab to track which tab should be "active".
# Streamlit doesn't allow programmatic tab switching, so we pass the
# default_tab_index to st.tabs (supported in newer Streamlit versions via
# the internal API). We use a workaround: render a JS snippet to click the
# right tab on load.
_tab_js = st.session_state.active_tab
st.markdown(f"""
<script>
  window._targetTab = {_tab_js};
  function switchTab() {{
    var btns = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
    if (btns.length > window._targetTab) {{
      btns[window._targetTab].click();
    }}
  }}
  setTimeout(switchTab, 300);
</script>
""", unsafe_allow_html=True)

tabs = st.tabs(["📋 Storyboards", "🎬 Editor", "📦 Export / Import"])

# ════════════════════════════════════════════════════════════
# TAB 0 — STORYBOARD LIST
# ════════════════════════════════════════════════════════════
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
                st.session_state.active_tab        = 1
                st.session_state.editing_scene     = None
                st.rerun()
        with c2:
            import_file = st.file_uploader("Import JSON", type=["json"], key="import_sb", label_visibility="collapsed")
            if import_file:
                try:
                    imported = json.load(import_file)
                    sbid = str(uuid.uuid4())
                    if isinstance(imported, list):
                        sc_imp  = normalise_scenes(imported)
                        nm_imp  = import_file.name.replace(".json", "")
                    elif isinstance(imported, dict) and "scenes" in imported:
                        sc_imp  = normalise_scenes(imported["scenes"])
                        nm_imp  = imported.get("name", import_file.name.replace(".json", ""))
                    else:
                        st.error("Unrecognised format.")
                        sc_imp = []
                        nm_imp = "Imported"
                    if sc_imp:
                        st.session_state.projects[st.session_state.active_project]["storyboards"][sbid] = {
                            "name": nm_imp, "created": datetime.now().strftime("%b %d, %Y"), "scenes": sc_imp
                        }
                        st.session_state.active_storyboard = sbid
                        st.session_state.active_tab        = 1
                        st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {e}")

    st.markdown("---")
    if not storyboards:
        st.markdown('<div style="text-align:center;padding:3rem;color:#334155;">No storyboards yet. Create one above.</div>', unsafe_allow_html=True)
    else:
        for sbid, sb in storyboards.items():
            n_sc   = len(sb.get("scenes", []))
            is_open = sbid == active_sb_id
            ci, co, cd = st.columns([6, 1.5, 1])
            with ci:
                st.markdown(f"""
                <div style="padding:0.5rem 0;">
                  <div style="font-size:14px;font-weight:600;
                              color:{'#93c5fd' if is_open else '#e2e8f0'};">
                    {'▸ ' if is_open else ''}{sb['name']}
                  </div>
                  <div style="font-size:12px;color:#475569;">
                    {sb.get('created','')} · {n_sc} scene{'s' if n_sc!=1 else ''}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with co:
                if st.button("Open →", key=f"open_{sbid}", use_container_width=True):
                    st.session_state.active_storyboard = sbid
                    st.session_state.active_tab        = 1
                    st.session_state.editing_scene     = None
                    st.rerun()
            with cd:
                if st.button("🗑", key=f"del_{sbid}", use_container_width=True):
                    del st.session_state.projects[st.session_state.active_project]["storyboards"][sbid]
                    if active_sb_id == sbid:
                        st.session_state.active_storyboard = None
                    st.rerun()
            st.markdown('<hr style="margin:0;border-color:#1e1e3a;">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 1 — EDITOR
# ════════════════════════════════════════════════════════════
with tabs[1]:
    if not active_sb:
        st.info("Open or create a storyboard from the **Storyboards** tab.")
    else:
        # ── INPUT / GENERATION CONTROLS ───────────────────────────────────────
        with st.expander("⚙️ Generate / Input Controls", expanded=not active_sb.get("scenes")):
            c1, c2 = st.columns([1, 1])
            with c1:
                num_scenes = st.slider("Scenes to generate", 3, 12, 6, key="num_scenes_slider")
                input_type = st.radio("Source", ["Plain Text", "PDF Document"], horizontal=True, key="input_type_radio")
            with c2:
                final_text = ""
                if input_type == "Plain Text":
                    final_text = st.text_area("Paste content", height=130,
                        placeholder="e.g. Working of a Steam Engine…", key="plain_text_input")
                    st.caption(f"{len(final_text)} chars")
                else:
                    pdf_up = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_uploader")
                    if pdf_up:
                        reader = PyPDF2.PdfReader(pdf_up)
                        for pg in reader.pages:
                            final_text += (pg.extract_text() or "")
                        st.success(f"PDF extracted · {len(final_text)} chars")

            gc, cc = st.columns(2)
            with gc:
                gen_btn = st.button(f"🚀 Generate {num_scenes} Scenes", key="gen_btn", use_container_width=True)
            with cc:
                clr_btn = st.button("✕ Clear All Scenes", key="clear_btn", use_container_width=True)

            if clr_btn:
                save_scenes([])
                st.session_state.editing_scene = None
                st.rerun()
            if gen_btn and final_text:
                with st.spinner("Generating scenes with Groq…"):
                    new_sc = generate_scenes_groq(final_text, num_scenes)
                    if new_sc:
                        save_scenes(new_sc)
                        st.session_state.editing_scene = None
                        st.success(f"✓ {len(new_sc)} scenes generated!")
                        st.rerun()
            elif gen_btn and not final_text:
                st.warning("Paste content or upload a PDF first.")

        # ── SCENE CARDS ───────────────────────────────────────────────────────
        scenes = active_sb.get("scenes", [])

        if not scenes:
            st.markdown("""
            <div style="text-align:center;padding:5rem 2rem;color:#334155;
                        border:1px dashed #1e1e3a;border-radius:16px;margin-top:1rem;">
              <div style="font-size:3rem;">🎞</div>
              <div style="font-size:15px;font-weight:600;color:#475569;margin-top:0.5rem;">
                No scenes yet
              </div>
              <div style="font-size:13px;margin-top:0.3rem;">
                Open the controls above and hit Generate.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Storyboard header
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        padding:0.65rem 1.1rem;background:#0d0d1a;border:1px solid #1e1e3a;
                        border-radius:12px;margin:0.5rem 0 1.25rem 0;">
              <div style="font-size:13px;font-weight:700;color:#e2e8f0;">
                📋 {active_sb['name']}
              </div>
              <div style="font-size:12px;color:#475569;font-family:'JetBrains Mono',monospace;">
                {len(scenes)} SCENE{'S' if len(scenes)!=1 else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)

            for i, sc in enumerate(scenes):
                assets  = get_scene_assets(sc)
                labels  = sc.get("labels", [])
                anim    = sc.get("animation", "").strip()
                vd      = sc.get("visual_description", "").strip()
                narr    = sc.get("narration", "").strip()
                snum    = sc.get("scene_number", i + 1)
                title   = sc.get("title", "Untitled")
                img_b64 = sc.get("scene_image")
                editing = (st.session_state.editing_scene == i)

                # ── SCENE HEADER ROW ─────────────────────────────────────────
                h_num, h_title, h_edit, h_img = st.columns([0.07, 0.55, 0.16, 0.22])
                with h_num:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#2563eb,#7c3aed);
                                color:white;font-size:10px;font-weight:800;
                                letter-spacing:0.12em;padding:5px 8px;border-radius:14px;
                                font-family:'JetBrains Mono',monospace;text-align:center;margin-top:6px;">
                      {snum:02d}
                    </div>
                    """, unsafe_allow_html=True)
                with h_title:
                    st.markdown(f"""
                    <div style="font-size:15px;font-weight:700;color:#f1f5f9;
                                padding-top:4px;letter-spacing:0.01em;">{title}</div>
                    """, unsafe_allow_html=True)
                with h_edit:
                    edit_label = "✅ Done Editing" if editing else "✏️ Edit Scene"
                    if st.button(edit_label, key=f"edit_toggle_{i}", use_container_width=True):
                        st.session_state.editing_scene = None if editing else i
                        st.rerun()
                with h_img:
                    img_label = "🔄 Regenerate Image" if img_b64 else "🖼 Generate Image"
                    gen_img_btn = st.button(img_label, key=f"gen_img_{i}", use_container_width=True)

                # ── EDIT MODE ─────────────────────────────────────────────────
                if editing:
                    with st.container():
                        st.markdown("""
                        <div style="background:#0a0a1a;border:1px solid #2563eb;
                                    border-radius:12px;padding:1rem 1.1rem;margin:0.6rem 0;">
                        """, unsafe_allow_html=True)

                        ea, eb = st.columns(2)
                        with ea:
                            new_title      = st.text_input("Scene Title", value=title,
                                                key=f"e_title_{i}")
                            new_assets_str = st.text_input(
                                "Assets (comma-separated GLB names)",
                                value=", ".join(assets), key=f"e_assets_{i}")
                            new_labels_str = st.text_input(
                                "Labels (comma-separated UI text)",
                                value=", ".join(labels), key=f"e_labels_{i}")
                        with eb:
                            new_narr = st.text_area("Narration", value=narr,
                                                    height=110, key=f"e_narr_{i}")
                            new_vd   = st.text_area("Visual Description", value=vd,
                                                    height=75,  key=f"e_vd_{i}")

                        new_anim = st.text_area("Animation Logic (numbered steps)",
                                                value=anim, height=100, key=f"e_anim_{i}")

                        sv_col, _ = st.columns([1, 4])
                        with sv_col:
                            if st.button("💾 Save Changes", key=f"save_scene_{i}",
                                         use_container_width=True):
                                scenes[i]["title"]              = new_title.strip()
                                scenes[i]["assets"]             = [x.strip() for x in new_assets_str.split(",") if x.strip()]
                                scenes[i]["labels"]             = [x.strip() for x in new_labels_str.split(",") if x.strip()]
                                scenes[i]["narration"]          = new_narr.strip()
                                scenes[i]["visual_description"] = new_vd.strip()
                                scenes[i]["animation"]          = new_anim.strip()
                                save_scenes(scenes)
                                st.session_state.editing_scene  = None
                                st.rerun()

                        st.markdown("</div>", unsafe_allow_html=True)

                # ── DISPLAY MODE ──────────────────────────────────────────────
                else:
                    # ROW 1: Image | Assets | Labels | Narration
                    img_col, ca, cb, cn = st.columns([1, 1, 1, 2])

                    with img_col:
                        if img_b64:
                            st.markdown(
                                f'<img class="scene-img" src="data:image/png;base64,{img_b64}" />',
                                unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="height:145px;background:#0d0d1a;border:1px dashed #2d2d5a;
                                        border-radius:8px;display:flex;align-items:center;
                                        justify-content:center;flex-direction:column;gap:6px;">
                              <span style="font-size:1.8rem;opacity:0.5;">🖼</span>
                              <span style="font-size:11px;color:#334155;">No image yet</span>
                            </div>
                            """, unsafe_allow_html=True)

                    with ca:
                        asset_tags = "".join([
                            f'<span style="display:inline-block;margin:2px 3px 2px 0;padding:3px 9px;'
                            f'border-radius:5px;background:#0f1f3d;color:#60a5fa;font-size:11px;'
                            f'font-weight:600;font-family:JetBrains Mono,monospace;">{a}</span>'
                            for a in assets
                        ]) or '<span style="color:#334155;font-size:11px;">—</span>'
                        st.markdown(f"""
                        <div style="background:#0d1117;border:1px solid #1e3a5f;border-radius:10px;
                                    padding:0.75rem 0.85rem;height:145px;overflow-y:auto;">
                          <div style="font-size:9px;font-weight:800;letter-spacing:0.15em;
                                      color:#3b82f6;text-transform:uppercase;margin-bottom:7px;">
                            🔷 3D Assets
                          </div>
                          <div style="line-height:1.9;">{asset_tags}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with cb:
                        label_tags = "".join([
                            f'<span style="display:inline-block;margin:2px 3px 2px 0;padding:3px 9px;'
                            f'border-radius:5px;background:#0f2d1a;color:#4ade80;font-size:11px;'
                            f'font-weight:600;">{l}</span>'
                            for l in labels
                        ]) or '<span style="color:#334155;font-size:11px;">—</span>'
                        st.markdown(f"""
                        <div style="background:#0d1a12;border:1px solid #1a3d25;border-radius:10px;
                                    padding:0.75rem 0.85rem;height:145px;overflow-y:auto;">
                          <div style="font-size:9px;font-weight:800;letter-spacing:0.15em;
                                      color:#4ade80;text-transform:uppercase;margin-bottom:7px;">
                            🟢 UI Labels
                          </div>
                          <div style="line-height:1.9;">{label_tags}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with cn:
                        st.markdown(f"""
                        <div style="background:#1a0d1a;border:1px solid #3d1a2e;border-radius:10px;
                                    padding:0.75rem 0.85rem;height:145px;overflow-y:auto;
                                    border-left:3px solid #fb7185;">
                          <div style="font-size:9px;font-weight:800;letter-spacing:0.15em;
                                      color:#fb7185;text-transform:uppercase;margin-bottom:7px;">
                            🎙 Narration
                          </div>
                          <div style="font-size:12px;color:#f1f5f9;line-height:1.75;font-style:italic;">
                            {narr if narr else '—'}
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                    # ROW 2: Animation | Visual Description
                    canim, cvd = st.columns([1, 1])

                    with canim:
                        anim_lines = [l.strip() for l in anim.replace("\r\n", "\n").split("\n") if l.strip()]
                        steps_html = "".join([
                            f'<div style="display:flex;gap:8px;margin-bottom:5px;align-items:flex-start;">'
                            f'<span style="min-width:18px;height:18px;border-radius:50%;'
                            f'background:linear-gradient(135deg,#d97706,#f59e0b);color:#000;'
                            f'font-size:9px;font-weight:800;display:flex;align-items:center;'
                            f'justify-content:center;flex-shrink:0;margin-top:2px;">{idx+1}</span>'
                            f'<span style="font-size:12px;color:#fde68a;line-height:1.5;">'
                            f'{line.lstrip("0123456789. ") if line[:1].isdigit() else line}</span>'
                            f'</div>'
                            for idx, line in enumerate(anim_lines)
                        ]) or '<span style="color:#334155;font-size:11px;">—</span>'
                        st.markdown(f"""
                        <div style="background:#1a1400;border:1px solid #3d2e00;border-radius:10px;
                                    padding:0.75rem 0.85rem;border-left:3px solid #f59e0b;">
                          <div style="font-size:9px;font-weight:800;letter-spacing:0.15em;
                                      color:#f59e0b;text-transform:uppercase;margin-bottom:8px;">
                            ⚡ Animation Logic (GLB Safe)
                          </div>
                          {steps_html}
                        </div>
                        """, unsafe_allow_html=True)

                    with cvd:
                        st.markdown(f"""
                        <div style="background:#120d1a;border:1px solid #2d1a4a;border-radius:10px;
                                    padding:0.75rem 0.85rem;border-left:3px solid #a78bfa;">
                          <div style="font-size:9px;font-weight:800;letter-spacing:0.15em;
                                      color:#a78bfa;text-transform:uppercase;margin-bottom:7px;">
                            🎨 Visual Description
                          </div>
                          <div style="font-size:12px;color:#c4b5fd;line-height:1.7;">
                            {vd if vd else '—'}
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                # ── GEMINI IMAGE GENERATION (outside edit/display if) ─────────
                if gen_img_btn:
                    with st.spinner(f"Generating image for Scene {snum:02d} with Gemini…"):
                        b64 = generate_scene_image(sc)
                        if b64:
                            scenes[i]["scene_image"] = b64
                            save_scenes(scenes)
                            st.success(f"✓ Image generated for Scene {snum:02d}!")
                            st.rerun()

                # ── DELETE + DIVIDER ──────────────────────────────────────────
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                _, del_col = st.columns([7, 1])
                with del_col:
                    if st.button("🗑 Delete", key=f"del_scene_{i}", use_container_width=True):
                        scenes.pop(i)
                        save_scenes(scenes)
                        if st.session_state.editing_scene == i:
                            st.session_state.editing_scene = None
                        st.rerun()

                st.markdown("""
                <div style="height:1px;background:linear-gradient(90deg,#2563eb22,#7c3aed55,#2563eb22);
                            margin:0.75rem 0 1.4rem 0;border-radius:2px;"></div>
                """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — EXPORT / IMPORT
# ════════════════════════════════════════════════════════════
with tabs[2]:
    if not active_sb:
        st.info("Open a storyboard first to export it.")
    else:
        scenes = active_sb.get("scenes", [])
        col_exp, col_imp = st.columns(2)

        with col_exp:
            st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:0.12em;color:#475569;text-transform:uppercase;margin-bottom:0.75rem;">Export</div>', unsafe_allow_html=True)
            if scenes:
                export_scenes = []
                for sc in scenes:
                    sc_exp = dict(sc)
                    if "assets" not in sc_exp:
                        sc_exp["assets"] = sc_exp.pop("required_assets", sc_exp.pop("models_3d", []))
                    sc_exp.pop("required_assets", None)
                    sc_exp.pop("models_3d", None)
                    if "labels" not in sc_exp:
                        sc_exp["labels"] = []
                    # Don't export giant base64 image by default (optional toggle)
                    export_scenes.append(sc_exp)

                include_images = st.checkbox("Include generated images in export (increases file size)", value=False)
                if not include_images:
                    for s in export_scenes:
                        s.pop("scene_image", None)

                export_payload = {
                    "name": active_sb["name"],
                    "created": active_sb.get("created", ""),
                    "scenes": export_scenes
                }
                st.download_button(
                    "📥 Download Storyboard JSON",
                    data=json.dumps(export_payload, indent=2),
                    file_name=f"{active_sb['name'].replace(' ','_')}_storyboard.json",
                    mime="application/json",
                    use_container_width=True
                )
                st.markdown("---")
                st.markdown("**Scene Table Preview**")
                header  = "| # | Title | Assets | Labels | Narration |"
                sep     = "|---|-------|--------|--------|-----------|"
                rows_md = [
                    f"| {s.get('scene_number','?')} | {s.get('title','')} "
                    f"| {', '.join(get_scene_assets(s))} "
                    f"| {', '.join(s.get('labels',[]))} "
                    f"| {s.get('narration','')[:80]}{'…' if len(s.get('narration',''))>80 else ''} |"
                    for s in scenes
                ]
                st.markdown("\n".join([header, sep] + rows_md))
            else:
                st.info("No scenes to export yet.")

        with col_imp:
            st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:0.12em;color:#475569;text-transform:uppercase;margin-bottom:0.75rem;">Import into Active Storyboard</div>', unsafe_allow_html=True)
            st.caption("Upload a JSON exported from LPVision Studio or a raw scenes array.")
            imp = st.file_uploader("Choose JSON", type=["json"], key="export_tab_import")
            if imp:
                try:
                    data = json.load(imp)
                    if isinstance(data, list):
                        imp_sc = normalise_scenes(data)
                    elif isinstance(data, dict) and "scenes" in data:
                        imp_sc = normalise_scenes(data["scenes"])
                    else:
                        st.error("Unrecognised format.")
                        imp_sc = []
                    if imp_sc:
                        if st.button("⬆ Apply Imported Scenes", key="apply_import"):
                            save_scenes(imp_sc)
                            st.session_state.active_tab    = 1
                            st.session_state.editing_scene = None
                            st.rerun()
                except Exception as e:
                    st.error(f"Parse error: {e}")
