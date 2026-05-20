import streamlit as st
import streamlit.components.v1 as components
import requests, PyPDF2, json, uuid, base64, re, io, time
from datetime import datetime

st.set_page_config(page_title="LPVision Studio", layout="wide", page_icon="🎬")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Playfair+Display:wght@700;800&display=swap');

:root {
  --void: #02020e;
  --card: #07071a;
  --raised: #0c0c22;
  --input: #08081e;
  --b0: #111130;
  --b1: #1a1a40;
  --b2: #242455;
  --blue: #4d7fff;
  --blue-glow: rgba(77,127,255,0.2);
  --purp: #8b5cf6;
  --teal: #14d9c5;
  --amber: #f59e0b;
  --pink: #ec4899;
  --green: #10d981;
  --red: #f43f5e;
  --t0: #eef0ff;
  --t1: #7e87b8;
  --t2: #30335a;
  --font-main: 'Space Grotesk', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  --font-display: 'Playfair Display', serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
  font-family: var(--font-main);
  background: var(--void);
  color: var(--t0);
}

.main { background: var(--void) !important; }
.block-container { padding: 0 1.5rem 3rem 1.5rem !important; max-width: 100% !important; }

section[data-testid="stSidebar"] {
  background: var(--card) !important;
  border-right: 1px solid var(--b0) !important;
  width: 240px !important;
}
section[data-testid="stSidebar"] .block-container { padding: 1rem !important; }

#MainMenu, footer, header { visibility: hidden; }

/* ── Buttons ── */
.stButton > button {
  background: var(--raised) !important;
  color: var(--t1) !important;
  border: 1px solid var(--b1) !important;
  border-radius: 8px !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  font-family: var(--font-main) !important;
  padding: 0.4rem 0.9rem !important;
  transition: all 0.2s ease !important;
  letter-spacing: 0.02em !important;
}
.stButton > button:hover {
  background: var(--b1) !important;
  color: var(--t0) !important;
  border-color: var(--blue) !important;
  box-shadow: 0 0 12px var(--blue-glow) !important;
}
.stDownloadButton > button {
  background: rgba(16,217,129,.07) !important;
  color: var(--green) !important;
  border: 1px solid rgba(16,217,129,.2) !important;
  border-radius: 8px !important;
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
  background: var(--input) !important;
  color: var(--t0) !important;
  border: 1px solid var(--b1) !important;
  border-radius: 8px !important;
  font-family: var(--font-main) !important;
  font-size: 13px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px var(--blue-glow) !important;
}

label {
  color: var(--t2) !important;
  font-size: 10px !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  font-family: var(--font-mono) !important;
}
.stCheckbox label, .stRadio label {
  color: var(--t1) !important;
  font-size: 13px !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  font-family: var(--font-main) !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
  background: var(--raised) !important;
  color: var(--t1) !important;
  border: 1px solid var(--b0) !important;
  border-radius: 8px !important;
  font-size: 13px !important;
  font-family: var(--font-main) !important;
}
.streamlit-expanderContent {
  background: var(--card) !important;
  border: 1px solid var(--b0) !important;
  border-top: none !important;
  border-radius: 0 0 8px 8px !important;
}

[data-testid="stFileUploadDropzone"] {
  background: var(--input) !important;
  border: 1px dashed var(--b1) !important;
  border-radius: 8px !important;
}
.stAlert {
  background: var(--raised) !important;
  border: 1px solid var(--b0) !important;
  border-radius: 8px !important;
}
hr { border-color: var(--b0) !important; }

/* ── Brand ── */
.brand-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0.4rem 0 1.1rem;
  border-bottom: 1px solid var(--b0);
  margin-bottom: 1rem;
}
.brand-logo {
  width: 36px; height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  box-shadow: 0 0 20px rgba(77,127,255,0.35);
}
.brand-name { font-size: 15px; font-weight: 700; color: var(--t0); font-family: var(--font-main); }
.brand-sub { font-size: 9px; font-weight: 500; color: var(--t2); letter-spacing: 0.2em; font-family: var(--font-mono); }

/* ── Topbar ── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--b0);
  margin-bottom: 1rem;
}
.topbar-sb {
  font-size: 16px;
  font-weight: 700;
  color: var(--t0);
  font-family: var(--font-main);
}
.topbar-proj { font-size: 11px; color: var(--t2); font-family: var(--font-mono); }
.topbar-sep { color: var(--t2); margin: 0 4px; }

/* ── Custom Tab Bar ── */
.tab-bar {
  display: flex;
  border-bottom: 1px solid var(--b0);
  margin-bottom: 1rem;
  gap: 0;
}
.tab-item {
  padding: 0.55rem 1.2rem;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  font-family: var(--font-mono);
  transition: all 0.2s;
  color: var(--t2);
  border-bottom: 2px solid transparent;
  user-select: none;
}
.tab-item:hover { color: var(--t1); }
.tab-item.active { color: var(--t0); border-bottom: 2px solid var(--blue); }

/* ── Scene card ── */
.scene-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px; height: 34px;
  border-radius: 9px;
  background: linear-gradient(135deg, #1e3a8a, #4c1d95);
  color: #fff;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 700;
}
.scene-title {
  font-family: var(--font-main);
  font-size: 15px;
  font-weight: 700;
  color: var(--t0);
  line-height: 1.2;
}

/* ── Section panels ── */
.sec-panel {
  background: var(--raised);
  border: 1px solid var(--b0);
  border-radius: 10px;
  padding: 0.7rem 0.85rem;
  height: 100%;
}
.sec-label {
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-family: var(--font-mono);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 5px;
}
.pill {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 16px;
  font-size: 10px;
  font-weight: 600;
  font-family: var(--font-mono);
  margin: 2px 2px 2px 0;
}

/* ── Image placeholder ── */
.img-placeholder {
  height: 155px;
  background: var(--raised);
  border: 1.5px dashed var(--b1);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* ── Narration ── */
.narr-text {
  font-size: 12.5px;
  color: #f0e8ff;
  line-height: 1.9;
  font-style: italic;
  letter-spacing: 0.01em;
}

/* ── Animation steps ── */
.anim-row {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
  align-items: flex-start;
}
.anim-n {
  min-width: 18px; height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #92400e, #f59e0b);
  color: #000;
  font-size: 8px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.anim-txt { font-size: 11.5px; color: #fde68a; line-height: 1.6; }

.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--b1), transparent);
  margin: 0.5rem 0 1rem;
}

/* ── Status bar ── */
.gen-bar {
  background: var(--raised);
  border: 1px solid var(--b1);
  border-radius: 8px;
  padding: 0.5rem 0.85rem;
  font-size: 12px;
  color: var(--t1);
  font-family: var(--font-mono);
}

/* ── Storyboard list ── */
.sb-row { display: flex; align-items: center; padding: 0.5rem 0; }
.sb-name { font-size: 13px; font-weight: 700; color: var(--t0); font-family: var(--font-main); }
.sb-meta { font-size: 10px; color: var(--t2); font-family: var(--font-mono); margin-top: 2px; }
.sb-active .sb-name { color: var(--blue); }

/* ── Auto badge ── */
.auto-badge {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 12px;
  font-size: 9px;
  font-weight: 700;
  font-family: var(--font-mono);
  background: rgba(20,217,197,.1);
  color: var(--teal);
  border: 1px solid rgba(20,217,197,.25);
  margin-left: 6px;
}

/* ── Hide offscreen tab buttons ── */
div[data-testid="stHorizontalBlock"]:has(button[key="tab_btn_0"]),
div[data-testid="stHorizontalBlock"]:has(button[key="tab_btn_1"]),
div[data-testid="stHorizontalBlock"]:has(button[key="tab_btn_2"]) {
  position: absolute !important;
  left: -9999px !important;
  height: 0 !important;
  overflow: hidden !important;
}

/* ── Hide lightbox trigger buttons ── */
div[data-testid="stHorizontalBlock"]:has(button[key="lb_close_btn"]) {
  position: fixed !important;
  left: -9999px !important;
  top: 0 !important;
  width: 1px !important;
  height: 1px !important;
  overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────
def init():
    if "projects" not in st.session_state:
        pid = str(uuid.uuid4())
        st.session_state.projects = {
            pid: {"name": "My First Project", "created": _date(), "storyboards": {}}
        }
    defaults = {
        "active_project": None, "active_sb": None, "active_tab": 0,
        "editing_scene": None, "gen_all": False, "lb_scene": None,
        "go_editor": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if not st.session_state.active_project:
        st.session_state.active_project = list(st.session_state.projects.keys())[0]

def _date(): return datetime.now().strftime("%b %d, %Y")
init()

# ─────────────────────────────────────────────────
# SECRETS
# ─────────────────────────────────────────────────
GROQ_KEY = st.secrets.get("GROQ_API_KEY", None)
GEM_KEY  = st.secrets.get("GEMINI_API_KEY", None)
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEM_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
GEM_MODELS = ["gemini-2.0-flash-preview-image-generation", "gemini-2.5-flash-image-preview"]

# ─────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────
def active_proj():
    return st.session_state.projects.get(st.session_state.active_project, {})

def active_sb():
    p = active_proj(); sid = st.session_state.active_sb
    return p.get("storyboards", {}).get(sid) if sid else None

def assets(sc):
    return sc.get("assets", sc.get("required_assets", sc.get("models_3d", [])))

def save_scenes(scenes):
    pid = st.session_state.active_project; sid = st.session_state.active_sb
    st.session_state.projects[pid]["storyboards"][sid]["scenes"] = scenes

def norm(scenes):
    for s in scenes:
        if "assets" not in s:
            s["assets"] = s.pop("required_assets", s.pop("models_3d", []))
        s.setdefault("labels", [])
        s.setdefault("scene_image", None)
    return scenes

def pill(t, bg, fg):
    return f'<span class="pill" style="background:{bg};color:{fg};">{t}</span>'

def sec(icon, label, color, body, accent=None):
    ac = f"border-left: 3px solid {accent};" if accent else ""
    return (
        f'<div class="sec-panel" style="{ac}">'
        f'<div class="sec-label" style="color:{color};">'
        f'<span>{icon}</span><span>{label}</span></div>{body}</div>'
    )

def anim_html(raw):
    lines = [l.strip() for l in raw.replace("\\n", "\n").split("\n") if l.strip()]
    if not lines:
        return '<span style="color:var(--t2);font-size:11px;">—</span>'
    return "".join(
        f'<div class="anim-row"><div class="anim-n">{i+1}</div>'
        f'<div class="anim-txt">{l.lstrip("0123456789.) ") if l[:1].isdigit() else l}</div></div>'
        for i, l in enumerate(lines)
    )

def fix_cc(s):
    res, ins, esc = [], False, False
    for c in s:
        if esc: res.append(c); esc = False; continue
        if c == '\\': res.append(c); esc = True; continue
        if c == '"': ins = not ins; res.append(c); continue
        if ins:
            if c == '\n': res.append('\\n')
            elif c == '\r': res.append('\\r')
            elif c == '\t': res.append('\\t')
            else: res.append(c)
        else:
            res.append(c)
    return ''.join(res)

def strip_fence(r):
    r = r.strip()
    r = re.sub(r'^```[a-zA-Z]*\n?', '', r)
    return re.sub(r'```$', '', r.strip()).strip()

def image_to_text_via_gemini(b64_img, mime_type="image/jpeg"):
    if not GEM_KEY: return None
    payload = {"contents": [{"parts": [
        {"inline_data": {"mime_type": mime_type, "data": b64_img}},
        {"text": (
            "Carefully extract ALL educational content from this image: "
            "every piece of text, labels, dates, years, proper names, facts, "
            "diagrams, processes, and key concepts visible. "
            "Be thorough and verbatim — this will be used to create a storyboard."
        )}
    ]}]}
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEM_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload, timeout=60
        )
        if r.status_code == 200:
            parts = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
            return " ".join(p.get("text", "") for p in parts if "text" in p)
    except:
        pass
    return None

# ─────────────────────────────────────────────────
# GROQ SCENE GENERATION
# ─────────────────────────────────────────────────
def gen_scenes(text, n, auto_count=False):
    if not GROQ_KEY:
        st.error("Add GROQ_API_KEY to Secrets.")
        return None

    count_instruction = (
        "Decide the optimal number of scenes yourself based on how much content there is. "
        "Use between 4 and 15 scenes — enough to cover every distinct concept without padding."
    ) if auto_count else f"Convert the source material into EXACTLY {n} storyboard scenes."

    sys_prompt = (
        "You are a Senior 3D Instructional Animator and Educational Script Writer.\n"
        f"{count_instruction}\n"
        "Return ONLY a valid JSON array — no markdown, no preamble, no explanation.\n\n"
        "Each JSON object must have EXACTLY these keys:\n\n"
        "  scene_number  : integer (1 to N)\n"
        "  title         : string, 3-6 words, unique per scene\n"
        "  assets        : array of 3-5 snake_case .glb filenames for objects physically shown in THIS scene\n"
        "  labels        : array of 2-4 short annotation strings — only terms visible on screen this scene\n"
        "  animation     : string — numbered steps using \\n between steps, describing 3D movements\n"
        "  visual_description : string — vivid, detailed description for a photorealistic 3D CGI render:\n"
        "    * Specific objects with exact colors, materials (matte, metallic, glass, wood, stone etc)\n"
        "    * Precise spatial arrangement (foreground, midground, background, left/right/center)\n"
        "    * Rich atmospheric lighting (golden hour, cool blue studio, dramatic rim light, etc)\n"
        "    * Camera angle and focal length feel (wide establishing, tight close-up, eye-level, bird-eye)\n"
        "    * Textures, surface details, and environmental mood\n"
        "    * The single most important visual moment to freeze-frame\n"
        "    * DO NOT mention polygon counts, triangle counts, or technical 3D jargon.\n"
        "  narration     : string — VOICE-OVER script for THIS scene only.\n"
        "    FORMAT RULES:\n"
        "    1. Third person past tense — knowledgeable narrator.\n"
        "    2. Always cite exact years, dates, and proper names from the source.\n"
        "    3. 2–3 complete flowing sentences, each adding a distinct new fact.\n"
        "    4. Vivid, accessible language — explain any technical term right after it.\n"
        "    5. Never start with 'In this scene', the scene title, or scene number.\n"
        "    6. Never repeat facts from earlier scenes.\n"
        "    7. No bullet points or numbered lists.\n\n"
        "JSON RULE: no literal newline or tab inside string values — use \\n for line breaks."
    )

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Source material:\n\n{text[:6000]}"}
        ],
        "temperature": 0.2,
        "max_tokens": 4096
    }
    hdr = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post(GROQ_URL, headers=hdr, json=body, timeout=60)
        r.raise_for_status()
        raw = strip_fence(r.json()["choices"][0]["message"]["content"])
        raw = fix_cc(raw)
        data = json.loads(raw)
        if not isinstance(data, list):
            st.error("Unexpected format")
            return None
        return norm(data)
    except requests.HTTPError:
        st.error(f"Groq HTTP {r.status_code}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSON parse error: {e.msg}")
        return None
    except Exception as e:
        st.error(str(e))
        return None

# ─────────────────────────────────────────────────
# IMAGE PROMPT — high quality 3D educational render
# ─────────────────────────────────────────────────
def img_prompt(sc):
    title = sc.get("title", "")
    a = ", ".join(assets(sc))
    lbl = ", ".join(sc.get("labels", []))
    vd = sc.get("visual_description", "")[:400]
    lines = [l.strip() for l in sc.get("animation", "").replace("\\n", "\n").split("\n") if l.strip()]
    key_moment = " | ".join(lines[:3])

    return (
        f"Hyperrealistic 3D CGI educational illustration. "
        f"Scene title: '{title}'. "
        f"Key visual moment: {key_moment}. "
        f"Scene description: {vd}. "
        f"Featured objects: {a}. "
        f"On-screen annotation labels near relevant parts: {lbl}. "
        "Technical render specifications: "
        "Photorealistic PBR materials with subsurface scattering and ray-traced reflections. "
        "Professional 4-point studio lighting with soft key light and dramatic accent rim light. "
        "Deep space dark charcoal-navy void background with subtle ambient occlusion. "
        "Ultra sharp 8K detail, cinematic depth-of-field with bokeh. "
        "16:9 widescreen aspect ratio. "
        "High production value, museum-quality educational visualization. "
        "Color grading: rich, saturated, cinematic with deep shadows and bright highlights. "
        "ABSOLUTELY NO text, NO words, NO watermarks, NO UI overlays. "
        "Pure photorealistic 3D render only, no flat illustration style."
    )

def _quota(code, msg):
    return code == 429 or "quota" in msg.lower() or "rate" in msg.lower()

def gen_gemini(sc):
    if not GEM_KEY: return None, "no_key"
    pay = {
        "contents": [{"parts": [{"text": img_prompt(sc)}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "imageConfig": {"aspectRatio": "16:9", "imageSize": "1K"}
        }
    }
    for m in GEM_MODELS:
        try:
            r = requests.post(
                f"{GEM_BASE.format(m=m)}?key={GEM_KEY}",
                headers={"Content-Type": "application/json"},
                json=pay, timeout=90
            )
            if r.status_code == 200:
                for part in r.json().get("candidates", [{}])[0].get("content", {}).get("parts", []):
                    d = part.get("inlineData", {})
                    if d.get("mimeType", "").startswith("image/"):
                        return d["data"], None
            elif r.status_code in (400, 404):
                continue
            else:
                try: msg = r.json().get("error", {}).get("message", "")
                except: msg = r.text[:150]
                if _quota(r.status_code, msg): return None, "quota"
        except:
            continue
    return None, "failed"

def gen_poll(sc):
    enc = requests.utils.quote(img_prompt(sc)[:700])
    url = (
        f"https://image.pollinations.ai/prompt/{enc}"
        f"?width=1280&height=720&model=flux&nologo=true&enhance=true&seed=-1"
    )
    try:
        r = requests.get(url, timeout=120)
        if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
            return base64.b64encode(r.content).decode(), None
        return None, f"poll_{r.status_code}"
    except Exception as e:
        return None, str(e)

def gen_image(sc, slot=None):
    def log(m):
        if slot: slot.caption(m)
    if GEM_KEY:
        b, e = gen_gemini(sc)
        if b: log("✓ Gemini"); return b
        if e == "quota": log("Gemini quota → Pollinations…")
    b, e = gen_poll(sc)
    if b: log("✓ Pollinations"); return b
    log(f"⚠ {e}"); return None

# ─────────────────────────────────────────────────
# PDF EXPORT
# ─────────────────────────────────────────────────
def make_pdf(name, scenes):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import mm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, Image as RI, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER
        from PIL import Image as PI
    except:
        return None, "reportlab/Pillow missing"

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=15*mm, rightMargin=15*mm, topMargin=12*mm, bottomMargin=12*mm
    )
    C = dict(
        bg=HexColor("#02020e"), card=HexColor("#07071a"), b=HexColor("#111130"),
        blue=HexColor("#4d7fff"), purp=HexColor("#8b5cf6"), green=HexColor("#10d981"),
        amber=HexColor("#f59e0b"), pink=HexColor("#ec4899"), t=HexColor("#eef0ff"),
        mut=HexColor("#30335a")
    )
    S = lambda n, **k: ParagraphStyle(
        n, **{**dict(fontName="Helvetica", fontSize=9, leading=13, textColor=C["t"], spaceAfter=2), **k}
    )
    story = [
        Paragraph("LPVision Studio", S("H", fontSize=20, fontName="Helvetica-Bold")),
        Paragraph(f"{name} · {len(scenes)} Scenes", S("s", fontSize=10, textColor=C["mut"])),
        Paragraph(datetime.now().strftime("%B %d, %Y %H:%M"), S("d", fontSize=8, textColor=C["mut"])),
        HRFlowable(width="100%", thickness=1, color=C["b"], spaceAfter=8)
    ]
    for i, sc in enumerate(scenes):
        snum = sc.get("scene_number", i+1); ttl = sc.get("title", "")
        ast = assets(sc); lbl = sc.get("labels", [])
        anim = sc.get("animation", "").replace("\\n", "\n")
        vd = sc.get("visual_description", ""); narr = sc.get("narration", "")
        b64 = sc.get("scene_image")
        ic = []
        if b64:
            try:
                p = PI.open(io.BytesIO(base64.b64decode(b64)))
                b2 = io.BytesIO(); p.save(b2, "PNG"); b2.seek(0)
                ic.append(RI(b2, width=70*mm, height=39.4*mm))
            except:
                ic.append(Paragraph("[img err]", S("e", fontSize=8, textColor=C["mut"])))
        else:
            ic.append(Paragraph("[ No Image ]", S("ni", fontSize=8, textColor=C["mut"], alignment=TA_CENTER)))
        al = [l.strip() for l in anim.split("\n") if l.strip()]
        data = [[
            [Paragraph(f"{snum:02d}", S("n", fontSize=18, fontName="Helvetica-Bold", textColor=C["blue"], alignment=TA_CENTER, leading=22))],
            ic,
            [Paragraph(f"SCENE {snum:02d}", S("sl", fontSize=6, fontName="Helvetica-Bold", textColor=C["mut"], spaceAfter=3)),
             Paragraph(ttl, S("st", fontSize=11, fontName="Helvetica-Bold", leading=15)), Spacer(1, 4),
             Paragraph("ASSETS", S("al", fontSize=6, fontName="Helvetica-Bold", textColor=C["blue"], spaceAfter=2)),
             Paragraph("  ".join(f"[{a}]" for a in ast) or "—", S("at", fontSize=7, textColor=C["blue"], leading=10)), Spacer(1, 3),
             Paragraph("LABELS", S("ll", fontSize=6, fontName="Helvetica-Bold", textColor=C["green"], spaceAfter=2)),
             Paragraph("  ".join(f"[{l}]" for l in lbl) or "—", S("lt", fontSize=7, textColor=C["green"], leading=10))],
            [Paragraph("VOICE-OVER", S("vl", fontSize=6, fontName="Helvetica-Bold", textColor=C["pink"], spaceAfter=3)),
             Paragraph(narr or "—", S("v", fontSize=8, fontName="Helvetica-Oblique", textColor=HexColor("#fce7f3"), leading=12))],
            [Paragraph("ANIMATION", S("anl", fontSize=6, fontName="Helvetica-Bold", textColor=C["amber"], spaceAfter=3)),
             Paragraph("<br/>".join(f"{k+1}. {l.lstrip('0123456789.) ')}" for k, l in enumerate(al)) or "—",
                       S("an", fontSize=7, textColor=HexColor("#fde68a"), leading=11)),
             Spacer(1, 5),
             Paragraph("VISUAL", S("vdl", fontSize=6, fontName="Helvetica-Bold", textColor=C["purp"], spaceAfter=3)),
             Paragraph(vd or "—", S("vd", fontSize=7, textColor=HexColor("#c4b5fd"), leading=11))]
        ]]
        t = Table(data, colWidths=[13*mm, 70*mm, 52*mm, 60*mm, 59*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C["card"]), ("BOX", (0, 0), (-1, -1), 1, C["b"]),
            ("INNERGRID", (0, 0), (-1, -1), .5, HexColor("#0c0c22")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#07091a")), ("LINEAFTER", (0, 0), (0, -1), 2, C["blue"]),
            ("LINEBEFORE", (3, 0), (3, -1), 2, C["pink"]), ("LINEBEFORE", (4, 0), (4, -1), 2, C["amber"]),
        ]))
        story += [KeepTogether([t]), Spacer(1, 5)]
    story += [
        HRFlowable(width="100%", thickness=.5, color=C["b"], spaceBefore=6),
        Paragraph(
            f"LPVision Studio · {name} · © {datetime.now().year} LearningPad",
            S("ft", fontSize=7, textColor=C["mut"], alignment=TA_CENTER)
        )
    ]
    def bg(c, d):
        c.saveState(); c.setFillColor(C["bg"])
        c.rect(0, 0, landscape(A4)[0], landscape(A4)[1], fill=1, stroke=0); c.restoreState()
    doc.build(story, onFirstPage=bg, onLaterPages=bg)
    buf.seek(0)
    return buf.getvalue(), None

# ─────────────────────────────────────────────────
# LIGHTBOX — self-contained components.html iframe
# Handles close/regen via postMessage → hidden Streamlit buttons
# ─────────────────────────────────────────────────
def show_lightbox():
    sc = st.session_state.lb_scene
    if not sc: return
    b64 = sc.get("scene_image")
    if not b64: return

    snum = sc.get("scene_number", "?")
    title = sc.get("title", "")
    uri = f"data:image/png;base64,{b64}"
    cap = f"Scene {snum:02d} · {title}"
    fname = f"scene_{snum:02d}_{title.replace(' ', '_').lower()}.png"

    # Blur background
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] > .main > .block-container {
        filter: blur(3px) brightness(0.08) !important;
        pointer-events: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Full overlay via components.html — buttons post messages to parent
    overlay_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: rgba(2,2,14,0.98);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    gap: 16px;
    font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
  }}
  .img-wrap {{
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    box-shadow:
      0 0 0 1px rgba(77,127,255,0.25),
      0 0 60px rgba(77,127,255,0.2),
      0 30px 80px rgba(0,0,0,0.8);
  }}
  img {{
    max-width: 88vw;
    max-height: 68vh;
    border-radius: 16px;
    object-fit: contain;
    display: block;
  }}
  .cap {{
    font-size: 11px;
    color: #30335a;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.08em;
    text-align: center;
  }}
  .actions {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
  }}
  .btn {{
    padding: 10px 24px;
    border-radius: 50px;
    font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    border: none;
    transition: all 0.18s ease;
    letter-spacing: 0.04em;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }}
  .btn-dl {{
    background: rgba(16,217,129,0.1);
    color: #10d981;
    border: 1px solid rgba(16,217,129,0.3) !important;
  }}
  .btn-dl:hover {{ background: rgba(16,217,129,0.22); }}
  .btn-regen {{
    background: rgba(77,127,255,0.1);
    color: #4d7fff;
    border: 1px solid rgba(77,127,255,0.28) !important;
  }}
  .btn-regen:hover {{ background: rgba(77,127,255,0.2); }}
  .btn-close {{
    background: rgba(244,63,94,0.1);
    color: #f43f5e;
    border: 1px solid rgba(244,63,94,0.3) !important;
  }}
  .btn-close:hover {{ background: rgba(244,63,94,0.22); }}
</style>
</head>
<body>
  <div class="img-wrap">
    <img src="{uri}" alt="{cap}" />
  </div>
  <div class="cap">{cap}</div>
  <div class="actions">
    <a href="{uri}" download="{fname}" class="btn btn-dl">⬇ Download PNG</a>
    <button class="btn btn-regen" onclick="pm('lb_regen')">🔄 Regenerate</button>
    <button class="btn btn-close" onclick="pm('lb_close')">✕ Close</button>
  </div>
  <script>
    function pm(type) {{
      window.parent.postMessage({{ type: type }}, '*');
    }}
    // Also close on Escape key
    window.parent.document.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') pm('lb_close');
    }});
  </script>
</body>
</html>"""

    components.html(overlay_html, height=750, scrolling=False)

    # Message listener that fires hidden Streamlit buttons
    components.html("""
<script>
(function() {
  function findAndClick(label) {
    var doc = window.parent.document;
    var btns = doc.querySelectorAll('button');
    for (var i = 0; i < btns.length; i++) {
      var txt = btns[i].innerText ? btns[i].innerText.trim() : '';
      if (txt === label) { btns[i].click(); return true; }
    }
    return false;
  }
  window.parent.addEventListener('message', function(e) {
    if (!e.data || !e.data.type) return;
    if (e.data.type === 'lb_close') findAndClick('__lb_close__');
    if (e.data.type === 'lb_regen') findAndClick('__lb_regen__');
  }, false);
})();
</script>
""", height=0, scrolling=False)

    # Hidden close/regen buttons
    hc1, hc2 = st.columns(2)
    with hc1:
        if st.button("__lb_close__", key="lb_close_btn"):
            st.session_state.lb_scene = None
            st.rerun()
    with hc2:
        if st.button("__lb_regen__", key="lb_regen_btn"):
            cur_sb = active_sb()
            if cur_sb:
                scenes = cur_sb.get("scenes", [])
                idx = next(
                    (j for j, s in enumerate(scenes)
                     if s.get("scene_number") == sc.get("scene_number")), None
                )
                if idx is not None:
                    with st.spinner("Regenerating…"):
                        b = gen_image(scenes[idx])
                    if b:
                        scenes[idx]["scene_image"] = b
                        save_scenes(scenes)
                        st.session_state.lb_scene = scenes[idx]
            st.rerun()

# ─────────────────────────────────────────────────
# LIGHTBOX GATE
# ─────────────────────────────────────────────────
if st.session_state.lb_scene:
    show_lightbox()
    st.stop()

# ─────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-wrap">
      <div class="brand-logo">LP</div>
      <div>
        <div class="brand-sub">LPVISION</div>
        <div class="brand-name">Studio</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:9px;font-weight:700;letter-spacing:.2em;color:var(--t2);'
        'text-transform:uppercase;margin-bottom:.5rem;font-family:var(--font-mono);">📁 Projects</div>',
        unsafe_allow_html=True
    )

    with st.expander("＋ New Project"):
        nm = st.text_input("Name", placeholder="e.g. Biology Ch3", key="np_name")
        if st.button("✅ Create", key="np_btn"):
            if nm.strip():
                pid = str(uuid.uuid4())
                st.session_state.projects[pid] = {"name": nm.strip(), "created": _date(), "storyboards": {}}
                st.session_state.active_project = pid
                st.session_state.active_sb = None
                st.rerun()

    for pid, proj in st.session_state.projects.items():
        is_active = pid == st.session_state.active_project
        lbl = f"{'▸ ' if is_active else ''}{proj['name']} [{len(proj.get('storyboards', {}))}]"
        if st.button(lbl, key=f"p_{pid}", use_container_width=True):
            st.session_state.active_project = pid
            st.session_state.active_sb = None
            st.session_state.active_tab = 0
            st.rerun()

    if len(st.session_state.projects) > 1:
        st.markdown("---")
        with st.expander("🗑 Delete Project"):
            st.warning(f"Delete **{active_proj().get('name', '')}**?")
            if st.button("⚠ Confirm Delete", key="dp_btn"):
                del st.session_state.projects[st.session_state.active_project]
                st.session_state.active_project = list(st.session_state.projects.keys())[0]
                st.session_state.active_sb = None
                st.rerun()

    st.markdown("---")
    gk = bool(GROQ_KEY); mk = bool(GEM_KEY)
    st.markdown(f"""
    <div style="font-size:11px;color:var(--t2);line-height:2.2;font-family:var(--font-mono);">
      🤖 Groq &nbsp;
      <span style="color:{'var(--green)' if gk else 'var(--red)'};">{'✓ Connected' if gk else '✗ Missing'}</span><br>
      🖼 Gemini &nbsp;
      <span style="color:{'var(--green)' if mk else 'var(--amber)'};">{'✓ Connected' if mk else '⚠ Fallback'}</span>
    </div>
    <div style="font-size:9px;color:var(--t2);text-align:center;margin-top:12px;font-family:var(--font-mono);">
      © 2026 LearningPad
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────────
proj  = active_proj()
pname = proj.get("name", "Untitled")
sbs   = proj.get("storyboards", {})
sb    = active_sb()
sbid  = st.session_state.active_sb

st.markdown(f"""
<div class="topbar">
  <div style="display:flex;align-items:center;gap:6px;">
    <span style="font-size:13px;">📁</span>
    <span class="topbar-proj">{pname}</span>
    <span class="topbar-sep">›</span>
    <span style="font-size:13px;">🎬</span>
    <span class="topbar-sb">{"Select a Storyboard" if not sb else sb['name']}</span>
  </div>
  <span style="font-size:10px;color:var(--t2);font-family:var(--font-mono);">
    📋 {len(sbs)} storyboard{'s' if len(sbs) != 1 else ''}
  </span>
</div>
""", unsafe_allow_html=True)

# ── Custom tab bar ──
cur_tab = st.session_state.active_tab
TAB_LABELS = [("📋", "STORYBOARDS"), ("🎬", "EDITOR"), ("📦", "EXPORT")]

tab_html = '<div class="tab-bar">'
for i, (icon, label) in enumerate(TAB_LABELS):
    active_cls = "active" if i == cur_tab else ""
    tab_html += (
        f'<div class="tab-item {active_cls}" '
        f'onclick="window.parent.document.querySelector(\'[data-tab-id=\\\"{i}\\\"]\').click()">'
        f'{icon} {label}</div>'
    )
tab_html += '</div>'
st.markdown(tab_html, unsafe_allow_html=True)

# Hidden Streamlit tab trigger buttons
t0, t1, t2 = st.columns(3)
with t0:
    if st.button("TAB0", key="tab_btn_0"): st.session_state.active_tab = 0; st.rerun()
with t1:
    if st.button("TAB1", key="tab_btn_1"): st.session_state.active_tab = 1; st.rerun()
with t2:
    if st.button("TAB2", key="tab_btn_2"): st.session_state.active_tab = 2; st.rerun()

# Tag hidden buttons with data-tab-id attributes for JS
components.html("""
<script>
(function tag(attempt) {
  var doc = window.parent.document;
  var btns = doc.querySelectorAll('button');
  var found = 0;
  btns.forEach(function(b) {
    var t = (b.innerText || '').trim();
    if (t === 'TAB0') { b.setAttribute('data-tab-id', '0'); found++; }
    if (t === 'TAB1') { b.setAttribute('data-tab-id', '1'); found++; }
    if (t === 'TAB2') { b.setAttribute('data-tab-id', '2'); found++; }
  });
  if (found < 3 && attempt < 20) setTimeout(function(){ tag(attempt+1); }, 60);
})(0);
</script>
""", height=0, scrolling=False)

# ════════════════════════════════════════════════════
# TAB 0 — STORYBOARDS
# ════════════════════════════════════════════════════
if cur_tab == 0:
    c1, _ = st.columns([3, 5])
    with c1:
        sbn = st.text_input("🏷 Storyboard name", placeholder="Untitled Storyboard", key="new_sb_name")
        ca, cb = st.columns(2)
        with ca:
            if st.button("➕ New Storyboard", key="nsb", use_container_width=True):
                name = sbn.strip() or f"Storyboard {len(sbs)+1}"
                nid = str(uuid.uuid4())
                st.session_state.projects[st.session_state.active_project]["storyboards"][nid] = {
                    "name": name, "created": _date(), "scenes": []
                }
                st.session_state.active_sb = nid
                st.session_state.editing_scene = None
                st.session_state.active_tab = 1
                st.rerun()
        with cb:
            imp = st.file_uploader("📂 Import JSON", type=["json"], key="imp_sb", label_visibility="collapsed")
            if imp:
                try:
                    raw = json.load(imp); nid = str(uuid.uuid4())
                    if isinstance(raw, list):
                        sc_imp, nm_imp = norm(raw), imp.name.replace(".json", "")
                    elif isinstance(raw, dict) and "scenes" in raw:
                        sc_imp = norm(raw["scenes"]); nm_imp = raw.get("name", imp.name.replace(".json", ""))
                    else:
                        st.error("Bad format"); sc_imp = []; nm_imp = "Imported"
                    if sc_imp:
                        st.session_state.projects[st.session_state.active_project]["storyboards"][nid] = {
                            "name": nm_imp, "created": _date(), "scenes": sc_imp
                        }
                        st.session_state.active_sb = nid
                        st.session_state.active_tab = 1
                        st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {e}")

    st.markdown("---")
    if not sbs:
        st.markdown(
            '<div style="text-align:center;padding:3rem;color:var(--t2);">'
            '🎞 No storyboards yet — create one above.</div>',
            unsafe_allow_html=True
        )
    else:
        for sid, sb_item in sbs.items():
            n_sc = len(sb_item.get("scenes", []))
            n_img = sum(1 for s in sb_item.get("scenes", []) if s.get("scene_image"))
            is_open = sid == sbid
            ci, co, cd = st.columns([6, 1.5, 1])
            with ci:
                cls = "sb-active" if is_open else ""
                st.markdown(f"""
                <div class="sb-row {cls}">
                  <div>
                    <div class="sb-name">{'🎬 ' if is_open else '📋 '}{sb_item['name']}</div>
                    <div class="sb-meta">🗓 {sb_item.get('created','')} · 🎞 {n_sc} scenes · 🖼 {n_img} images</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with co:
                if st.button("🎬 Open", key=f"open_{sid}", use_container_width=True):
                    st.session_state.active_sb = sid
                    st.session_state.editing_scene = None
                    st.session_state.active_tab = 1
                    st.rerun()
            with cd:
                if st.button("🗑", key=f"dsb_{sid}", use_container_width=True):
                    del st.session_state.projects[st.session_state.active_project]["storyboards"][sid]
                    if sbid == sid: st.session_state.active_sb = None
                    st.rerun()
            st.markdown('<hr style="margin:4px 0;border-color:var(--b0);">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 1 — EDITOR
# ════════════════════════════════════════════════════
elif cur_tab == 1:
    sb = active_sb()
    if not sb:
        st.info("🎬 Open or create a storyboard from the **Storyboards** tab.")
    else:
        has = bool(sb.get("scenes"))

        with st.expander("⚙️ Generate / Input Controls", expanded=not has):
            r1, r2 = st.columns(2)
            with r1:
                auto_count = st.checkbox(
                    "🤖 Auto-detect scene count", value=False, key="auto_count",
                    help="Let the AI decide the optimal number of scenes (4–15) based on content."
                )
                if auto_count:
                    st.markdown('<span class="auto-badge">✨ AI decides 4–15 scenes</span>', unsafe_allow_html=True)
                    n_sc = 0
                else:
                    n_sc = st.slider("🎞 Number of scenes", 3, 15, 6, key="nsc")

                src = st.radio(
                    "📂 Source", ["📝 Plain Text", "📄 PDF Document", "🖼 Image"],
                    horizontal=True, key="src_type"
                )
                with_imgs = st.checkbox("🖼 Auto-generate images after scenes", value=False, key="with_imgs")

            with r2:
                txt = ""; src_img_b64 = None; src_img_mime = "image/jpeg"

                if src == "📝 Plain Text":
                    txt = st.text_area(
                        "✏️ Script / content", height=150,
                        placeholder="Paste your lesson, script or topic description here…",
                        key="src_txt"
                    )
                    st.caption(f"📊 {len(txt)} chars")

                elif src == "📄 PDF Document":
                    pf = st.file_uploader("📄 Upload PDF", type=["pdf"], key="pdf_up")
                    if pf:
                        rd = PyPDF2.PdfReader(pf)
                        for pg in rd.pages: txt += (pg.extract_text() or "")
                        st.success(f"✅ {len(txt)} chars extracted from PDF")

                else:
                    img_up = st.file_uploader(
                        "🖼 Upload Image (JPG/PNG/WEBP)",
                        type=["jpg", "jpeg", "png", "webp"], key="img_src_up"
                    )
                    if img_up:
                        src_img_mime = img_up.type or "image/jpeg"
                        img_up.seek(0); src_img_b64 = base64.b64encode(img_up.read()).decode()
                        img_up.seek(0); st.image(img_up, caption="📸 Source image", use_container_width=True)
                        if not GEM_KEY:
                            st.warning("⚠️ GEMINI_API_KEY required for image → scenes.")

            ga, gb = st.columns(2)
            with ga:
                btn_lbl = "🚀 Generate Scenes" if auto_count else f"🚀 Generate {n_sc} Scenes"
                gen_btn = st.button(btn_lbl, key="gen_btn", use_container_width=True)
            with gb:
                clr_btn = st.button("🗑 Clear All Scenes", key="clr_btn", use_container_width=True)

            if clr_btn:
                save_scenes([]); st.session_state.editing_scene = None; st.rerun()

            if gen_btn:
                final_txt = txt.strip()
                if src == "🖼 Image":
                    if not src_img_b64:
                        st.warning("Upload an image first."); final_txt = ""
                    elif not GEM_KEY:
                        st.error("GEMINI_API_KEY required."); final_txt = ""
                    else:
                        with st.spinner("🔍 Extracting content from image via Gemini…"):
                            final_txt = image_to_text_via_gemini(src_img_b64, src_img_mime) or ""
                        if final_txt: st.success(f"✅ {len(final_txt)} chars extracted")
                        else: st.error("Could not extract content from image.")
                if final_txt:
                    with st.spinner("⚙️ Generating scenes…"):
                        new = gen_scenes(final_txt, n_sc, auto_count=auto_count)
                    if new:
                        save_scenes(new); st.session_state.editing_scene = None
                        st.success(f"✅ {len(new)} scenes generated!")
                        if with_imgs:
                            prog = st.progress(0, "🖼 Generating images…")
                            for idx, sc_item in enumerate(new):
                                slot = st.empty(); b = gen_image(sc_item, slot)
                                if b: new[idx]["scene_image"] = b; save_scenes(new)
                                prog.progress(int((idx+1)/len(new)*100), f"Scene {idx+1}/{len(new)}")
                                time.sleep(0.15)
                            prog.progress(100, "✅ All images done!")
                        st.rerun()
                elif src != "🖼 Image":
                    st.warning("Paste content or upload a file first.")

        sb = active_sb()
        scenes = sb.get("scenes", []) if sb else []

        # ── Add scene manually ──
        with st.expander("➕ Add Scene Manually"):
            ma, mb = st.columns(2)
            with ma:
                m_title = st.text_input("🏷 Scene Title", key="m_title", placeholder="e.g. Introduction")
                m_assets = st.text_input("📦 3D Assets (comma-separated GLB names)", key="m_assets", placeholder="object_a.glb, object_b.glb")
                m_labels = st.text_input("🏷 On-Screen Labels (comma-separated)", key="m_labels", placeholder="Label A, Label B")
            with mb:
                m_narr = st.text_area("🎙 Voice-Over / Narration", key="m_narr", height=100,
                    placeholder='"In 1497, Vasco da Gama set sail from Lisbon…"')
                m_vd = st.text_area("🎨 Visual Description", key="m_vd", height=65,
                    placeholder="Describe objects, layout, camera angle, mood…")
            m_anim = st.text_area("⚡ Animation Logic (one step per line)", key="m_anim", height=70,
                placeholder="1. Object A moves into frame\n2. Highlight part B\n3. Camera zooms in")

            st.markdown(
                '<div style="font-size:9px;font-weight:700;letter-spacing:.12em;color:var(--t2);'
                'text-transform:uppercase;margin:.6rem 0 .25rem;font-family:var(--font-mono);">'
                '🖼 Scene Image (optional)</div>',
                unsafe_allow_html=True
            )
            m_img_up = st.file_uploader(
                "Import scene image", type=["jpg", "jpeg", "png", "webp"],
                key="m_img_up", label_visibility="collapsed"
            )
            m_img_b64 = None
            if m_img_up:
                m_img_up.seek(0); m_img_b64 = base64.b64encode(m_img_up.read()).decode()
                m_img_up.seek(0); st.image(m_img_up, caption="Preview", use_container_width=True)

            if st.button("➕ Add This Scene", key="m_add"):
                if m_title.strip():
                    new_sc = {
                        "scene_number": len(scenes)+1, "title": m_title.strip(),
                        "assets": [x.strip() for x in m_assets.split(",") if x.strip()],
                        "labels": [x.strip() for x in m_labels.split(",") if x.strip()],
                        "narration": m_narr.strip(), "visual_description": m_vd.strip(),
                        "animation": m_anim.strip(), "scene_image": m_img_b64
                    }
                    scenes.append(new_sc); save_scenes(scenes); st.success("✅ Scene added!"); st.rerun()
                else:
                    st.warning("Enter a scene title at minimum.")

        if not scenes:
            st.markdown("""
            <div style="text-align:center;padding:4rem 2rem;color:var(--t2);
                border:1.5px dashed var(--b1);border-radius:14px;margin-top:.5rem;background:var(--card);">
              <div style="font-size:2.5rem;margin-bottom:.5rem;">🎞</div>
              <div style="font-size:14px;font-weight:700;color:var(--t1);font-family:var(--font-main);">No scenes yet</div>
              <div style="font-size:12px;margin-top:.4rem;">Use the Generate controls above, or add scenes manually.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            n_img = sum(1 for s in scenes if s.get("scene_image"))
            n_miss = len(scenes) - n_img

            hc1, hc2 = st.columns([3, 1])
            with hc1:
                miss_html = (
                    f" &nbsp;·&nbsp; <span style='color:var(--amber);'>⚠ {n_miss} missing</span>"
                    if n_miss else ""
                )
                st.markdown(f"""
                <div style="padding:.6rem .95rem;background:var(--card);border:1px solid var(--b0);
                    border-radius:9px;margin-bottom:.6rem;">
                  <span style="font-size:14px;font-weight:700;color:var(--t0);font-family:var(--font-main);">
                    🎬 {sb['name']}
                  </span>
                  <span style="font-size:10px;color:var(--t2);font-family:var(--font-mono);margin-left:12px;">
                    🎞 {len(scenes)} scenes &nbsp;·&nbsp; 🖼 {n_img} images{miss_html}
                  </span>
                </div>
                """, unsafe_allow_html=True)
            with hc2:
                lbl = f"🖼 Generate All ({n_miss})" if n_miss else "🔄 Regen All Images"
                if st.button(lbl, key="gen_all", use_container_width=True):
                    st.session_state.gen_all = True; st.rerun()

            if st.session_state.gen_all:
                st.session_state.gen_all = False
                targets = [i for i, s in enumerate(scenes) if not s.get("scene_image")] or list(range(len(scenes)))
                bar = st.progress(0, "Starting…"); stat = st.empty()
                for step, idx in enumerate(targets):
                    sc = scenes[idx]; sn = sc.get("scene_number", idx+1)
                    stat.markdown(
                        f'<div class="gen-bar">🖼 Generating Scene {sn:02d} — {sc.get("title","")}…</div>',
                        unsafe_allow_html=True
                    )
                    sl = st.empty(); b = gen_image(sc, sl)
                    if b: scenes[idx]["scene_image"] = b; save_scenes(scenes)
                    bar.progress(int((step+1)/len(targets)*100), f"Scene {sn:02d} ({step+1}/{len(targets)})")
                    time.sleep(0.2)
                bar.progress(100, "✅ Done!"); stat.success(f"✅ {len(targets)} images generated!")
                time.sleep(1.2); st.rerun()

            # ── SCENE CARDS ──
            for i, sc in enumerate(scenes):
                ast_list = assets(sc); lbl_list = sc.get("labels", [])
                anim_raw = sc.get("animation", "").strip()
                vd_txt = sc.get("visual_description", "").strip()
                narr_txt = sc.get("narration", "").strip()
                snum = sc.get("scene_number", i+1); title = sc.get("title", "Untitled")
                img_b64 = sc.get("scene_image"); editing = st.session_state.editing_scene == i

                with st.container():
                    h1, h2, h3, h4 = st.columns([.06, .5, .2, .24])
                    with h1:
                        st.markdown(
                            f'<div class="scene-num" style="margin-top:5px;">{snum:02d}</div>',
                            unsafe_allow_html=True
                        )
                    with h2:
                        st.markdown(
                            f'<div class="scene-title" style="padding-top:6px;">🎞 {title}</div>',
                            unsafe_allow_html=True
                        )
                    with h3:
                        if st.button("✅ Done" if editing else "✏️ Edit", key=f"edit_{i}", use_container_width=True):
                            st.session_state.editing_scene = None if editing else i; st.rerun()
                    with h4:
                        gen_img = st.button(
                            "🔄 Regen Image" if img_b64 else "🖼 Generate Image",
                            key=f"gi_{i}", use_container_width=True
                        )

                    # ── EDIT MODE ──
                    if editing:
                        st.markdown(
                            '<div style="background:rgba(37,68,140,.08);border:1px solid var(--blue);'
                            'border-radius:10px;padding:.85rem 1rem;margin:.4rem 0;">',
                            unsafe_allow_html=True
                        )
                        ea, eb = st.columns(2)
                        with ea:
                            nt = st.text_input("🏷 Title", value=title, key=f"et_{i}")
                            na = st.text_input("📦 Assets", value=", ".join(ast_list), key=f"ea_{i}")
                            nl = st.text_input("🏷 Labels", value=", ".join(lbl_list), key=f"el_{i}")
                        with eb:
                            nn = st.text_area("🎙 Voice-Over", value=narr_txt, height=115, key=f"en_{i}",
                                help='Preserve exact dates & names.')
                            nv = st.text_area("🎨 Visual Description", value=vd_txt, height=70, key=f"ev_{i}",
                                help="Objects, layout, camera angle, mood — no tech jargon.")
                        nanim = st.text_area("⚡ Animation Logic", value=anim_raw, height=80, key=f"ean_{i}")

                        st.markdown(
                            '<div style="font-size:9px;font-weight:700;letter-spacing:.12em;color:var(--t2);'
                            'text-transform:uppercase;margin:.5rem 0 .2rem;font-family:var(--font-mono);">'
                            '🖼 Import / Replace Scene Image</div>',
                            unsafe_allow_html=True
                        )
                        edit_img_up = st.file_uploader(
                            "Replace scene image", type=["jpg", "jpeg", "png", "webp"],
                            key=f"eimg_{i}", label_visibility="collapsed"
                        )
                        new_img_b64 = img_b64
                        if edit_img_up:
                            edit_img_up.seek(0); new_img_b64 = base64.b64encode(edit_img_up.read()).decode()
                            edit_img_up.seek(0); st.image(edit_img_up, caption="New image preview", use_container_width=True)

                        sv, sr, _ = st.columns([1, 1, 3])
                        with sv:
                            if st.button("💾 Save", key=f"save_{i}", use_container_width=True):
                                scenes[i].update({
                                    "title": nt.strip(),
                                    "assets": [x.strip() for x in na.split(",") if x.strip()],
                                    "labels": [x.strip() for x in nl.split(",") if x.strip()],
                                    "narration": nn.strip(), "visual_description": nv.strip(),
                                    "animation": nanim.strip(), "scene_image": new_img_b64
                                })
                                save_scenes(scenes); st.session_state.editing_scene = None; st.rerun()
                        with sr:
                            if img_b64 and st.button("🗑 Clear Img", key=f"clrimg_{i}", use_container_width=True):
                                scenes[i]["scene_image"] = None; save_scenes(scenes); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

                    # ── DISPLAY MODE ──
                    else:
                        ci_col, ca_col, cb_col, cn_col = st.columns([1, 1, 1, 2])
                        with ci_col:
                            if img_b64:
                                if st.button("🔍 View Full", key=f"lb_{i}", use_container_width=True):
                                    st.session_state.lb_scene = sc; st.rerun()
                                st.markdown(
                                    f'<img src="data:image/png;base64,{img_b64}" '
                                    f'style="width:100%;border-radius:9px;border:1px solid var(--b1);'
                                    f'margin-top:4px;cursor:zoom-in;"/>',
                                    unsafe_allow_html=True
                                )
                                st.download_button(
                                    "⬇ Save PNG", data=base64.b64decode(img_b64),
                                    file_name=f"scene_{snum:02d}.png", mime="image/png",
                                    key=f"dl_{i}", use_container_width=True
                                )
                            else:
                                st.markdown("""
                                <div class="img-placeholder">
                                  <span style="font-size:2rem;opacity:.18;">🖼</span>
                                  <span style="font-size:10px;color:var(--t2);">No image yet</span>
                                  <span style="font-size:9px;color:var(--t2);">Import or generate</span>
                                </div>
                                """, unsafe_allow_html=True)
                                quick_img = st.file_uploader(
                                    "📂 Import image", type=["jpg", "jpeg", "png", "webp"],
                                    key=f"qimp_{i}", label_visibility="collapsed"
                                )
                                if quick_img:
                                    quick_img.seek(0)
                                    scenes[i]["scene_image"] = base64.b64encode(quick_img.read()).decode()
                                    save_scenes(scenes); st.rerun()

                        with ca_col:
                            tags = "".join(pill(a, "#0a1f45", "#60a5fa") for a in ast_list) or \
                                   '<span style="color:var(--t2);font-size:11px;">—</span>'
                            st.markdown(
                                sec("📦", "3D Assets · GLB", "#4d7fff", f'<div style="line-height:2.1;">{tags}</div>'),
                                unsafe_allow_html=True
                            )

                        with cb_col:
                            ltags = "".join(pill(l, "#061f14", "#10d981") for l in lbl_list) or \
                                    '<span style="color:var(--t2);font-size:11px;">—</span>'
                            st.markdown(
                                sec("🏷", "On-Screen Labels", "#10d981", f'<div style="line-height:2.1;">{ltags}</div>'),
                                unsafe_allow_html=True
                            )

                        with cn_col:
                            st.markdown(
                                sec("🎙", "Voice-Over / Narration", "#ec4899",
                                    f'<div class="narr-text">{narr_txt or "—"}</div>', accent="#ec4899"),
                                unsafe_allow_html=True
                            )

                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                        ca2, cb2 = st.columns(2)
                        with ca2:
                            st.markdown(
                                sec("⚡", "Animation Steps", "#f59e0b", anim_html(anim_raw), accent="#f59e0b"),
                                unsafe_allow_html=True
                            )
                        with cb2:
                            st.markdown(
                                sec("🎨", "Visual Description", "#8b5cf6",
                                    f'<div style="font-size:12px;color:#c4b5fd;line-height:1.75;">{vd_txt or "—"}</div>',
                                    accent="#8b5cf6"),
                                unsafe_allow_html=True
                            )

                    if gen_img:
                        with st.spinner(f"🖼 Generating image for Scene {snum:02d}…"):
                            sl = st.empty(); b = gen_image(sc, sl)
                        if b:
                            scenes[i]["scene_image"] = b; save_scenes(scenes)
                            st.success(f"✅ Scene {snum:02d} image done!"); st.rerun()

                    st.markdown("<div style='height:3px;'></div>", unsafe_allow_html=True)
                    _, dc = st.columns([8, 1])
                    with dc:
                        if st.button("🗑", key=f"dsc_{i}", use_container_width=True):
                            scenes.pop(i); save_scenes(scenes)
                            if st.session_state.editing_scene == i:
                                st.session_state.editing_scene = None
                            st.rerun()
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 2 — EXPORT
# ════════════════════════════════════════════════════
elif cur_tab == 2:
    sb = active_sb()
    if not sb:
        st.info("📦 Open a storyboard first.")
    else:
        scenes = sb.get("scenes", [])
        ex, im = st.columns(2)
        with ex:
            st.markdown(
                '<div style="font-size:10px;font-weight:700;letter-spacing:.15em;color:var(--t2);'
                'text-transform:uppercase;margin-bottom:.7rem;font-family:var(--font-mono);">📤 Export</div>',
                unsafe_allow_html=True
            )
            if scenes:
                inc = st.checkbox("🖼 Include images in JSON", value=False)
                out = []
                for s in scenes:
                    e = dict(s)
                    if "assets" not in e: e["assets"] = e.pop("required_assets", e.pop("models_3d", []))
                    e.pop("required_assets", None); e.pop("models_3d", None)
                    e.setdefault("labels", [])
                    if not inc: e.pop("scene_image", None)
                    out.append(e)
                st.download_button(
                    "📥 Download JSON",
                    data=json.dumps({"name": sb["name"], "created": sb.get("created", ""), "scenes": out}, indent=2),
                    file_name=f"{sb['name'].replace(' ', '_')}_storyboard.json",
                    mime="application/json", use_container_width=True
                )
                st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
                if st.button("📄 Generate PDF", key="gen_pdf", use_container_width=True):
                    with st.spinner("📄 Building PDF…"):
                        pb, pe = make_pdf(sb["name"], scenes)
                    if pb:
                        st.session_state["_pdf"] = pb; st.session_state["_pdfn"] = sb["name"]
                        st.success(f"✅ PDF ready — {len(pb)//1024} KB"); st.rerun()
                    else:
                        st.error(f"PDF error: {pe}")
                if "_pdf" in st.session_state and st.session_state.get("_pdfn") == sb["name"]:
                    st.download_button(
                        "⬇️ Download PDF", data=st.session_state["_pdf"],
                        file_name=f"{sb['name'].replace(' ', '_')}.pdf",
                        mime="application/pdf", use_container_width=True
                    )
                st.markdown("---")
                hdr = "| # | Title | Assets | Labels | Voice-Over |"
                sep = "|---|-------|--------|--------|------------|"
                rows = [
                    f"| {s.get('scene_number','?')} | {s.get('title','')} | "
                    f"{', '.join(assets(s))} | {', '.join(s.get('labels',[]))} | "
                    f"{s.get('narration','')[:80]}{'…' if len(s.get('narration',''))>80 else ''} |"
                    for s in scenes
                ]
                st.markdown("\n".join([hdr, sep] + rows))
            else:
                st.info("No scenes yet.")

        with im:
            st.markdown(
                '<div style="font-size:10px;font-weight:700;letter-spacing:.15em;color:var(--t2);'
                'text-transform:uppercase;margin-bottom:.7rem;font-family:var(--font-mono);">📥 Import</div>',
                unsafe_allow_html=True
            )
            st.caption("Upload a JSON to load scenes into the active storyboard.")
            imf = st.file_uploader("📂 Choose JSON", type=["json"], key="impf")
            if imf:
                try:
                    rd = json.load(imf)
                    if isinstance(rd, list): isc = norm(rd)
                    elif isinstance(rd, dict) and "scenes" in rd: isc = norm(rd["scenes"])
                    else: st.error("Bad format"); isc = []
                    if isc and st.button("⬆ Apply Imported Scenes", key="apply_imp"):
                        save_scenes(isc); st.rerun()
                except Exception as e:
                    st.error(f"Parse error: {e}")
