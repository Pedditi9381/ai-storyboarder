import streamlit as st
import requests
import PyPDF2
import json
import uuid
import base64
import re
import io
import time
from datetime import datetime

# â”€â”€â”€ PAGE CONFIG â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.set_page_config(page_title="LPVision Studio", layout="wide", page_icon="ðŸŽ¬")

# â”€â”€â”€ CSS + LIGHTBOX â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
.sidebar-brand .brand-text { font-size:12px; font-weight:600; color:#94a3b8; letter-spacing:0.1em; }
.sidebar-brand .brand-name { font-size:15px; font-weight:700; color:#f1f5f9; }
.stButton>button { background:#1e1e3a !important; color:#94a3b8 !important; border:1px solid #2d2d5a !important; border-radius:8px !important; font-size:13px !important; font-weight:500 !important; font-family:'Space Grotesk',sans-serif !important; transition:all 0.15s !important; }
.stButton>button:hover { background:#2d2d5a !important; color:#e2e8f0 !important; border-color:#3b4f8a !important; }
.stDownloadButton>button { background:#0f2a1e !important; color:#34d399 !important; border:1px solid #1a4a33 !important; border-radius:8px !important; font-family:'Space Grotesk',sans-serif !important; }
.stTextArea textarea { background:#0d0d1a !important; color:#e2e8f0 !important; border:1px solid #2d2d5a !important; border-radius:8px !important; font-family:'Space Grotesk',sans-serif !important; font-size:13px !important; }
.stTextInput input { background:#0d0d1a !important; color:#e2e8f0 !important; border:1px solid #2d2d5a !important; border-radius:8px !important; font-family:'Space Grotesk',sans-serif !important; font-size:13px !important; }
label { color:#64748b !important; font-size:12px !important; font-weight:500 !important; }
.stTabs [data-baseweb="tab-list"] { background:transparent !important; gap:0; border-bottom:1px solid #1e1e3a; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#475569 !important; font-family:'Space Grotesk',sans-serif !important; font-size:13px !important; border-bottom:2px solid transparent !important; }
.stTabs [aria-selected="true"] { color:#f1f5f9 !important; border-bottom-color:#3b82f6 !important; }
.stTabs [data-baseweb="tab-panel"] { padding:1.25rem 0 0 0 !important; }
.streamlit-expanderHeader { background:#0d0d1a !important; color:#94a3b8 !important; border:1px solid #1e1e3a !important; border-radius:8px !important; }
[data-testid="stFileUploadDropzone"] { background:#0d0d1a !important; border:1px dashed #2d2d5a !important; border-radius:8px !important; }
.stAlert { background:#0d0d1a !important; border:1px solid #1e1e3a !important; border-radius:8px !important; color:#94a3b8 !important; }
hr { border-color:#1e1e3a !important; }
.stRadio label { color:#94a3b8 !important; }

/* â”€â”€ Clickable scene image â”€â”€ */
.scene-img-wrap { position:relative; cursor:zoom-in; display:block; }
.scene-img-wrap img { width:100%; border-radius:8px; object-fit:cover; border:1px solid #2d2d5a; display:block; transition:transform 0.15s,box-shadow 0.15s; }
.scene-img-wrap:hover img { transform:scale(1.02); box-shadow:0 0 0 2px #3b82f6,0 8px 32px rgba(59,130,246,0.25); }
.zoom-hint { position:absolute; bottom:6px; right:8px; font-size:10px; color:rgba(255,255,255,0.6); background:rgba(0,0,0,0.6); border-radius:4px; padding:2px 7px; pointer-events:none; }

/* â”€â”€ Lightbox â”€â”€ */
#lpv-lightbox { display:none; position:fixed; z-index:99999; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.93); align-items:center; justify-content:center; backdrop-filter:blur(10px); }
#lpv-lightbox.open { display:flex; }
#lpv-lightbox img { max-width:92vw; max-height:88vh; border-radius:12px; box-shadow:0 0 60px rgba(59,130,246,0.4),0 0 0 1px #3b82f6; object-fit:contain; }
#lpv-lb-close { position:fixed; top:18px; right:26px; font-size:34px; color:#e2e8f0; cursor:pointer; background:none; border:none; line-height:1; opacity:0.7; transition:opacity 0.15s; }
#lpv-lb-close:hover { opacity:1; }
#lpv-lb-cap { position:fixed; bottom:22px; left:50%; transform:translateX(-50%); font-size:12px; color:#94a3b8; background:rgba(0,0,0,0.75); padding:6px 18px; border-radius:20px; white-space:nowrap; font-family:'JetBrains Mono',monospace; letter-spacing:0.05em; }
</style>

<!-- Lightbox DOM -->
<div id="lpv-lightbox">
  <button id="lpv-lb-close" onclick="closeLB()">&#x2715;</button>
  <img id="lpv-lb-img" src="" alt=""/>
  <div id="lpv-lb-cap"></div>
</div>
<script>
function openLB(src, cap) {
  document.getElementById('lpv-lb-img').src = src;
  document.getElementById('lpv-lb-cap').textContent = cap || '';
  document.getElementById('lpv-lightbox').classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeLB() {
  document.getElementById('lpv-lightbox').classList.remove('open');
  document.getElementById('lpv-lb-img').src = '';
  document.body.style.overflow = '';
}
document.getElementById('lpv-lightbox').addEventListener('click', function(e){ if(e.target===this) closeLB(); });
document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeLB(); });
</script>
""", unsafe_allow_html=True)

# â”€â”€â”€ SESSION STATE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def init_state():
    defaults = {
        "active_project": None, "active_storyboard": None,
        "editing_scene": None, "goto_editor": False, "gen_all_images": False
    }
    if "projects" not in st.session_state:
        did = str(uuid.uuid4())
        st.session_state.projects = {
            did: {"name": "My First Project", "created": datetime.now().strftime("%b %d, %Y"), "storyboards": {}}
        }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if not st.session_state.active_project:
        st.session_state.active_project = list(st.session_state.projects.keys())[0]

init_state()

# â”€â”€â”€ API KEYS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
GROQ_API_KEY   = st.secrets.get("GROQ_API_KEY",   None)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", None)
GROQ_URL       = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_MODELS  = [
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image-preview",
    "gemini-2.0-flash-preview-image-generation",
]
GEMINI_BASE    = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# â”€â”€â”€ HELPERS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def get_active_project():
    return st.session_state.projects.get(st.session_state.active_project, {})

def get_active_storyboard():
    proj  = get_active_project()
    sb_id = st.session_state.active_storyboard
    return proj.get("storyboards", {}).get(sb_id) if sb_id else None

def get_scene_assets(sc):
    return sc.get("assets", sc.get("required_assets", sc.get("models_3d", [])))

def save_scenes(scenes):
    pid  = st.session_state.active_project
    sbid = st.session_state.active_storyboard
    st.session_state.projects[pid]["storyboards"][sbid]["scenes"] = scenes

def normalise_scenes(scenes):
    for sc in scenes:
        if "assets" not in sc:
            sc["assets"] = sc.pop("required_assets", sc.pop("models_3d", []))
        sc.setdefault("labels", [])
        sc.setdefault("scene_image", None)
    return scenes

def pill(text, bg, color):
    return (f'<span style="display:inline-block;margin:2px 3px 2px 0;padding:3px 10px;'
            f'border-radius:5px;background:{bg};color:{color};font-size:11px;font-weight:600;">'
            f'{text}</span>')

def section_box(title, color, html, bg, border, left_accent=None):
    acc = f"border-left:3px solid {left_accent};" if left_accent else ""
    return (f'<div style="background:{bg};border:1px solid {border};border-radius:10px;'
            f'padding:0.75rem 0.85rem;{acc}height:100%;box-sizing:border-box;">'
            f'<div style="font-size:9px;font-weight:800;letter-spacing:0.15em;color:{color};'
            f'text-transform:uppercase;margin-bottom:7px;">{title}</div>{html}</div>')

def clickable_img(b64, scene_title, snum):
    uri = f"data:image/png;base64,{b64}"
    cap = f"Scene {snum:02d}  Â·  {scene_title}".replace("'", "&#39;")
    return (f'<div class="scene-img-wrap" onclick="openLB(\'{uri}\',\'{cap}\')">'
            f'<img src="{uri}" alt="{cap}"/>'
            f'<span class="zoom-hint">ðŸ” Click to expand</span></div>')

# â”€â”€â”€ GROQ helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def fix_control_chars(s):
    res, in_str, esc = [], False, False
    for ch in s:
        if esc: res.append(ch); esc = False; continue
        if ch == '\\': res.append(ch); esc = True; continue
        if ch == '"': in_str = not in_str; res.append(ch); continue
        if in_str:
            if   ch == '\n': res.append('\\n')
            elif ch == '\r': res.append('\\r')
            elif ch == '\t': res.append('\\t')
            else:            res.append(ch)
        else: res.append(ch)
    return ''.join(res)

def strip_fences(raw):
    raw = raw.strip()
    raw = re.sub(r'^```[a-zA-Z]*\n?', '', raw)
    return re.sub(r'```$', '', raw.strip()).strip()

# â”€â”€â”€ GROQ: SCENE GENERATION â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def generate_scenes_groq(text, num_scenes):
    if not GROQ_API_KEY:
        st.error("Add GROQ_API_KEY to Streamlit Secrets."); return None
    sys_p = (f"You are a Senior 3D Instructional Animator. Convert the input into EXACTLY {num_scenes} storyboard scenes.\n"
             "Return ONLY a valid JSON array. No markdown fences. No explanation. No preamble.\n"
             "Each element must have exactly these keys:\n"
             "  scene_number (int), title (str 3-6 words), assets (array of 3-6 lowercase_glb_names),\n"
             "  labels (array of 2-5 short UI caption strings), animation (str: numbered steps as plain text),\n"
             "  visual_description (str: 2-3 sentences on camera/lighting/layout),\n"
             "  narration (str: 2-4 complete educational sentences spoken by narrator)\n"
             "CRITICAL JSON RULES: Never use literal newline or tab characters inside any string value.\n"
             "Use the two-character sequence backslash-n to represent a line break inside a string.")
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role":"system","content":sys_p},
                     {"role":"user","content":f"Create a 3D educational storyboard for:\n\n{text[:6000]}"}],
        "temperature": 0.3, "max_tokens": 4096
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        raw  = strip_fences(resp.json()["choices"][0]["message"]["content"])
        raw  = fix_control_chars(raw)
        data = json.loads(raw)
        if not isinstance(data, list): st.error("Groq: unexpected format."); return None
        return normalise_scenes(data)
    except requests.HTTPError:
        st.error(f"Groq HTTP {resp.status_code}: {resp.text[:300]}"); return None
    except json.JSONDecodeError as e:
        st.error(f"JSON parse error @{e.pos}: {e.msg}")
        st.code(f"â€¦{raw[max(0,e.pos-60):e.pos+60]}â€¦"); return None
    except Exception as e:
        st.error(f"Generation failed: {e}"); return None

# â”€â”€â”€ IMAGE PROMPT: ANIMATION-LOGIC DRIVEN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def build_image_prompt(sc):
    """
    The ANIMATION LOGIC is the primary driver of what to depict.
    Assets, visual description, and narration provide supporting context.
    """
    title  = sc.get("title", "")
    assets = ", ".join(get_scene_assets(sc))
    labels = ", ".join(sc.get("labels", []))
    narr   = sc.get("narration", "")[:180]
    vd     = sc.get("visual_description", "")[:200]
    raw_a  = sc.get("animation", "").strip()
    lines  = [l.strip() for l in raw_a.replace("\\n","\n").split("\n") if l.strip()]
    anim   = " | ".join(lines) if lines else raw_a[:300]

    return (
        f"Professional 3D CGI educational animation storyboard frame. "
        f"Scene: '{title}'. "
        f"PRIMARY â€” Animation action to depict (show the key visual moment of this step): {anim}. "
        f"3D GLB assets present: {assets}. "
        f"On-screen annotation labels: {labels}. "
        f"Camera / staging: {vd} "
        f"Educational context: {narr}. "
        "Render: Blender 4 Cycles photorealistic, clean hard-surface meshes, subdivision level 2, "
        "beveled edges for GLB-export topology, PBR metallic/roughness workflow, "
        "four-point HDRI studio lighting (amber key 3200K, blue fill 6500K, purple-teal rim, white bounce), "
        "deep charcoal studio #12121e with subtle floor reflection, AO baked, "
        "cinema depth-of-field f/2.8, 16:9 widescreen, objects arranged to clearly illustrate the animation step, "
        "no 2D art, no cartoon, no text overlays, no watermarks."
    )

# â”€â”€â”€ GEMINI: SILENT QUOTA HANDLING â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _is_quota(code, msg):
    return code == 429 or "quota" in msg.lower() or "rate" in msg.lower()

def generate_scene_image_gemini(sc):
    if not GEMINI_API_KEY:
        return None, "no_key"
    prompt  = build_image_prompt(sc)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE","TEXT"],
                             "imageConfig": {"aspectRatio":"16:9","imageSize":"1K"}}
    }
    last = "no_models"
    for model in GEMINI_MODELS:
        url = f"{GEMINI_BASE.format(model=model)}?key={GEMINI_API_KEY}"
        try:
            resp = requests.post(url, headers={"Content-Type":"application/json"},
                                 json=payload, timeout=90)
            if resp.status_code == 200:
                for part in (resp.json().get("candidates",[{}])[0]
                             .get("content",{}).get("parts",[])):
                    inline = part.get("inlineData",{})
                    if inline.get("mimeType","").startswith("image/"):
                        return inline["data"], None
                last = "200_no_image"
            elif resp.status_code in (400, 404):
                last = f"{model}_unavailable"; continue
            else:
                try: msg = resp.json().get("error",{}).get("message","")
                except: msg = resp.text[:200]
                if _is_quota(resp.status_code, msg):
                    return None, "quota"   # silent signal
                last = f"{model}_{resp.status_code}"; break
        except Exception as e:
            last = f"{model}_exc_{e}"; continue
    return None, last

def generate_scene_image_pollinations(sc):
    enc = requests.utils.quote(build_image_prompt(sc)[:700])
    url = (f"https://image.pollinations.ai/prompt/{enc}"
           f"?width=1024&height=576&model=flux&nologo=true&enhance=true&seed=-1")
    try:
        resp = requests.get(url, timeout=120)
        if resp.status_code == 200 and "image" in resp.headers.get("content-type",""):
            return base64.b64encode(resp.content).decode("utf-8"), None
        return None, f"pollinations_{resp.status_code}"
    except Exception as e:
        return None, str(e)

def generate_scene_image(sc, status_slot=None):
    """
    Try Gemini; silently fall back to Pollinations on quota/fail.
    Never shows the long 429 error message.
    """
    def log(m):
        if status_slot: status_slot.caption(m)

    if GEMINI_API_KEY:
        b64, err = generate_scene_image_gemini(sc)
        if b64:
            log("âœ“ via Gemini")
            return b64
        if err == "quota":
            log("Gemini quota reached â€” switching to Pollinationsâ€¦")
        elif err not in ("no_key", "no_models", "200_no_image"):
            log("Gemini unavailable â€” switching to Pollinationsâ€¦")
        # fall through silently

    b64, err = generate_scene_image_pollinations(sc)
    if b64:
        log("âœ“ via Pollinations")
        return b64
    log(f"âš  Image failed: {err}")
    return None

# â”€â”€â”€ PDF EXPORT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def generate_storyboard_pdf(sb_name, scenes):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import mm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor, white
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, HRFlowable, Image as RLImage, KeepTogether)
        from reportlab.lib.enums import TA_CENTER
        from PIL import Image as PILImage
    except ImportError:
        return None, "reportlab or Pillow not installed."

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
        leftMargin=15*mm, rightMargin=15*mm, topMargin=12*mm, bottomMargin=12*mm,
        title=f"LPVision â€” {sb_name}", author="LPVision Studio")

    C = dict(bg=HexColor("#06060f"), card=HexColor("#0d0d1a"), bord=HexColor("#1e1e3a"),
             blue=HexColor("#3b82f6"), purp=HexColor("#8b5cf6"), green=HexColor("#4ade80"),
             ambr=HexColor("#f59e0b"), pink=HexColor("#fb7185"), text=HexColor("#e2e8f0"),
             mute=HexColor("#64748b"))

    def S(n, **k):
        b = dict(fontName="Helvetica", fontSize=9, leading=13, textColor=C["text"], spaceAfter=2)
        b.update(k); return ParagraphStyle(n, **b)

    story = [
        Paragraph("LPVision Studio", S("H", fontSize=22, fontName="Helvetica-Bold", leading=26)),
        Paragraph(f"Storyboard Export Â· {sb_name}", S("sub", fontSize=11, textColor=C["mute"])),
        Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y at %H:%M')} Â· {len(scenes)} Scenes",
                  S("dt", fontSize=8, textColor=C["mute"])),
        HRFlowable(width="100%", thickness=1, color=C["bord"], spaceAfter=8)
    ]
    for i, sc in enumerate(scenes):
        snum  = sc.get("scene_number", i+1); title = sc.get("title","Untitled")
        assets= get_scene_assets(sc);         labels= sc.get("labels",[])
        anim  = sc.get("animation","").strip().replace("\\n","\n")
        vd    = sc.get("visual_description","").strip()
        narr  = sc.get("narration","").strip(); b64 = sc.get("scene_image")

        img_cell = []
        if b64:
            try:
                pil  = PILImage.open(io.BytesIO(base64.b64decode(b64)))
                b2   = io.BytesIO(); pil.save(b2,"PNG"); b2.seek(0)
                img_cell.append(RLImage(b2, width=70*mm, height=39.4*mm))
            except: img_cell.append(Paragraph("[Image error]", S("ie", fontSize=8, textColor=C["mute"])))
        else:
            img_cell.append(Paragraph("[ No Image ]", S("ni", fontSize=8, textColor=C["mute"], alignment=TA_CENTER)))

        al  = [l.strip() for l in anim.split("\n") if l.strip()]
        ah  = "<br/>".join([f"{k+1}. {l.lstrip('0123456789.) ')}" for k,l in enumerate(al)]) or "â€”"
        at  = "  ".join([f"[{a}]" for a in assets]) or "â€”"
        lt  = "  ".join([f"[{l}]" for l in labels]) or "â€”"

        data = [[
            [Paragraph(f"{snum:02d}", S("sn", fontSize=18, fontName="Helvetica-Bold",
                        textColor=C["blue"], alignment=TA_CENTER, leading=22))],
            img_cell,
            [Paragraph(f"SCENE {snum:02d}", S("sl",fontSize=6,fontName="Helvetica-Bold",textColor=C["mute"],spaceAfter=3)),
             Paragraph(title, S("st",fontSize=12,fontName="Helvetica-Bold",textColor=C["text"],leading=16)),
             Spacer(1,4),
             Paragraph("3D ASSETS", S("al",fontSize=6,fontName="Helvetica-Bold",textColor=C["blue"],spaceAfter=2)),
             Paragraph(at, S("at",fontSize=7,textColor=C["blue"],leading=10)),
             Spacer(1,3),
             Paragraph("UI LABELS", S("ll",fontSize=6,fontName="Helvetica-Bold",textColor=C["green"],spaceAfter=2)),
             Paragraph(lt, S("lt",fontSize=7,textColor=C["green"],leading=10))],
            [Paragraph("NARRATION", S("nl",fontSize=6,fontName="Helvetica-Bold",textColor=C["pink"],spaceAfter=3)),
             Paragraph(narr or "â€”", S("nb",fontSize=8,fontName="Helvetica-Oblique",
                        textColor=HexColor("#fce7f3"),leading=12))],
            [Paragraph("ANIMATION LOGIC", S("anl",fontSize=6,fontName="Helvetica-Bold",textColor=C["ambr"],spaceAfter=3)),
             Paragraph(ah, S("an",fontSize=7.5,textColor=HexColor("#fde68a"),leading=11)),
             Spacer(1,5),
             Paragraph("VISUAL DESCRIPTION", S("vdl",fontSize=6,fontName="Helvetica-Bold",textColor=C["purp"],spaceAfter=3)),
             Paragraph(vd or "â€”", S("vd",fontSize=7.5,textColor=HexColor("#c4b5fd"),leading=11))]
        ]]
        tbl = Table(data, colWidths=[14*mm, 72*mm, 52*mm, 58*mm, 58*mm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),C["card"]),("BOX",(0,0),(-1,-1),1,C["bord"]),
            ("INNERGRID",(0,0),(-1,-1),0.5,HexColor("#151528")),("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("BACKGROUND",(0,0),(0,-1),HexColor("#0a1628")),("LINEAFTER",(0,0),(0,-1),2,C["blue"]),
            ("LINEBEFORE",(3,0),(3,-1),2,C["pink"]),("LINEBEFORE",(4,0),(4,-1),2,C["ambr"]),
        ]))
        story += [KeepTogether([tbl]), Spacer(1,5)]

    story += [HRFlowable(width="100%",thickness=0.5,color=C["bord"],spaceBefore=6),
              Paragraph(f"LPVision Studio Â· {sb_name} Â· {len(scenes)} Scenes Â· Â© {datetime.now().year} LearningPad",
                        S("ft",fontSize=7,textColor=C["mute"],alignment=TA_CENTER))]

    def on_page(canvas, doc):
        canvas.saveState(); canvas.setFillColor(C["bg"])
        canvas.rect(0,0,landscape(A4)[0],landscape(A4)[1],fill=1,stroke=0); canvas.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0); return buf.getvalue(), None

# â”€â”€â”€ SIDEBAR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with st.sidebar:
    st.markdown('''<div class="sidebar-brand"><div class="logo">LP</div>
      <div><div class="brand-text">LPVISION</div><div class="brand-name">Studio</div></div></div>
    ''', unsafe_allow_html=True)

    st.markdown('<div style="font-size:10px;font-weight:600;letter-spacing:0.15em;color:#475569;text-transform:uppercase;margin-bottom:0.5rem;">Projects</div>', unsafe_allow_html=True)

    with st.expander("ï¼‹ New Project"):
        new_proj_name = st.text_input("Project name", placeholder="e.g. Biology Ch3", key="new_proj_input")
        if st.button("Create Project", key="create_proj_btn"):
            if new_proj_name.strip():
                pid = str(uuid.uuid4())
                st.session_state.projects[pid] = {"name": new_proj_name.strip(),
                    "created": datetime.now().strftime("%b %d, %Y"), "storyboards": {}}
                st.session_state.active_project    = pid
                st.session_state.active_storyboard = None
                st.session_state.goto_editor       = False
                st.rerun()

    for pid, proj in st.session_state.projects.items():
        is_active = pid == st.session_state.active_project
        lbl = f"{'â–¸ ' if is_active else ''}{proj['name']}  [{len(proj.get('storyboards',{}))}]"
        if st.button(lbl, key=f"proj_btn_{pid}", use_container_width=True):
            st.session_state.active_project = pid
            st.session_state.active_storyboard = None
            st.session_state.goto_editor = False
            st.rerun()

    if len(st.session_state.projects) > 1:
        st.markdown("---")
        with st.expander("ðŸ—‘ Delete Project"):
            st.warning(f"Delete **{get_active_project().get('name','')}**?")
            if st.button("Confirm Delete", key="del_proj_confirm"):
                del st.session_state.projects[st.session_state.active_project]
                st.session_state.active_project    = list(st.session_state.projects.keys())[0]
                st.session_state.active_storyboard = None
                st.session_state.goto_editor       = False
                st.rerun()

    st.markdown("---")
    groq_ok = bool(GROQ_API_KEY); gem_ok = bool(GEMINI_API_KEY)
    st.markdown(f"""
    <div style="font-size:11px;color:#475569;line-height:2;">
      Groq <span style="color:{'#4ade80' if groq_ok else '#f87171'};">{'âœ“ Connected' if groq_ok else 'âœ— Add GROQ_API_KEY'}</span><br>
      Gemini <span style="color:{'#4ade80' if gem_ok else '#f59e0b'};">{'âœ“ Connected' if gem_ok else 'âš  Pollinations fallback'}</span>
    </div>
    <div style="font-size:10px;color:#334155;text-align:center;margin-top:10px;">Â© 2026 LearningPad</div>
    """, unsafe_allow_html=True)

# â”€â”€â”€ MAIN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
proj         = get_active_project()
proj_name    = proj.get("name", "Untitled")
storyboards  = proj.get("storyboards", {})
active_sb    = get_active_storyboard()
active_sb_id = st.session_state.active_storyboard

st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:0.6rem 0;border-bottom:1px solid #1e1e3a;margin-bottom:1rem;">
  <div style="display:flex;align-items:center;gap:10px;">
    <span style="font-size:14px;font-weight:600;color:#94a3b8;">{proj_name}</span>
    <span style="color:#334155;">â€º</span>
    <span style="font-size:14px;font-weight:700;color:#f1f5f9;">
      {active_sb['name'] if active_sb else 'Select a Storyboard'}
    </span>
  </div>
  <div style="font-size:12px;color:#475569;font-family:'JetBrains Mono',monospace;">
    {len(storyboards)} storyboard{'s' if len(storyboards)!=1 else ''}
  </div>
</div>
""", unsafe_allow_html=True)

default_tab = 1 if st.session_state.goto_editor else 0
tabs = st.tabs(["ðŸ“‹ Storyboards", "ðŸŽ¬ Editor", "ðŸ“¦ Export / Import"])

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 0 â€” STORYBOARD LIST
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tabs[0]:
    c_form, _ = st.columns([3, 5])
    with c_form:
        new_sb_name = st.text_input("New storyboard name", placeholder="Untitled Storyboard", key="new_sb_name")
        ca, cb = st.columns(2)
        with ca:
            if st.button("ï¼‹ New Storyboard", key="new_sb_btn", use_container_width=True):
                name = new_sb_name.strip() or f"Storyboard {len(storyboards)+1}"
                sbid = str(uuid.uuid4())
                st.session_state.projects[st.session_state.active_project]["storyboards"][sbid] = {
                    "name": name, "created": datetime.now().strftime("%b %d, %Y"), "scenes": []
                }
                st.session_state.active_storyboard = sbid
                st.session_state.editing_scene     = None
                st.session_state.goto_editor       = True
                st.rerun()
        with cb:
            imp_file = st.file_uploader("Import JSON", type=["json"], key="import_sb", label_visibility="collapsed")
            if imp_file:
                try:
                    raw_imp = json.load(imp_file)
                    sbid    = str(uuid.uuid4())
                    if isinstance(raw_imp, list):
                        sc_imp, nm_imp = normalise_scenes(raw_imp), imp_file.name.replace(".json","")
                    elif isinstance(raw_imp, dict) and "scenes" in raw_imp:
                        sc_imp = normalise_scenes(raw_imp["scenes"])
                        nm_imp = raw_imp.get("name", imp_file.name.replace(".json",""))
                    else:
                        st.error("Unrecognised JSON format."); sc_imp = []; nm_imp = "Imported"
                    if sc_imp:
                        st.session_state.projects[st.session_state.active_project]["storyboards"][sbid] = {
                            "name": nm_imp, "created": datetime.now().strftime("%b %d, %Y"), "scenes": sc_imp
                        }
                        st.session_state.active_storyboard = sbid
                        st.session_state.goto_editor = True
                        st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {e}")

    st.markdown("---")
    if not storyboards:
        st.markdown('<div style="text-align:center;padding:3rem;color:#334155;">No storyboards yet.</div>', unsafe_allow_html=True)
    else:
        for sbid, sb in storyboards.items():
            n_sc = len(sb.get("scenes", [])); is_open = sbid == active_sb_id
            ci, co, cd = st.columns([6, 1.5, 1])
            with ci:
                c = '#93c5fd' if is_open else '#e2e8f0'
                st.markdown(f"""<div style="padding:0.5rem 0;">
                  <div style="font-size:14px;font-weight:600;color:{c};">{'â–¸ ' if is_open else ''}{sb['name']}</div>
                  <div style="font-size:12px;color:#475569;">{sb.get('created','')} Â· {n_sc} scene{'s' if n_sc!=1 else ''}</div>
                </div>""", unsafe_allow_html=True)
            with co:
                if st.button("Open â†’", key=f"open_{sbid}", use_container_width=True):
                    st.session_state.active_storyboard = sbid
                    st.session_state.editing_scene = None
                    st.session_state.goto_editor = True
                    st.rerun()
            with cd:
                if st.button("ðŸ—‘", key=f"del_{sbid}", use_container_width=True):
                    del st.session_state.projects[st.session_state.active_project]["storyboards"][sbid]
                    if active_sb_id == sbid:
                        st.session_state.active_storyboard = None
                        st.session_state.goto_editor = False
                    st.rerun()
            st.markdown('<hr style="margin:4px 0;border-color:#1e1e3a;">', unsafe_allow_html=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 1 â€” EDITOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tabs[default_tab if default_tab == 1 else 1]:
    if not active_sb:
        st.info("Open or create a storyboard from the **Storyboards** tab.")
    else:
        has_scenes = bool(active_sb.get("scenes"))
        with st.expander("âš™ï¸  Generate / Input Controls", expanded=not has_scenes):
            c1, c2 = st.columns(2)
            with c1:
                num_scenes = st.slider("Scenes to generate", 3, 12, 6, key="num_scenes_slider")
                input_type = st.radio("Source", ["Plain Text", "PDF Document"], horizontal=True, key="input_type_radio")
            with c2:
                final_text = ""
                if input_type == "Plain Text":
                    final_text = st.text_area("Paste content", height=130,
                        placeholder="e.g. Working of a Steam Engine, Photosynthesisâ€¦", key="plain_text_input")
                    st.caption(f"{len(final_text)} chars")
                else:
                    pdf_up = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_uploader")
                    if pdf_up:
                        reader = PyPDF2.PdfReader(pdf_up)
                        for pg in reader.pages: final_text += (pg.extract_text() or "")
                        st.success(f"PDF extracted Â· {len(final_text)} chars")
            gc, cc = st.columns(2)
            with gc:
                gen_btn = st.button(f"ðŸš€ Generate {num_scenes} Scenes", key="gen_btn", use_container_width=True)
            with cc:
                clr_btn = st.button("âœ• Clear All Scenes", key="clear_btn", use_container_width=True)
            if clr_btn:
                save_scenes([]); st.session_state.editing_scene = None; st.rerun()
            if gen_btn:
                if not final_text.strip():
                    st.warning("Paste content or upload a PDF first.")
                else:
                    with st.spinner(f"Generating {num_scenes} scenes with Groqâ€¦"):
                        new_sc = generate_scenes_groq(final_text, num_scenes)
                    if new_sc:
                        save_scenes(new_sc); st.session_state.editing_scene = None
                        st.session_state.goto_editor = True
                        st.success(f"âœ“ {len(new_sc)} scenes generated!"); st.rerun()

        scenes = active_sb.get("scenes", [])

        if not scenes:
            st.markdown("""<div style="text-align:center;padding:5rem 2rem;color:#334155;
                border:1px dashed #1e1e3a;border-radius:16px;margin-top:1rem;">
              <div style="font-size:3rem;">ðŸŽž</div>
              <div style="font-size:15px;font-weight:600;color:#475569;margin-top:0.5rem;">No scenes yet</div>
              <div style="font-size:13px;margin-top:0.3rem;">Expand the controls above and hit Generate.</div>
            </div>""", unsafe_allow_html=True)
        else:
            n_images  = sum(1 for s in scenes if s.get("scene_image"))
            n_missing = len(scenes) - n_images

            # â”€â”€ Header bar + Generate All button
            hc1, hc2 = st.columns([3, 1])
            with hc1:
                st.markdown(f"""
                <div style="padding:0.6rem 1rem;background:#0d0d1a;border:1px solid #1e1e3a;
                            border-radius:12px;margin:0.5rem 0 0 0;">
                  <span style="font-size:13px;font-weight:700;color:#e2e8f0;">ðŸ“‹ {active_sb['name']}</span>
                  <span style="font-size:12px;color:#475569;font-family:'JetBrains Mono',monospace;margin-left:16px;">
                    {len(scenes)} SCENES &nbsp;Â·&nbsp; {n_images} IMAGES
                    {f"&nbsp;Â·&nbsp; <span style='color:#f59e0b;'>{n_missing} MISSING</span>" if n_missing else ""}
                  </span>
                </div>""", unsafe_allow_html=True)
            with hc2:
                gen_all_lbl = f"ðŸ–¼ Generate All ({n_missing})" if n_missing else "ðŸ”„ Regen All"
                if st.button(gen_all_lbl, key="gen_all_btn", use_container_width=True):
                    st.session_state.gen_all_images = True
                    st.rerun()

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # â”€â”€ GENERATE ALL FLOW
            if st.session_state.gen_all_images:
                st.session_state.gen_all_images = False
                targets = [i for i, s in enumerate(scenes) if not s.get("scene_image")]
                if not targets:
                    targets = list(range(len(scenes)))  # regen all if all exist
                total    = len(targets)
                prog_bar = st.progress(0, text="Startingâ€¦")
                stat_txt = st.empty()
                for step, idx in enumerate(targets):
                    sc    = scenes[idx]
                    snum  = sc.get("scene_number", idx+1)
                    ttl   = sc.get("title","")
                    stat_txt.markdown(
                        f'<div style="font-size:12px;color:#94a3b8;">Generating Scene {snum:02d} â€” <em>{ttl}</em>â€¦</div>',
                        unsafe_allow_html=True)
                    slot = st.empty()
                    b64  = generate_scene_image(sc, slot)
                    if b64:
                        scenes[idx]["scene_image"] = b64
                        save_scenes(scenes)
                    prog_bar.progress(int((step+1)/total*100),
                                      text=f"Scene {snum:02d} done  ({step+1}/{total})")
                    time.sleep(0.3)
                prog_bar.progress(100, text="âœ“ All images done!")
                stat_txt.success(f"âœ“ {total} images generated!")
                time.sleep(1.2)
                st.rerun()

            # â”€â”€ SCENE CARDS
            for i, sc in enumerate(scenes):
                assets  = get_scene_assets(sc)
                labels  = sc.get("labels", [])
                anim    = sc.get("animation", "").strip()
                vd      = sc.get("visual_description", "").strip()
                narr    = sc.get("narration", "").strip()
                snum    = sc.get("scene_number", i+1)
                title   = sc.get("title", "Untitled")
                img_b64 = sc.get("scene_image")
                editing = (st.session_state.editing_scene == i)

                # Header row
                h1, h2, h3, h4 = st.columns([0.06, 0.52, 0.18, 0.24])
                with h1:
                    st.markdown(f"""<div style="background:linear-gradient(135deg,#2563eb,#7c3aed);
                        color:white;font-size:10px;font-weight:800;letter-spacing:0.1em;
                        padding:5px 8px;border-radius:12px;text-align:center;
                        font-family:'JetBrains Mono',monospace;margin-top:6px;">{snum:02d}</div>""",
                        unsafe_allow_html=True)
                with h2:
                    st.markdown(f'<div style="font-size:15px;font-weight:700;color:#f1f5f9;padding-top:4px;">{title}</div>',
                                unsafe_allow_html=True)
                with h3:
                    if st.button("âœ… Done" if editing else "âœï¸ Edit Scene",
                                 key=f"edit_toggle_{i}", use_container_width=True):
                        st.session_state.editing_scene = None if editing else i
                        st.rerun()
                with h4:
                    gen_img = st.button("ðŸ”„ Regenerate Image" if img_b64 else "ðŸ–¼ Generate Image",
                                        key=f"gen_img_{i}", use_container_width=True)

                # â”€â”€ EDIT MODE
                if editing:
                    st.markdown('<div style="background:#0a0a1a;border:1px solid #2563eb;border-radius:12px;padding:1rem 1.1rem;margin:0.6rem 0;">',
                                unsafe_allow_html=True)
                    ea, eb = st.columns(2)
                    with ea:
                        new_title  = st.text_input("Scene Title", value=title, key=f"e_title_{i}")
                        new_assets = st.text_input("Assets (comma-separated GLB names)", value=", ".join(assets), key=f"e_assets_{i}")
                        new_labels = st.text_input("Labels (comma-separated UI text)", value=", ".join(labels), key=f"e_labels_{i}")
                    with eb:
                        new_narr = st.text_area("Narration", value=narr, height=110, key=f"e_narr_{i}")
                        new_vd   = st.text_area("Visual Description", value=vd, height=75, key=f"e_vd_{i}")
                    new_anim = st.text_area("Animation Logic", value=anim, height=90, key=f"e_anim_{i}")
                    sv, _ = st.columns([1, 4])
                    with sv:
                        if st.button("ðŸ’¾ Save Changes", key=f"save_{i}", use_container_width=True):
                            scenes[i].update({
                                "title":              new_title.strip(),
                                "assets":             [x.strip() for x in new_assets.split(",") if x.strip()],
                                "labels":             [x.strip() for x in new_labels.split(",") if x.strip()],
                                "narration":          new_narr.strip(),
                                "visual_description": new_vd.strip(),
                                "animation":          new_anim.strip(),
                            })
                            save_scenes(scenes)
                            st.session_state.editing_scene = None
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                # â”€â”€ DISPLAY MODE
                else:
                    c_img, c_a, c_b, c_n = st.columns([1, 1, 1, 2])
                    with c_img:
                        if img_b64:
                            st.markdown(clickable_img(img_b64, title, snum), unsafe_allow_html=True)
                        else:
                            st.markdown("""<div style="height:145px;background:#0d0d1a;border:1px dashed #2d2d5a;
                                border-radius:8px;display:flex;align-items:center;justify-content:center;
                                flex-direction:column;gap:6px;">
                              <span style="font-size:2rem;opacity:0.4;">ðŸ–¼</span>
                              <span style="font-size:11px;color:#334155;">No image yet</span>
                            </div>""", unsafe_allow_html=True)
                    with c_a:
                        tags = "".join([pill(a,"#0f1f3d","#60a5fa") for a in assets]) or '<span style="color:#334155;font-size:11px;">â€”</span>'
                        st.markdown(section_box("ðŸ”· 3D Assets (GLB)","#3b82f6",f'<div style="line-height:1.9;">{tags}</div>',"#0d1117","#1e3a5f"), unsafe_allow_html=True)
                    with c_b:
                        ltags = "".join([pill(l,"#0f2d1a","#4ade80") for l in labels]) or '<span style="color:#334155;font-size:11px;">â€”</span>'
                        st.markdown(section_box("ðŸŸ¢ UI Labels","#4ade80",f'<div style="line-height:1.9;">{ltags}</div>',"#0d1a12","#1a3d25"), unsafe_allow_html=True)
                    with c_n:
                        st.markdown(section_box("ðŸŽ™ Narration","#fb7185",
                            f'<div style="font-size:12px;color:#f1f5f9;line-height:1.75;font-style:italic;">{narr or "â€”"}</div>',
                            "#1a0d1a","#3d1a2e",left_accent="#fb7185"), unsafe_allow_html=True)

                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                    c_anim, c_vd = st.columns(2)
                    with c_anim:
                        al2 = [l.strip() for l in anim.replace("\\n","\n").replace("\r\n","\n").split("\n") if l.strip()]
                        steps = "".join([
                            f'<div style="display:flex;gap:8px;margin-bottom:5px;align-items:flex-start;">'
                            f'<span style="min-width:18px;height:18px;border-radius:50%;background:linear-gradient(135deg,#d97706,#f59e0b);color:#000;font-size:9px;font-weight:800;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;">{idx2+1}</span>'
                            f'<span style="font-size:12px;color:#fde68a;line-height:1.5;">{line.lstrip("0123456789.) ") if line[:1].isdigit() else line}</span></div>'
                            for idx2, line in enumerate(al2)
                        ]) or '<span style="color:#334155;font-size:11px;">â€”</span>'
                        st.markdown(section_box("âš¡ Animation Logic (GLB Safe)","#f59e0b",steps,"#1a1400","#3d2e00",left_accent="#f59e0b"), unsafe_allow_html=True)
                    with c_vd:
                        st.markdown(section_box("ðŸŽ¨ Visual Description","#a78bfa",
                            f'<div style="font-size:12px;color:#c4b5fd;line-height:1.7;">{vd or "â€”"}</div>',
                            "#120d1a","#2d1a4a",left_accent="#a78bfa"), unsafe_allow_html=True)

                # â”€â”€ Single image generation
                if gen_img:
                    with st.spinner(f"Generating image for Scene {snum:02d}â€¦"):
                        slot = st.empty()
                        b64  = generate_scene_image(sc, slot)
                    if b64:
                        scenes[i]["scene_image"] = b64
                        save_scenes(scenes)
                        st.success(f"âœ“ Image generated for Scene {snum:02d}!")
                        st.rerun()

                # Delete + divider
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                _, dc = st.columns([8, 1])
                with dc:
                    if st.button("ðŸ—‘ Delete", key=f"del_scene_{i}", use_container_width=True):
                        scenes.pop(i); save_scenes(scenes)
                        if st.session_state.editing_scene == i:
                            st.session_state.editing_scene = None
                        st.rerun()
                st.markdown("""<div style="height:1px;background:linear-gradient(90deg,#2563eb22,#7c3aed55,#2563eb22);
                    margin:0.75rem 0 1.4rem 0;border-radius:2px;"></div>""", unsafe_allow_html=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 2 â€” EXPORT / IMPORT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tabs[2]:
    if not active_sb:
        st.info("Open a storyboard first to export it.")
    else:
        scenes = active_sb.get("scenes", [])
        c_exp, c_imp = st.columns(2)
        with c_exp:
            st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:0.12em;color:#475569;text-transform:uppercase;margin-bottom:0.75rem;">Export</div>', unsafe_allow_html=True)
            if scenes:
                export_scenes = []
                for sc in scenes:
                    e = dict(sc)
                    if "assets" not in e:
                        e["assets"] = e.pop("required_assets", e.pop("models_3d", []))
                    e.pop("required_assets", None); e.pop("models_3d", None)
                    e.setdefault("labels", [])
                    export_scenes.append(e)

                inc_imgs = st.checkbox("Include generated images in JSON export", value=False)
                export_no_img = [dict(e) for e in export_scenes]
                if not inc_imgs:
                    for e in export_no_img: e.pop("scene_image", None)
                payload_out = {"name": active_sb["name"], "created": active_sb.get("created",""), "scenes": export_no_img}
                st.download_button("ðŸ“¥ Download Storyboard JSON",
                    data=json.dumps(payload_out, indent=2),
                    file_name=f"{active_sb['name'].replace(' ','_')}_storyboard.json",
                    mime="application/json", use_container_width=True)

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.markdown('<div style="font-size:10px;color:#475569;margin-bottom:6px;">PDF includes all scene data + images. Requires <code>reportlab</code> and <code>Pillow</code>.</div>', unsafe_allow_html=True)
                if st.button("ðŸ“„ Generate PDF Storyboard", key="gen_pdf_btn", use_container_width=True):
                    with st.spinner("Building PDFâ€¦"):
                        pdf_bytes, pdf_err = generate_storyboard_pdf(active_sb["name"], scenes)
                    if pdf_bytes:
                        st.session_state["_pdf_bytes"] = pdf_bytes
                        st.session_state["_pdf_name"]  = active_sb["name"]
                        st.success(f"âœ“ PDF ready â€” {len(pdf_bytes)//1024} KB"); st.rerun()
                    else:
                        st.error(f"PDF failed: {pdf_err}")

                if "_pdf_bytes" in st.session_state and st.session_state.get("_pdf_name") == active_sb["name"]:
                    st.download_button("â¬‡ï¸ Download PDF",
                        data=st.session_state["_pdf_bytes"],
                        file_name=f"{active_sb['name'].replace(' ','_')}_storyboard.pdf",
                        mime="application/pdf", use_container_width=True)

                st.markdown("---")
                st.markdown("**Scene Table Preview**")
                hdr  = "| # | Title | Assets | Labels | Narration |"
                sep2 = "|---|-------|--------|--------|-----------|"
                rows_md = [
                    f"| {s.get('scene_number','?')} | {s.get('title','')} "
                    f"| {', '.join(get_scene_assets(s))} "
                    f"| {', '.join(s.get('labels',[]))} "
                    f"| {s.get('narration','')[:80]}{'â€¦' if len(s.get('narration',''))>80 else ''} |"
                    for s in scenes
                ]
                st.markdown("\n".join([hdr, sep2] + rows_md))
            else:
                st.info("No scenes to export yet.")

        with c_imp:
            st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:0.12em;color:#475569;text-transform:uppercase;margin-bottom:0.75rem;">Import into Active Storyboard</div>', unsafe_allow_html=True)
            st.caption("Upload a JSON exported from LPVision Studio or a raw scenes array.")
            imp_f = st.file_uploader("Choose JSON", type=["json"], key="export_tab_import")
            if imp_f:
                try:
                    raw_d = json.load(imp_f)
                    if isinstance(raw_d, list):
                        imp_sc = normalise_scenes(raw_d)
                    elif isinstance(raw_d, dict) and "scenes" in raw_d:
                        imp_sc = normalise_scenes(raw_d["scenes"])
                    else:
                        st.error("Unrecognised format."); imp_sc = []
                    if imp_sc:
                        if st.button("â¬† Apply Imported Scenes", key="apply_import"):
                            save_scenes(imp_sc); st.session_state.editing_scene = None
                            st.session_state.goto_editor = True; st.rerun()
                except Exception as e:
                    st.error(f"Parse error: {e}")
