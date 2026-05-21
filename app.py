import streamlit as st
import streamlit.components.v1 as components
import requests, PyPDF2, json, uuid, base64, re, io, time
from datetime import datetime

st.set_page_config(page_title="LPVision Studio", layout="wide", page_icon="🎬")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&family=Cormorant+Garamond:wght@600;700&display=swap');

:root {
  --bg:       #060610;
  --card:     #0d0d20;
  --raised:   #111128;
  --border:   #1e1e3a;
  --border2:  #2a2a50;
  --blue:     #5b8cff;
  --blue-dim: rgba(91,140,255,0.12);
  --blue-glow:rgba(91,140,255,0.25);
  --teal:     #00d4b4;
  --purple:   #9f7aea;
  --amber:    #f6ad55;
  --rose:     #fc8181;
  --green:    #48bb78;
  --t0:       #e8ecff;
  --t1:       #8891c4;
  --t2:       #3a3d6b;
  --font:     'DM Sans', sans-serif;
  --mono:     'DM Mono', monospace;
  --display:  'Cormorant Garamond', serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
  font-family: var(--font);
  background: var(--bg);
  color: var(--t0);
}

.main { background: var(--bg) !important; }
.block-container { padding: 0 1.4rem 3rem 1.4rem !important; max-width: 100% !important; }

section[data-testid="stSidebar"] {
  background: var(--card) !important;
  border-right: 1px solid var(--border) !important;
  width: 220px !important;
}
section[data-testid="stSidebar"] .block-container { padding: 0.85rem !important; }

#MainMenu, footer, header { visibility: hidden; }

/* Buttons */
.stButton > button {
  background: var(--raised) !important;
  color: var(--t1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 7px !important;
  font-size: 11.5px !important;
  font-weight: 600 !important;
  font-family: var(--font) !important;
  padding: 0.38rem 0.85rem !important;
  transition: all 0.18s !important;
}
.stButton > button:hover {
  background: var(--blue-dim) !important;
  color: var(--t0) !important;
  border-color: var(--blue) !important;
  box-shadow: 0 0 14px var(--blue-glow) !important;
}
.stDownloadButton > button {
  background: rgba(72,187,120,.07) !important;
  color: var(--green) !important;
  border: 1px solid rgba(72,187,120,.2) !important;
  border-radius: 7px !important;
}
.stDownloadButton > button:hover {
  background: rgba(72,187,120,.14) !important;
}

/* Inputs */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
  background: var(--card) !important;
  color: var(--t0) !important;
  border: 1px solid var(--border) !important;
  border-radius: 7px !important;
  font-family: var(--font) !important;
  font-size: 13px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 2px var(--blue-dim) !important;
  outline: none !important;
}
label {
  color: var(--t2) !important;
  font-size: 10px !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  font-family: var(--mono) !important;
}
.stCheckbox label, .stRadio label {
  color: var(--t1) !important;
  font-size: 12px !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  font-family: var(--font) !important;
}

/* Expanders */
.streamlit-expanderHeader {
  background: var(--raised) !important;
  color: var(--t1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 7px !important;
  font-size: 12px !important;
  font-family: var(--font) !important;
}
.streamlit-expanderContent {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 7px 7px !important;
}

[data-testid="stFileUploadDropzone"] {
  background: var(--card) !important;
  border: 1px dashed var(--border2) !important;
  border-radius: 7px !important;
}
.stAlert {
  background: var(--raised) !important;
  border: 1px solid var(--border) !important;
  border-radius: 7px !important;
}
hr { border-color: var(--border) !important; }

/* Slider */
.stSlider [data-baseweb="slider"] { padding: 0 !important; }

/* Brand */
.brand-wrap {
  display: flex; align-items: center; gap: 9px;
  padding: 0.3rem 0 1rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.9rem;
}
.brand-logo {
  width: 32px; height: 32px; border-radius: 8px;
  background: linear-gradient(135deg, #1e40af, #6d28d9);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 11px; font-weight: 700;
  color: #fff; box-shadow: 0 0 18px rgba(91,140,255,0.3);
}
.brand-name { font-size: 14px; font-weight: 700; color: var(--t0); }
.brand-sub  { font-size: 8px; color: var(--t2); letter-spacing: .2em; font-family: var(--mono); }

/* Topbar */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.55rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.85rem;
}
.topbar-title { font-size: 15px; font-weight: 700; color: var(--t0); }
.topbar-meta  { font-size: 10px; color: var(--t2); font-family: var(--mono); }

/* Tab bar */
.tab-bar {
  display: flex; gap: 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.9rem;
}
.tab-item {
  padding: 0.48rem 1.1rem;
  font-size: 10.5px; font-weight: 700; letter-spacing: .07em;
  text-transform: uppercase; cursor: pointer;
  font-family: var(--mono); transition: all .18s;
  color: var(--t2); border-bottom: 2px solid transparent;
  user-select: none; display: flex; align-items: center; gap: 5px;
}
.tab-item:hover { color: var(--t1); }
.tab-item.active { color: var(--t0); border-bottom-color: var(--blue); }

/* Scene card */
.scene-badge {
  width: 30px; height: 30px; border-radius: 8px;
  background: linear-gradient(135deg, #1e3a8a, #4c1d95);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--mono); font-size: 11px; font-weight: 700; color: #fff;
}
.scene-title {
  font-size: 14px; font-weight: 700; color: var(--t0);
  font-family: var(--font); line-height: 1.25;
}

/* Info panels */
.info-panel {
  background: var(--raised); border: 1px solid var(--border);
  border-radius: 9px; padding: 0.65rem 0.8rem; height: 100%;
}
.panel-label {
  font-size: 8.5px; font-weight: 700; letter-spacing: .18em;
  text-transform: uppercase; font-family: var(--mono);
  margin-bottom: 7px; display: flex; align-items: center; gap: 4px;
}
.chip {
  display: inline-block; padding: 2px 9px; border-radius: 14px;
  font-size: 10px; font-weight: 600; font-family: var(--mono);
  margin: 2px 2px 2px 0; line-height: 1.6;
}
.img-placeholder {
  height: 145px; background: var(--raised);
  border: 1.5px dashed var(--border2); border-radius: 9px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 5px;
}
.narr-text {
  font-size: 12px; color: #d4d8ff;
  line-height: 1.75; font-style: italic;
}
.anim-step {
  display: flex; gap: 7px; margin-bottom: 5px; align-items: flex-start;
}
.anim-dot {
  min-width: 16px; height: 16px; border-radius: 50%;
  background: linear-gradient(135deg, #92400e, #f59e0b);
  color: #000; font-size: 7.5px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 2px;
}
.anim-text { font-size: 11px; color: #fde68a; line-height: 1.6; }
.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
  margin: 0.4rem 0 0.9rem;
}
.stat-bar {
  background: var(--raised); border: 1px solid var(--border);
  border-radius: 7px; padding: 0.45rem 0.8rem;
  font-size: 11.5px; color: var(--t1); font-family: var(--mono);
}
.sb-name { font-size: 13px; font-weight: 700; color: var(--t0); }
.sb-meta { font-size: 9.5px; color: var(--t2); font-family: var(--mono); margin-top: 1px; }

/* Hidden tab buttons */
div[data-testid="stHorizontalBlock"]:has(button[key="tab_btn_0"]),
div[data-testid="stHorizontalBlock"]:has(button[key="tab_btn_1"]),
div[data-testid="stHorizontalBlock"]:has(button[key="tab_btn_2"]) {
  position: absolute !important; left: -9999px !important;
  height: 0 !important; overflow: hidden !important;
  pointer-events: none !important;
}
div[data-testid="stHorizontalBlock"]:has(button[key="lb_close_btn"]) {
  position: fixed !important; left: -9999px !important;
  top: 0 !important; width: 1px !important; height: 1px !important;
  overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ───────────────────────────────
def init():
    if "projects" not in st.session_state:
        pid = str(uuid.uuid4())
        st.session_state.projects = {
            pid: {"name": "My First Project", "created": _date(), "storyboards": {}}
        }
    defaults = {
        "active_project": None, "active_sb": None, "active_tab": 0,
        "editing_scene": None, "gen_all": False, "lb_scene": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if not st.session_state.active_project:
        st.session_state.active_project = list(st.session_state.projects.keys())[0]

def _date(): return datetime.now().strftime("%b %d, %Y")
init()

# ─── SECRETS ────────────────────────────────────
GROQ_KEY = st.secrets.get("GROQ_API_KEY", None)
GEM_KEY  = st.secrets.get("GEMINI_API_KEY", None)
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEM_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
GEM_MODELS = ["gemini-2.0-flash-preview-image-generation", "gemini-2.5-flash-image-preview"]

# ─── HELPERS ────────────────────────────────────
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

def chip(t, bg, fg):
    return f'<span class="chip" style="background:{bg};color:{fg};">{t}</span>'

def panel(icon, label, color, body, accent=None):
    ac = f"border-left:3px solid {accent};" if accent else ""
    return (
        f'<div class="info-panel" style="{ac}">'
        f'<div class="panel-label" style="color:{color};">'
        f'<span>{icon}</span><span>{label}</span></div>{body}</div>'
    )

def anim_html(raw):
    lines = [l.strip() for l in raw.replace("\\n", "\n").split("\n") if l.strip()]
    if not lines:
        return '<span style="color:var(--t2);font-size:11px;">—</span>'
    out = ""
    for i, l in enumerate(lines):
        txt = re.sub(r'^[\d]+[.)]\s*', '', l)
        out += (
            f'<div class="anim-step">'
            f'<div class="anim-dot">{i+1}</div>'
            f'<div class="anim-text">{txt}</div></div>'
        )
    return out

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
        else: res.append(c)
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
            "Extract ALL educational content from this image: every piece of text, labels, "
            "dates, years, proper names, facts, diagrams, processes, and key concepts visible. "
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
    except: pass
    return None

# ─── GROQ SCENE GENERATION ───────────────────────
def gen_scenes(text, n, auto_count=False):
    if not GROQ_KEY:
        st.error("Add GROQ_API_KEY to Secrets.")
        return None

    count_instruction = (
        "Decide the optimal number of scenes yourself based on content richness. "
        "Use between 4 and 15 scenes."
    ) if auto_count else f"Generate EXACTLY {n} storyboard scenes."

    sys_prompt = (
        "You are a Senior 3D Instructional Animator and Educational Script Writer.\n"
        f"{count_instruction}\n"
        "Return ONLY a valid JSON array — no markdown, no explanation.\n\n"
        "Each JSON object must have EXACTLY these keys:\n"
        "  scene_number  : integer\n"
        "  title         : string, 3-6 words\n"
        "  assets        : array of 3-5 snake_case .glb filenames\n"
        "  labels        : array of 2-4 short annotation strings\n"
        "  animation     : numbered steps using \\n between them\n"
        "  visual_description : vivid 3D CGI render description — objects, materials, lighting, camera angle, mood\n"
        "  narration     : STRICT RULES — \n"
        "    * Write EXACTLY 1-2 short sentences.\n"
        "    * Use ONLY words, facts, names, and dates that appear verbatim in the source material provided.\n"
        "    * Do NOT add any information, context, explanations, or facts not present in the source.\n"
        "    * Do NOT paraphrase or expand — stay as close to the source wording as possible.\n"
        "    * Do NOT start with 'In this scene', the title, or scene number.\n"
        "    * No bullet points.\n\n"
        "JSON RULE: no literal newlines inside string values — use \\n."
    )

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user",   "content": f"Source material:\n\n{text[:6000]}"}
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
            st.error("Unexpected format"); return None
        return norm(data)
    except requests.HTTPError:
        st.error(f"Groq HTTP {r.status_code}"); return None
    except json.JSONDecodeError as e:
        st.error(f"JSON parse error: {e.msg}"); return None
    except Exception as e:
        st.error(str(e)); return None

# ─── IMAGE PROMPT ────────────────────────────────
def img_prompt(sc):
    title = sc.get("title", "")
    a  = ", ".join(assets(sc))
    lbl = ", ".join(sc.get("labels", []))
    vd = sc.get("visual_description", "")[:500]
    lines = [l.strip() for l in sc.get("animation", "").replace("\\n", "\n").split("\n") if l.strip()]
    moment = " | ".join(lines[:2])

    return (
        f"Photorealistic 3D CGI educational visualization. "
        f"Topic: '{title}'. Key moment: {moment}. "
        f"Scene: {vd}. "
        f"Render requirements: "
        "Ultra-high-detail PBR materials with realistic subsurface scattering. "
        "Professional cinematic lighting — warm key light, cool fill, dramatic blue rim light. "
        "Deep space dark background, subtle nebula-like ambient glow. "
        "Physically accurate shadows and reflections. "
        "Macro-lens quality 8K detail. "
        "Museum-quality scientific visualization aesthetic. "
        "Rich, saturated color palette, deep contrast. "
        "16:9 cinematic aspect ratio. "
        "No text, no watermarks, no UI, no flat illustration — pure photorealistic 3D render."
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
        except: continue
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

# ─── PDF EXPORT ──────────────────────────────────
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
    except: return None, "reportlab/Pillow missing"

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
        leftMargin=14*mm, rightMargin=14*mm, topMargin=11*mm, bottomMargin=11*mm)
    C = dict(
        bg=HexColor("#060610"), card=HexColor("#0d0d20"), b=HexColor("#1e1e3a"),
        blue=HexColor("#5b8cff"), purp=HexColor("#9f7aea"), green=HexColor("#48bb78"),
        amber=HexColor("#f6ad55"), rose=HexColor("#fc8181"), t=HexColor("#e8ecff"),
        mut=HexColor("#3a3d6b")
    )
    S = lambda n, **k: ParagraphStyle(
        n, **{**dict(fontName="Helvetica", fontSize=9, leading=13, textColor=C["t"], spaceAfter=2), **k}
    )
    story = [
        Paragraph("LPVision Studio", S("H", fontSize=18, fontName="Helvetica-Bold")),
        Paragraph(f"{name} · {len(scenes)} Scenes", S("s", fontSize=9, textColor=C["mut"])),
        Paragraph(datetime.now().strftime("%B %d, %Y %H:%M"), S("d", fontSize=7, textColor=C["mut"])),
        HRFlowable(width="100%", thickness=1, color=C["b"], spaceAfter=7)
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
                ic.append(RI(b2, width=68*mm, height=38*mm))
            except: ic.append(Paragraph("[img err]", S("e", fontSize=8, textColor=C["mut"])))
        else:
            ic.append(Paragraph("[ No Image ]", S("ni", fontSize=8, textColor=C["mut"], alignment=TA_CENTER)))
        al = [l.strip() for l in anim.split("\n") if l.strip()]
        data = [[
            [Paragraph(f"{snum:02d}", S("n", fontSize=17, fontName="Helvetica-Bold", textColor=C["blue"], alignment=TA_CENTER, leading=22))],
            ic,
            [Paragraph(f"SCENE {snum:02d}", S("sl", fontSize=5.5, fontName="Helvetica-Bold", textColor=C["mut"], spaceAfter=2)),
             Paragraph(ttl, S("st", fontSize=10, fontName="Helvetica-Bold", leading=14)), Spacer(1, 3),
             Paragraph("ASSETS", S("al", fontSize=5.5, fontName="Helvetica-Bold", textColor=C["blue"], spaceAfter=1)),
             Paragraph("  ".join(f"[{a}]" for a in ast) or "—", S("at", fontSize=7, textColor=C["blue"], leading=10)), Spacer(1, 2),
             Paragraph("LABELS", S("ll", fontSize=5.5, fontName="Helvetica-Bold", textColor=C["green"], spaceAfter=1)),
             Paragraph("  ".join(f"[{l}]" for l in lbl) or "—", S("lt", fontSize=7, textColor=C["green"], leading=10))],
            [Paragraph("VOICE-OVER", S("vl", fontSize=5.5, fontName="Helvetica-Bold", textColor=C["rose"], spaceAfter=2)),
             Paragraph(narr or "—", S("v", fontSize=8, fontName="Helvetica-Oblique", textColor=HexColor("#fce7f3"), leading=12))],
            [Paragraph("ANIMATION", S("anl", fontSize=5.5, fontName="Helvetica-Bold", textColor=C["amber"], spaceAfter=2)),
             Paragraph("<br/>".join(f"{k+1}. {re.sub(r'^[\\d]+[.)\\s]+','',l)}" for k, l in enumerate(al)) or "—",
                       S("an", fontSize=7, textColor=HexColor("#fde68a"), leading=11)),
             Spacer(1, 4),
             Paragraph("VISUAL", S("vdl", fontSize=5.5, fontName="Helvetica-Bold", textColor=C["purp"], spaceAfter=2)),
             Paragraph(vd or "—", S("vd", fontSize=7, textColor=HexColor("#c4b5fd"), leading=11))]
        ]]
        t = Table(data, colWidths=[12*mm, 68*mm, 51*mm, 59*mm, 58*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), C["card"]), ("BOX",(0,0),(-1,-1),1,C["b"]),
            ("INNERGRID",(0,0),(-1,-1),.5,HexColor("#111128")), ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",(0,0),(-1,-1),5), ("RIGHTPADDING",(0,0),(-1,-1),5),
            ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("BACKGROUND",(0,0),(0,-1),HexColor("#0a0a1e")), ("LINEAFTER",(0,0),(0,-1),2,C["blue"]),
            ("LINEBEFORE",(3,0),(3,-1),1.5,C["rose"]), ("LINEBEFORE",(4,0),(4,-1),1.5,C["amber"]),
        ]))
        story += [KeepTogether([t]), Spacer(1,4)]
    story += [
        HRFlowable(width="100%", thickness=.5, color=C["b"], spaceBefore=5),
        Paragraph(f"LPVision Studio · {name} · © {datetime.now().year} LearningPad",
                  S("ft", fontSize=7, textColor=C["mut"], alignment=TA_CENTER))
    ]
    def bg(c, d):
        c.saveState(); c.setFillColor(C["bg"])
        c.rect(0, 0, landscape(A4)[0], landscape(A4)[1], fill=1, stroke=0); c.restoreState()
    doc.build(story, onFirstPage=bg, onLaterPages=bg)
    buf.seek(0)
    return buf.getvalue(), None

# ─── LIGHTBOX ────────────────────────────────────
def show_lightbox():
    sc = st.session_state.lb_scene
    if not sc: return
    b64 = sc.get("scene_image")
    if not b64: return

    snum  = sc.get("scene_number", "?")
    title = sc.get("title", "")
    uri   = f"data:image/png;base64,{b64}"
    cap   = f"Scene {snum:02d} · {title}"
    fname = f"scene_{snum:02d}_{title.replace(' ','_').lower()}.png"

    overlay = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
  background:rgba(3,3,18,0.97);
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  min-height:100vh;gap:14px;
  font-family:'DM Sans','Segoe UI',sans-serif;
}}
.img-wrap{{
  border-radius:14px;overflow:hidden;
  box-shadow:0 0 0 1px rgba(91,140,255,0.2),0 0 50px rgba(91,140,255,0.15),0 25px 70px rgba(0,0,0,0.85);
}}
img{{max-width:90vw;max-height:70vh;border-radius:14px;display:block;object-fit:contain;}}
.cap{{font-size:10px;color:#3a3d6b;font-family:'DM Mono',monospace;letter-spacing:.07em;}}
.actions{{display:flex;gap:9px;flex-wrap:wrap;justify-content:center;}}
.btn{{
  padding:9px 22px;border-radius:50px;
  font-size:11.5px;font-weight:700;cursor:pointer;border:none;
  transition:all .16s ease;letter-spacing:.03em;
  display:inline-flex;align-items:center;gap:5px;text-decoration:none;
}}
.btn-dl{{background:rgba(72,187,120,.1);color:#48bb78;border:1px solid rgba(72,187,120,.3)!important;}}
.btn-dl:hover{{background:rgba(72,187,120,.2);}}
.btn-regen{{background:rgba(91,140,255,.1);color:#5b8cff;border:1px solid rgba(91,140,255,.28)!important;}}
.btn-regen:hover{{background:rgba(91,140,255,.2);}}
.btn-close{{background:rgba(252,129,129,.1);color:#fc8181;border:1px solid rgba(252,129,129,.3)!important;}}
.btn-close:hover{{background:rgba(252,129,129,.2);}}
</style>
</head>
<body>
  <div class="img-wrap"><img src="{uri}" alt="{cap}"/></div>
  <div class="cap">{cap}</div>
  <div class="actions">
    <a href="{uri}" download="{fname}" class="btn btn-dl">⬇ Download</a>
    <button class="btn btn-regen" onclick="pm('lb_regen')">↺ Regenerate</button>
    <button class="btn btn-close" onclick="pm('lb_close')">✕ Close</button>
  </div>
  <script>
    function pm(t){{window.parent.postMessage({{type:t}},'*');}}
    document.addEventListener('keydown',function(e){{if(e.key==='Escape')pm('lb_close');}});
  </script>
</body>
</html>"""

    components.html(overlay, height=700, scrolling=False)

    components.html("""
<script>
(function(){
  function click(label){
    var btns=window.parent.document.querySelectorAll('button');
    for(var i=0;i<btns.length;i++){
      if((btns[i].innerText||'').trim()===label){btns[i].click();return;}
    }
  }
  window.parent.addEventListener('message',function(e){
    if(!e.data||!e.data.type)return;
    if(e.data.type==='lb_close')click('__lb_close__');
    if(e.data.type==='lb_regen')click('__lb_regen__');
  },false);
})();
</script>""", height=0, scrolling=False)

    hc1, hc2 = st.columns(2)
    with hc1:
        if st.button("__lb_close__", key="lb_close_btn"):
            st.session_state.lb_scene = None; st.rerun()
    with hc2:
        if st.button("__lb_regen__", key="lb_regen_btn"):
            cur_sb = active_sb()
            if cur_sb:
                scenes = cur_sb.get("scenes", [])
                idx = next((j for j, s in enumerate(scenes)
                            if s.get("scene_number") == sc.get("scene_number")), None)
                if idx is not None:
                    with st.spinner("Regenerating…"):
                        b = gen_image(scenes[idx])
                    if b:
                        scenes[idx]["scene_image"] = b
                        save_scenes(scenes)
                        st.session_state.lb_scene = scenes[idx]
            st.rerun()

# ─── LIGHTBOX GATE ───────────────────────────────
if st.session_state.lb_scene:
    show_lightbox()
    st.stop()

# ─── SIDEBAR ─────────────────────────────────────
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
        '<div style="font-size:8.5px;font-weight:700;letter-spacing:.18em;color:var(--t2);'
        'text-transform:uppercase;margin-bottom:.5rem;font-family:var(--mono);">📁 Projects</div>',
        unsafe_allow_html=True
    )

    with st.expander("＋ New Project"):
        nm = st.text_input("Name", placeholder="e.g. Biology Ch3", key="np_name")
        if st.button("Create", key="np_btn"):
            if nm.strip():
                pid = str(uuid.uuid4())
                st.session_state.projects[pid] = {"name": nm.strip(), "created": _date(), "storyboards": {}}
                st.session_state.active_project = pid
                st.session_state.active_sb = None; st.rerun()

    for pid, proj in st.session_state.projects.items():
        is_active = pid == st.session_state.active_project
        lbl = f"{'▸ ' if is_active else ''}{proj['name']} [{len(proj.get('storyboards',{}))}]"
        if st.button(lbl, key=f"p_{pid}", use_container_width=True):
            st.session_state.active_project = pid
            st.session_state.active_sb = None
            st.session_state.active_tab = 0; st.rerun()

    if len(st.session_state.projects) > 1:
        st.markdown("---")
        with st.expander("🗑 Delete Project"):
            st.warning(f"Delete **{active_proj().get('name','')}**?")
            if st.button("Confirm Delete", key="dp_btn"):
                del st.session_state.projects[st.session_state.active_project]
                st.session_state.active_project = list(st.session_state.projects.keys())[0]
                st.session_state.active_sb = None; st.rerun()

    st.markdown("---")
    gk = bool(GROQ_KEY); mk = bool(GEM_KEY)
    st.markdown(f"""
    <div style="font-size:10.5px;color:var(--t2);line-height:2.1;font-family:var(--mono);">
      🤖 Groq &nbsp;
      <span style="color:{'var(--green)' if gk else 'var(--rose)'};">{'✓' if gk else '✗'}</span><br>
      🖼 Gemini &nbsp;
      <span style="color:{'var(--green)' if mk else 'var(--amber)'};">{'✓' if mk else '⚠'}</span>
    </div>
    <div style="font-size:8.5px;color:var(--t2);text-align:center;margin-top:10px;font-family:var(--mono);">
      © 2026 LearningPad
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN ────────────────────────────────────────
proj  = active_proj()
pname = proj.get("name", "Untitled")
sbs   = proj.get("storyboards", {})
sb    = active_sb()

st.markdown(f"""
<div class="topbar">
  <div style="display:flex;align-items:center;gap:8px;">
    <span style="color:var(--t2);font-size:12px;font-family:var(--mono);">📁 {pname}</span>
    <span style="color:var(--t2);">›</span>
    <span class="topbar-title">{"Select a Storyboard" if not sb else sb['name']}</span>
  </div>
  <span class="topbar-meta">📋 {len(sbs)} storyboard{'s' if len(sbs)!=1 else ''}</span>
</div>
""", unsafe_allow_html=True)

# ── Tab bar ──
cur_tab = st.session_state.active_tab
TABS = [("📋", "Storyboards"), ("🎬", "Editor"), ("📦", "Export")]

tab_html = '<div class="tab-bar">'
for i, (icon, label) in enumerate(TABS):
    cls = "active" if i == cur_tab else ""
    tab_html += (
        f'<div class="tab-item {cls}" '
        f'onclick="(function(){{var b=window.parent.document.querySelector(\'button[data-tab-id=\\\"{i}\\\"]\');if(b)b.click();}})()">'
        f'{icon} {label}</div>'
    )
tab_html += '</div>'
st.markdown(tab_html, unsafe_allow_html=True)

t0, t1, t2 = st.columns(3)
with t0:
    if st.button("\u200b", key="tab_btn_0"): st.session_state.active_tab=0; st.rerun()
with t1:
    if st.button("\u200b\u200b", key="tab_btn_1"): st.session_state.active_tab=1; st.rerun()
with t2:
    if st.button("\u200b\u200b\u200b", key="tab_btn_2"): st.session_state.active_tab=2; st.rerun()

components.html("""
<script>
(function tag(n){
  var doc=window.parent.document;
  // Target by data-testid key attribute which Streamlit sets on the button's parent
  var containers=doc.querySelectorAll('[data-testid="baseButton-secondary"]');
  containers.forEach(function(b){
    var key=b.closest('[data-stale]') || b.parentElement;
    // Use aria-label or look for key in parent chain
  });
  // Fallback: tag by button order within the hidden columns block
  var allBtns=Array.from(doc.querySelectorAll('button'));
  var zws0=[], zws1=[], zws2=[];
  allBtns.forEach(function(b){
    var txt=b.textContent||'';
    // zero-width space buttons
    if(txt==='\u200b'){zws0.push(b);}
    else if(txt==='\u200b\u200b'){zws1.push(b);}
    else if(txt==='\u200b\u200b\u200b'){zws2.push(b);}
  });
  if(zws0[0])zws0[0].setAttribute('data-tab-id','0');
  if(zws1[0])zws1[0].setAttribute('data-tab-id','1');
  if(zws2[0])zws2[0].setAttribute('data-tab-id','2');
  var found=(zws0.length>0?1:0)+(zws1.length>0?1:0)+(zws2.length>0?1:0);
  if(found<3&&n<25)setTimeout(function(){tag(n+1);},80);
})(0);
</script>""", height=0, scrolling=False)

# ════ TAB 0 — STORYBOARDS ════════════════════════
if cur_tab == 0:
    c1, _ = st.columns([3, 5])
    with c1:
        sbn = st.text_input("🏷 Name", placeholder="Untitled Storyboard", key="new_sb_name")
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
                st.session_state.active_tab = 1; st.rerun()
        with cb:
            imp = st.file_uploader("📂 Import JSON", type=["json"], key="imp_sb", label_visibility="collapsed")
            if imp:
                try:
                    raw = json.load(imp); nid = str(uuid.uuid4())
                    if isinstance(raw, list):
                        sc_imp = norm(raw); nm_imp = imp.name.replace(".json","")
                    elif isinstance(raw, dict) and "scenes" in raw:
                        sc_imp = norm(raw["scenes"]); nm_imp = raw.get("name", imp.name.replace(".json",""))
                    else:
                        st.error("Bad format"); sc_imp = []; nm_imp = "Imported"
                    if sc_imp:
                        st.session_state.projects[st.session_state.active_project]["storyboards"][nid] = {
                            "name": nm_imp, "created": _date(), "scenes": sc_imp
                        }
                        st.session_state.active_sb = nid
                        st.session_state.active_tab = 1; st.rerun()
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
            n_sc  = len(sb_item.get("scenes", []))
            n_img = sum(1 for s in sb_item.get("scenes",[]) if s.get("scene_image"))
            is_open = sid == st.session_state.active_sb
            ci, co, cd = st.columns([6, 1.5, 1])
            with ci:
                st.markdown(f"""
                <div style="padding:.3rem 0;">
                  <div class="sb-name">{'🎬 ' if is_open else '📋 '}{sb_item['name']}</div>
                  <div class="sb-meta">🗓 {sb_item.get('created','')} &nbsp;·&nbsp; 🎞 {n_sc} scenes &nbsp;·&nbsp; 🖼 {n_img} images</div>
                </div>""", unsafe_allow_html=True)
            with co:
                if st.button("Open →", key=f"open_{sid}", use_container_width=True):
                    st.session_state.active_sb = sid
                    st.session_state.editing_scene = None
                    st.session_state.active_tab = 1; st.rerun()
            with cd:
                if st.button("🗑", key=f"dsb_{sid}", use_container_width=True):
                    del st.session_state.projects[st.session_state.active_project]["storyboards"][sid]
                    if st.session_state.active_sb == sid: st.session_state.active_sb = None
                    st.rerun()
            st.markdown('<hr style="margin:4px 0;border-color:var(--border);">', unsafe_allow_html=True)

# ════ TAB 1 — EDITOR ═════════════════════════════
elif cur_tab == 1:
    sb = active_sb()
    if not sb:
        st.info("🎬 Open or create a storyboard from the Storyboards tab.")
    else:
        has = bool(sb.get("scenes"))

        with st.expander("⚙️ Generate / Input Controls", expanded=not has):
            r1, r2 = st.columns(2)
            with r1:
                auto_count = st.checkbox("🤖 Auto-detect scene count", value=False, key="auto_count")
                if not auto_count:
                    n_sc = st.slider("🎞 Scenes", 3, 15, 6, key="nsc")
                else:
                    n_sc = 0
                src = st.radio("📂 Source", ["📝 Plain Text","📄 PDF","🖼 Image"],
                               horizontal=True, key="src_type")
                with_imgs = st.checkbox("🖼 Auto-generate images", value=False, key="with_imgs")
            with r2:
                txt=""; src_img_b64=None; src_img_mime="image/jpeg"
                if src == "📝 Plain Text":
                    txt = st.text_area("✏️ Content", height=145,
                        placeholder="Paste your lesson, script or topic…", key="src_txt")
                    st.caption(f"{len(txt)} chars")
                elif src == "📄 PDF":
                    pf = st.file_uploader("📄 Upload PDF", type=["pdf"], key="pdf_up")
                    if pf:
                        rd = PyPDF2.PdfReader(pf)
                        for pg in rd.pages: txt += (pg.extract_text() or "")
                        st.success(f"✅ {len(txt)} chars from PDF")
                else:
                    img_up = st.file_uploader("🖼 Upload Image", type=["jpg","jpeg","png","webp"], key="img_src_up")
                    if img_up:
                        src_img_mime = img_up.type or "image/jpeg"
                        img_up.seek(0); src_img_b64 = base64.b64encode(img_up.read()).decode()
                        img_up.seek(0); st.image(img_up, use_container_width=True)

            ga, gb = st.columns(2)
            with ga:
                lbl = "🚀 Generate Scenes" if auto_count else f"🚀 Generate {n_sc} Scenes"
                gen_btn = st.button(lbl, key="gen_btn", use_container_width=True)
            with gb:
                clr_btn = st.button("🗑 Clear All", key="clr_btn", use_container_width=True)

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
                        with st.spinner("🔍 Extracting content via Gemini…"):
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
                            prog.progress(100, "✅ Done!")
                        st.rerun()
                elif src != "🖼 Image":
                    st.warning("Paste content or upload a file first.")

        sb   = active_sb()
        scenes = sb.get("scenes", []) if sb else []

        # ── Add scene manually ──
        with st.expander("➕ Add Scene Manually"):
            ma, mb = st.columns(2)
            with ma:
                m_title  = st.text_input("Title", key="m_title", placeholder="e.g. Introduction")
                m_assets = st.text_input("3D Assets (comma-separated GLB)", key="m_assets")
                m_labels = st.text_input("On-Screen Labels (comma-separated)", key="m_labels")
            with mb:
                m_narr = st.text_area("Voice-Over", key="m_narr", height=90,
                    placeholder="1–2 sentence narration…")
                m_vd   = st.text_area("Visual Description", key="m_vd", height=60)
            m_anim = st.text_area("Animation Steps (one per line)", key="m_anim", height=65)
            m_img_up = st.file_uploader("Scene Image (optional)", type=["jpg","jpeg","png","webp"],
                key="m_img_up")
            m_img_b64 = None
            if m_img_up:
                m_img_up.seek(0); m_img_b64 = base64.b64encode(m_img_up.read()).decode()
                m_img_up.seek(0); st.image(m_img_up, use_container_width=True)
            if st.button("➕ Add Scene", key="m_add"):
                if m_title.strip():
                    new_sc = {
                        "scene_number": len(scenes)+1, "title": m_title.strip(),
                        "assets": [x.strip() for x in m_assets.split(",") if x.strip()],
                        "labels": [x.strip() for x in m_labels.split(",") if x.strip()],
                        "narration": m_narr.strip(), "visual_description": m_vd.strip(),
                        "animation": m_anim.strip(), "scene_image": m_img_b64
                    }
                    scenes.append(new_sc); save_scenes(scenes); st.success("✅ Scene added!"); st.rerun()
                else: st.warning("Enter a title.")

        if not scenes:
            st.markdown("""
            <div style="text-align:center;padding:3.5rem 2rem;color:var(--t2);
                border:1.5px dashed var(--border2);border-radius:12px;margin-top:.5rem;background:var(--card);">
              <div style="font-size:2rem;margin-bottom:.4rem;opacity:.4;">🎞</div>
              <div style="font-size:13px;font-weight:700;color:var(--t1);">No scenes yet</div>
              <div style="font-size:11.5px;margin-top:.3rem;">Use the Generate controls above.</div>
            </div>""", unsafe_allow_html=True)
        else:
            n_img  = sum(1 for s in scenes if s.get("scene_image"))
            n_miss = len(scenes) - n_img

            hc1, hc2 = st.columns([3, 1])
            with hc1:
                miss_html = f" &nbsp;<span style='color:var(--amber);'>⚠ {n_miss} missing</span>" if n_miss else ""
                st.markdown(f"""
                <div style="padding:.55rem .9rem;background:var(--card);border:1px solid var(--border);
                    border-radius:8px;margin-bottom:.55rem;">
                  <span style="font-size:13.5px;font-weight:700;color:var(--t0);">🎬 {sb['name']}</span>
                  <span style="font-size:9.5px;color:var(--t2);font-family:var(--mono);margin-left:10px;">
                    {len(scenes)} scenes &nbsp;·&nbsp; {n_img} images{miss_html}
                  </span>
                </div>""", unsafe_allow_html=True)
            with hc2:
                lbl = f"🖼 Gen All ({n_miss})" if n_miss else "↺ Regen All"
                if st.button(lbl, key="gen_all", use_container_width=True):
                    st.session_state.gen_all = True; st.rerun()

            if st.session_state.gen_all:
                st.session_state.gen_all = False
                targets = [i for i, s in enumerate(scenes) if not s.get("scene_image")] or list(range(len(scenes)))
                bar = st.progress(0, "Starting…"); stat = st.empty()
                for step, idx in enumerate(targets):
                    sc = scenes[idx]; sn = sc.get("scene_number", idx+1)
                    stat.markdown(
                        f'<div class="stat-bar">🖼 Generating Scene {sn:02d} — {sc.get("title","")}…</div>',
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
                ast_list  = assets(sc)
                lbl_list  = sc.get("labels", [])
                anim_raw  = sc.get("animation", "").strip()
                vd_txt    = sc.get("visual_description", "").strip()
                narr_txt  = sc.get("narration", "").strip()
                snum      = sc.get("scene_number", i+1)
                title     = sc.get("title", "Untitled")
                img_b64   = sc.get("scene_image")
                editing   = st.session_state.editing_scene == i

                with st.container():
                    h1, h2, h3, h4 = st.columns([.055, .5, .18, .26])
                    with h1:
                        st.markdown(f'<div class="scene-badge" style="margin-top:4px;">{snum:02d}</div>',
                                    unsafe_allow_html=True)
                    with h2:
                        st.markdown(f'<div class="scene-title" style="padding-top:5px;">{title}</div>',
                                    unsafe_allow_html=True)
                    with h3:
                        if st.button("✅ Done" if editing else "✏️ Edit", key=f"edit_{i}", use_container_width=True):
                            st.session_state.editing_scene = None if editing else i; st.rerun()
                    with h4:
                        gen_img = st.button(
                            "↺ Regen Image" if img_b64 else "🖼 Generate Image",
                            key=f"gi_{i}", use_container_width=True
                        )

                    # ── EDIT MODE ──
                    if editing:
                        st.markdown(
                            '<div style="background:var(--blue-dim);border:1px solid var(--blue);'
                            'border-radius:9px;padding:.8rem .95rem;margin:.35rem 0;">',
                            unsafe_allow_html=True
                        )
                        ea, eb = st.columns(2)
                        with ea:
                            nt = st.text_input("Title", value=title, key=f"et_{i}")
                            na = st.text_input("Assets", value=", ".join(ast_list), key=f"ea_{i}")
                            nl = st.text_input("Labels", value=", ".join(lbl_list), key=f"el_{i}")
                        with eb:
                            nn = st.text_area("Voice-Over", value=narr_txt, height=100, key=f"en_{i}")
                            nv = st.text_area("Visual Description", value=vd_txt, height=65, key=f"ev_{i}")
                        nanim = st.text_area("Animation Logic", value=anim_raw, height=75, key=f"ean_{i}")
                        edit_img_up = st.file_uploader("Replace Image", type=["jpg","jpeg","png","webp"],
                            key=f"eimg_{i}")
                        new_img_b64 = img_b64
                        if edit_img_up:
                            edit_img_up.seek(0); new_img_b64 = base64.b64encode(edit_img_up.read()).decode()
                            edit_img_up.seek(0); st.image(edit_img_up, use_container_width=True)
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
                                    f'style="width:100%;border-radius:8px;'
                                    f'border:1px solid var(--border);margin-top:4px;cursor:zoom-in;"/>',
                                    unsafe_allow_html=True
                                )
                                st.download_button(
                                    "⬇ PNG", data=base64.b64decode(img_b64),
                                    file_name=f"scene_{snum:02d}.png", mime="image/png",
                                    key=f"dl_{i}", use_container_width=True
                                )
                            else:
                                st.markdown("""
                                <div class="img-placeholder">
                                  <span style="font-size:1.8rem;opacity:.15;">🖼</span>
                                  <span style="font-size:10px;color:var(--t2);">No image</span>
                                </div>""", unsafe_allow_html=True)
                                quick_img = st.file_uploader("📂 Import", type=["jpg","jpeg","png","webp"],
                                    key=f"qimp_{i}", label_visibility="collapsed")
                                if quick_img:
                                    quick_img.seek(0)
                                    scenes[i]["scene_image"] = base64.b64encode(quick_img.read()).decode()
                                    save_scenes(scenes); st.rerun()

                        with ca_col:
                            tags = "".join(chip(a, "#0a1f45", "#60a5fa") for a in ast_list) or \
                                   '<span style="color:var(--t2);font-size:11px;">—</span>'
                            st.markdown(
                                panel("📦", "3D Assets", "var(--blue)", f'<div style="line-height:2.2;">{tags}</div>'),
                                unsafe_allow_html=True
                            )
                        with cb_col:
                            ltags = "".join(chip(l, "#052414", "#48bb78") for l in lbl_list) or \
                                    '<span style="color:var(--t2);font-size:11px;">—</span>'
                            st.markdown(
                                panel("🏷", "Labels", "var(--green)", f'<div style="line-height:2.2;">{ltags}</div>'),
                                unsafe_allow_html=True
                            )
                        with cn_col:
                            st.markdown(
                                panel("🎙", "Voice-Over", "var(--rose)",
                                      f'<div class="narr-text">{narr_txt or "—"}</div>', accent="var(--rose)"),
                                unsafe_allow_html=True
                            )

                        st.markdown("<div style='height:7px;'></div>", unsafe_allow_html=True)
                        ca2, cb2 = st.columns(2)
                        with ca2:
                            st.markdown(
                                panel("⚡", "Animation Steps", "var(--amber)", anim_html(anim_raw), accent="var(--amber)"),
                                unsafe_allow_html=True
                            )
                        with cb2:
                            st.markdown(
                                panel("🎨", "Visual Description", "var(--purple)",
                                      f'<div style="font-size:11.5px;color:#c4b5fd;line-height:1.7;">{vd_txt or "—"}</div>',
                                      accent="var(--purple)"),
                                unsafe_allow_html=True
                            )

                    if gen_img:
                        with st.spinner(f"🖼 Generating image for Scene {snum:02d}…"):
                            sl = st.empty(); b = gen_image(sc, sl)
                        if b:
                            scenes[i]["scene_image"] = b; save_scenes(scenes)
                            st.success(f"✅ Scene {snum:02d} done!"); st.rerun()

                    st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)
                    _, dc = st.columns([9, 1])
                    with dc:
                        if st.button("🗑", key=f"dsc_{i}", use_container_width=True):
                            scenes.pop(i); save_scenes(scenes)
                            if st.session_state.editing_scene == i:
                                st.session_state.editing_scene = None
                            st.rerun()
                    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ════ TAB 2 — EXPORT ═════════════════════════════
elif cur_tab == 2:
    sb = active_sb()
    if not sb:
        st.info("📦 Open a storyboard first.")
    else:
        scenes = sb.get("scenes", [])
        ex, im = st.columns(2)
        with ex:
            st.markdown(
                '<div style="font-size:9px;font-weight:700;letter-spacing:.15em;color:var(--t2);'
                'text-transform:uppercase;margin-bottom:.65rem;font-family:var(--mono);">📤 Export</div>',
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
                    data=json.dumps({"name": sb["name"], "created": sb.get("created",""), "scenes": out}, indent=2),
                    file_name=f"{sb['name'].replace(' ','_')}_storyboard.json",
                    mime="application/json", use_container_width=True
                )
                st.markdown("<div style='height:5px;'></div>", unsafe_allow_html=True)
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
                        file_name=f"{sb['name'].replace(' ','_')}.pdf",
                        mime="application/pdf", use_container_width=True
                    )
                st.markdown("---")
                hdr = "| # | Title | Assets | Labels | Voice-Over |"
                sep = "|---|-------|--------|--------|------------|"
                rows = [
                    f"| {s.get('scene_number','?')} | {s.get('title','')} | "
                    f"{', '.join(assets(s))} | {', '.join(s.get('labels',[]))} | "
                    f"{s.get('narration','')[:70]}{'…' if len(s.get('narration',''))>70 else ''} |"
                    for s in scenes
                ]
                st.markdown("\n".join([hdr, sep] + rows))
            else:
                st.info("No scenes yet.")

        with im:
            st.markdown(
                '<div style="font-size:9px;font-weight:700;letter-spacing:.15em;color:var(--t2);'
                'text-transform:uppercase;margin-bottom:.65rem;font-family:var(--mono);">📥 Import</div>',
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
