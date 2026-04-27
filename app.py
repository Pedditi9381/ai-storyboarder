import streamlit as st
import requests
import PyPDF2
import json
import uuid
import base64
import re
import io
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="LPVision Studio", layout="wide", page_icon="🎬")

# ─── CSS ───────────────────────────────────────────────────────────────────────
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
.scene-img { width:100%; border-radius:8px; object-fit:cover; border:1px solid #2d2d5a; display:block; }
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
    if "goto_editor" not in st.session_state:
        st.session_state.goto_editor = False

init_state()

# ─── API KEYS ──────────────────────────────────────────────────────────────────
GROQ_API_KEY   = st.secrets.get("GROQ_API_KEY",   None)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", None)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Updated Gemini model names — gemini-3.1-flash-image-preview is the latest (Nano Banana 2)
# Fallback chain: 3.1 → 2.5 → 2.0-preview
GEMINI_MODELS = [
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image-preview",
    "gemini-2.0-flash-preview-image-generation",
]
GEMINI_IMG_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

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

def pill(text, bg, color):
    return (
        f'<span style="display:inline-block;margin:2px 3px 2px 0;padding:3px 10px;'
        f'border-radius:5px;background:{bg};color:{color};font-size:11px;font-weight:600;">'
        f'{text}</span>'
    )

def section_box(title, color, content_html, bg, border, left_accent=None):
    accent = f"border-left:3px solid {left_accent};" if left_accent else ""
    return f"""
    <div style="background:{bg};border:1px solid {border};border-radius:10px;
                padding:0.75rem 0.85rem;{accent}height:100%;box-sizing:border-box;">
      <div style="font-size:9px;font-weight:800;letter-spacing:0.15em;
                  color:{color};text-transform:uppercase;margin-bottom:7px;">{title}</div>
      {content_html}
    </div>"""

# ─── GROQ: JSON CLEANER ────────────────────────────────────────────────────────
def fix_control_chars(s):
    result      = []
    in_string   = False
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
        if ch == '"':
            in_string = not in_string
            result.append(ch)
            continue
        if in_string:
            if   ch == '\n': result.append('\\n')
            elif ch == '\r': result.append('\\r')
            elif ch == '\t': result.append('\\t')
            else:            result.append(ch)
        else:
            result.append(ch)
    return ''.join(result)

def strip_fences(raw):
    raw = raw.strip()
    raw = re.sub(r'^```[a-zA-Z]*\n?', '', raw)
    raw = re.sub(r'```$', '', raw.strip())
    return raw.strip()

# ─── GROQ: SCENE GENERATION ────────────────────────────────────────────────────
def generate_scenes_groq(text, num_scenes):
    if not GROQ_API_KEY:
        st.error("Add GROQ_API_KEY to Streamlit Secrets.")
        return None

    system_prompt = f"""You are a Senior 3D Instructional Animator. Convert the input into EXACTLY {num_scenes} storyboard scenes.
Return ONLY a valid JSON array. No markdown fences. No explanation. No preamble.
Each element must have exactly these keys:
  scene_number (int), title (str 3-6 words), assets (array of 3-6 lowercase_glb_names),
  labels (array of 2-5 short UI caption strings), animation (str: numbered steps as plain text),
  visual_description (str: 2-3 sentences on camera/lighting/layout),
  narration (str: 2-4 complete educational sentences spoken by narrator)
CRITICAL JSON RULES: Never use literal newline or tab characters inside any string value.
Use the two-character sequence backslash-n to represent a line break inside a string."""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": f"Create a 3D educational storyboard for:\n\n{text[:6000]}"}
        ],
        "temperature": 0.3,
        "max_tokens":  4096
    }
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        raw = strip_fences(raw)
        raw = fix_control_chars(raw)
        data = json.loads(raw)
        if not isinstance(data, list):
            st.error("Groq returned unexpected format (not a JSON array).")
            return None
        return normalise_scenes(data)
    except requests.HTTPError as e:
        st.error(f"Groq HTTP error {resp.status_code}: {resp.text[:300]}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSON parse error at char {e.pos}: {e.msg}")
        snippet = raw[max(0, e.pos-60):e.pos+60] if raw else ""
        st.code(f"…{snippet}…", language="text")
        return None
    except Exception as e:
        st.error(f"Generation failed: {e}")
        return None

# ─── IMAGE PROMPT BUILDER ──────────────────────────────────────────────────────
def build_image_prompt(sc):
    """
    Craft a prompt for Gemini that produces a Blender-style 3D render —
    clean hard-surface GLB-ready models, PBR materials, HDRI studio lighting.
    This is the reference frame an artist uses to build each GLB asset.
    """
    vd     = sc.get("visual_description", "")
    title  = sc.get("title", "")
    assets = ", ".join(get_scene_assets(sc))
    labels = ", ".join(sc.get("labels", []))
    narr   = sc.get("narration", "")[:160]
    anim   = sc.get("animation", "")[:120]
    return (
        f"Professional 3D CGI storyboard reference frame for educational animation. "
        f"Scene: '{title}'. "
        f"Camera and layout: {vd} "
        f"Hard-surface GLB assets to model and position: {assets}. "
        f"UI annotation labels visible in scene: {labels}. "
        f"Animation sequence context: {anim}. "
        f"Educational topic: {narr}. "
        "Render specifications: Blender 4 Cycles renderer, photorealistic quality, "
        "clean subdivision-surface meshes with beveled edges (subdivision level 2), "
        "visible edge loops and clean topology suitable for GLB export to Three.js or Babylon.js, "
        "PBR shading with metallic/roughness workflow, "
        "four-point HDRI studio lighting — warm amber key (3200K), cool blue fill (6500K), "
        "purple-teal rim light, white bounce from below, "
        "deep charcoal #1a1a2e studio environment with subtle floor reflection, "
        "ambient occlusion baked, 16:9 widescreen composition, "
        "cinema-quality depth of field f/2.8 with foreground bokeh, "
        "objects positioned with clear spatial hierarchy for instructional clarity, "
        "subsurface scattering on translucent materials, "
        "no 2D illustration style, no cartoon, no flat design, "
        "no text overlays, no watermarks, no UI chrome, "
        "output should look like a professional GLB asset preview render."
    )

# ─── GEMINI IMAGE GENERATION ──────────────────────────────────────────────────
def generate_scene_image_gemini(sc):
    """
    Try Gemini image models in priority order:
      1. gemini-3.1-flash-image-preview  (Nano Banana 2 — best quality, 1K default)
      2. gemini-2.5-flash-image-preview  (Nano Banana 1 — good quality)
      3. gemini-2.0-flash-preview-image-generation  (stable preview)
    Returns (base64_str, None) on success or (None, error_msg) on failure.
    """
    if not GEMINI_API_KEY:
        return None, "No GEMINI_API_KEY in secrets."

    prompt = build_image_prompt(sc)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
            "imageConfig": {"aspectRatio": "16:9", "imageSize": "1K"}
        }
    }

    last_err = "No models tried."
    for model in GEMINI_MODELS:
        url = f"{GEMINI_IMG_BASE.format(model=model)}?key={GEMINI_API_KEY}"
        try:
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=90
            )
            if resp.status_code == 200:
                parts = (resp.json()
                         .get("candidates", [{}])[0]
                         .get("content", {})
                         .get("parts", []))
                for part in parts:
                    inline = part.get("inlineData", {})
                    if inline.get("mimeType", "").startswith("image/"):
                        return inline["data"], None
                last_err = f"{model}: responded 200 but no image part found."
            elif resp.status_code in (404, 400):
                # Model not available — try next
                err_msg = resp.json().get("error", {}).get("message", resp.text[:200])
                last_err = f"{model} {resp.status_code}: {err_msg}"
                continue
            else:
                err_msg = resp.json().get("error", {}).get("message", resp.text[:200])
                last_err = f"{model} {resp.status_code}: {err_msg}"
                break  # Non-404 error — don't retry other models
        except Exception as e:
            last_err = f"{model} exception: {e}"
            continue

    return None, last_err


def generate_scene_image_pollinations(sc):
    """
    Fallback: Pollinations.ai Flux model — free, no API key needed.
    """
    prompt  = build_image_prompt(sc)
    encoded = requests.utils.quote(prompt[:700])
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1024&height=576&model=flux&nologo=true&enhance=true&seed=-1"
    )
    try:
        resp = requests.get(url, timeout=120)
        if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
            return base64.b64encode(resp.content).decode("utf-8"), None
        return None, f"Pollinations {resp.status_code}"
    except Exception as e:
        return None, str(e)


def generate_scene_image(sc):
    """Try Gemini first (all models in fallback chain); fall back to Pollinations."""
    if GEMINI_API_KEY:
        b64, err = generate_scene_image_gemini(sc)
        if b64:
            return b64
        st.warning(f"Gemini image failed ({err}), using Pollinations fallback…")

    b64, err = generate_scene_image_pollinations(sc)
    if b64:
        return b64
    st.error(f"Image generation failed: {err}")
    return None

# ─── PDF EXPORT ────────────────────────────────────────────────────────────────
def generate_storyboard_pdf(sb_name, scenes):
    """
    Generate a professional storyboard PDF using reportlab.
    Each scene gets its own section with image (if available), metadata, and narration.
    Returns bytes of the PDF.
    """
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import mm, cm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.colors import HexColor, white, black
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, Image as RLImage, KeepTogether
        )
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        from PIL import Image as PILImage
    except ImportError:
        return None, "reportlab or Pillow not installed. Run: pip install reportlab Pillow"

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=12*mm, bottomMargin=12*mm,
        title=f"LPVision Studio — {sb_name}",
        author="LPVision Studio"
    )

    # ── Colours
    C_BG        = HexColor("#06060f")
    C_CARD      = HexColor("#0d0d1a")
    C_BORDER    = HexColor("#1e1e3a")
    C_ACCENT    = HexColor("#3b82f6")
    C_PURPLE    = HexColor("#8b5cf6")
    C_GREEN     = HexColor("#4ade80")
    C_AMBER     = HexColor("#f59e0b")
    C_PINK      = HexColor("#fb7185")
    C_TEXT      = HexColor("#e2e8f0")
    C_MUTED     = HexColor("#64748b")
    C_WHITE     = white

    # ── Styles
    def S(name, **kw):
        base = dict(fontName="Helvetica", fontSize=9, leading=13,
                    textColor=C_TEXT, spaceAfter=2)
        base.update(kw)
        return ParagraphStyle(name, **base)

    sTitle    = S("sTitle",  fontSize=22, fontName="Helvetica-Bold",
                  textColor=C_TEXT, spaceAfter=4, leading=26)
    sSub      = S("sSub",    fontSize=11, textColor=C_MUTED, spaceAfter=2)
    sLabel    = S("sLabel",  fontSize=7,  fontName="Helvetica-Bold",
                  textColor=C_MUTED, spaceAfter=3, letterSpacing=1.2)
    sSceneNum = S("sSceneNum", fontSize=18, fontName="Helvetica-Bold",
                  textColor=C_ACCENT, alignment=TA_CENTER, leading=22)
    sSceneTitle = S("sSceneTitle", fontSize=12, fontName="Helvetica-Bold",
                    textColor=C_TEXT, leading=16)
    sBody     = S("sBody",   fontSize=8,  textColor=C_TEXT, leading=12)
    sTag      = S("sTag",    fontSize=7,  textColor=C_ACCENT, leading=10)
    sTagG     = S("sTagG",   fontSize=7,  textColor=C_GREEN, leading=10)
    sNarr     = S("sNarr",   fontSize=8,  textColor=HexColor("#fce7f3"),
                  fontName="Helvetica-Oblique", leading=12)
    sAnim     = S("sAnim",   fontSize=7.5, textColor=HexColor("#fde68a"), leading=11)
    sVD       = S("sVD",     fontSize=7.5, textColor=HexColor("#c4b5fd"), leading=11)
    sFooter   = S("sFooter", fontSize=7,  textColor=C_MUTED, alignment=TA_CENTER)

    story = []

    # ── Cover header
    story.append(Paragraph("LPVision Studio", sTitle))
    story.append(Paragraph(f"Storyboard Export · {sb_name}", sSub))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%B %d, %Y at %H:%M')} · {len(scenes)} Scenes",
        S("sDate", fontSize=8, textColor=C_MUTED)
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceAfter=8))

    # ── Scene cards
    for i, sc in enumerate(scenes):
        snum   = sc.get("scene_number", i + 1)
        title  = sc.get("title", "Untitled")
        assets = get_scene_assets(sc)
        labels = sc.get("labels", [])
        anim   = sc.get("animation", "").strip().replace("\\n", "\n")
        vd     = sc.get("visual_description", "").strip()
        narr   = sc.get("narration", "").strip()
        img_b64 = sc.get("scene_image")

        # Build image column
        img_cell = []
        if img_b64:
            try:
                img_bytes = base64.b64decode(img_b64)
                pil_img = PILImage.open(io.BytesIO(img_bytes))
                img_buf = io.BytesIO()
                pil_img.save(img_buf, format="PNG")
                img_buf.seek(0)
                rl_img = RLImage(img_buf, width=70*mm, height=39.4*mm)
                img_cell.append(rl_img)
            except Exception:
                img_cell.append(Paragraph("[Image unavailable]",
                    S("sImgErr", fontSize=8, textColor=C_MUTED)))
        else:
            img_cell.append(Paragraph("[ No Image Generated ]",
                S("sNoImg", fontSize=8, textColor=C_MUTED, alignment=TA_CENTER)))

        # Scene number badge
        num_cell = [
            Paragraph(f"{snum:02d}", sSceneNum),
        ]

        # Title + assets + labels
        asset_tags = "  ".join([f"[{a}]" for a in assets]) or "—"
        label_tags = "  ".join([f"[{l}]" for l in labels]) or "—"
        meta_cell = [
            Paragraph(f"SCENE {snum:02d}", sLabel),
            Paragraph(title, sSceneTitle),
            Spacer(1, 4),
            Paragraph("3D ASSETS", S("sLbl2", fontSize=6, fontName="Helvetica-Bold",
                      textColor=C_ACCENT, spaceAfter=2)),
            Paragraph(asset_tags, sTag),
            Spacer(1, 3),
            Paragraph("UI LABELS", S("sLbl3", fontSize=6, fontName="Helvetica-Bold",
                      textColor=C_GREEN, spaceAfter=2)),
            Paragraph(label_tags, sTagG),
        ]

        # Narration
        narr_cell = [
            Paragraph("NARRATION", S("sLbl4", fontSize=6, fontName="Helvetica-Bold",
                      textColor=C_PINK, spaceAfter=3)),
            Paragraph(narr or "—", sNarr),
        ]

        # Animation + Visual Description
        anim_lines = [l.strip() for l in anim.split("\n") if l.strip()]
        anim_text = "<br/>".join([
            f"{idx+1}. {l.lstrip('0123456789.) ') if l[:1].isdigit() else l}"
            for idx, l in enumerate(anim_lines)
        ]) or "—"
        anim_cell = [
            Paragraph("ANIMATION LOGIC", S("sLbl5", fontSize=6, fontName="Helvetica-Bold",
                      textColor=C_AMBER, spaceAfter=3)),
            Paragraph(anim_text, sAnim),
            Spacer(1, 5),
            Paragraph("VISUAL DESCRIPTION", S("sLbl6", fontSize=6, fontName="Helvetica-Bold",
                      textColor=C_PURPLE, spaceAfter=3)),
            Paragraph(vd or "—", sVD),
        ]

        # Layout: [num | img | meta | narr | anim+vd]
        col_w = [14*mm, 72*mm, 52*mm, 58*mm, 58*mm]
        data = [[num_cell, img_cell, meta_cell, narr_cell, anim_cell]]

        tbl = Table(data, colWidths=col_w, repeatRows=0)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), C_CARD),
            ("BOX",          (0, 0), (-1, -1), 1, C_BORDER),
            ("INNERGRID",    (0, 0), (-1, -1), 0.5, HexColor("#151528")),
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",   (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            # Scene number column accent
            ("BACKGROUND",   (0, 0), (0, -1), HexColor("#0a1628")),
            ("LINEAFTER",    (0, 0), (0, -1), 2, C_ACCENT),
            # Narration column accent
            ("LINEBEFORE",   (3, 0), (3, -1), 2, C_PINK),
            # Anim column accent
            ("LINEBEFORE",   (4, 0), (4, -1), 2, C_AMBER),
        ]))

        story.append(KeepTogether([tbl]))
        story.append(Spacer(1, 5))

    # ── Footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER, spaceBefore=6))
    story.append(Paragraph(
        f"LPVision Studio · {sb_name} · {len(scenes)} Scenes · © {datetime.now().year} LearningPad",
        sFooter
    ))

    # ── Build
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_BG)
        canvas.rect(0, 0, landscape(A4)[0], landscape(A4)[1], fill=1, stroke=0)
        canvas.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf.getvalue(), None

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

    st.markdown('<div style="font-size:10px;font-weight:600;letter-spacing:0.15em;color:#475569;text-transform:uppercase;margin-bottom:0.5rem;">Projects</div>', unsafe_allow_html=True)

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
                st.session_state.goto_editor       = False
                st.rerun()

    for pid, proj in st.session_state.projects.items():
        is_active = pid == st.session_state.active_project
        sb_count  = len(proj.get("storyboards", {}))
        lbl       = f"{'▸ ' if is_active else ''}{proj['name']}  [{sb_count}]"
        if st.button(lbl, key=f"proj_btn_{pid}", use_container_width=True):
            st.session_state.active_project    = pid
            st.session_state.active_storyboard = None
            st.session_state.goto_editor       = False
            st.rerun()

    if len(st.session_state.projects) > 1:
        st.markdown("---")
        with st.expander("🗑 Delete Project"):
            st.warning(f"Delete **{get_active_project().get('name','')}**?")
            if st.button("Confirm Delete", key="del_proj_confirm"):
                del st.session_state.projects[st.session_state.active_project]
                st.session_state.active_project    = list(st.session_state.projects.keys())[0]
                st.session_state.active_storyboard = None
                st.session_state.goto_editor       = False
                st.rerun()

    st.markdown("---")
    groq_ok   = bool(GROQ_API_KEY)
    gemini_ok = bool(GEMINI_API_KEY)
    st.markdown(f"""
    <div style="font-size:11px;color:#475569;line-height:2;">
      Groq &nbsp;&nbsp;
        <span style="color:{'#4ade80' if groq_ok else '#f87171'};">
          {'✓ Connected' if groq_ok else '✗ Add GROQ_API_KEY'}</span><br>
      Gemini
        <span style="color:{'#4ade80' if gemini_ok else '#f59e0b'};">
          {'✓ Connected (3.1 Flash)' if gemini_ok else '⚠ Optional (Pollinations fallback)'}</span>
    </div>
    <div style="font-size:10px;color:#334155;text-align:center;margin-top:10px;">
      © 2026 LearningPad
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN ──────────────────────────────────────────────────────────────────────
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
    <span style="color:#334155;">›</span>
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
tabs = st.tabs(["📋 Storyboards", "🎬 Editor", "📦 Export / Import"])

# ════════════════════════════════════════════════════════════
# TAB 0 — STORYBOARD LIST
# ════════════════════════════════════════════════════════════
with tabs[0]:
    c_form, _ = st.columns([3, 5])
    with c_form:
        new_sb_name = st.text_input("New storyboard name", placeholder="Untitled Storyboard", key="new_sb_name")
        ca, cb = st.columns(2)
        with ca:
            if st.button("＋ New Storyboard", key="new_sb_btn", use_container_width=True):
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
                        st.error("Unrecognised JSON format.")
                        sc_imp = []
                        nm_imp = "Imported"
                    if sc_imp:
                        st.session_state.projects[st.session_state.active_project]["storyboards"][sbid] = {
                            "name": nm_imp, "created": datetime.now().strftime("%b %d, %Y"), "scenes": sc_imp
                        }
                        st.session_state.active_storyboard = sbid
                        st.session_state.goto_editor       = True
                        st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {e}")

    st.markdown("---")
    if not storyboards:
        st.markdown('<div style="text-align:center;padding:3rem;color:#334155;">No storyboards yet. Create one above.</div>', unsafe_allow_html=True)
    else:
        for sbid, sb in storyboards.items():
            n_sc    = len(sb.get("scenes", []))
            is_open = sbid == active_sb_id
            ci, co, cd = st.columns([6, 1.5, 1])
            with ci:
                c = '#93c5fd' if is_open else '#e2e8f0'
                st.markdown(f"""
                <div style="padding:0.5rem 0;">
                  <div style="font-size:14px;font-weight:600;color:{c};">
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
                    st.session_state.editing_scene     = None
                    st.session_state.goto_editor       = True
                    st.rerun()
            with cd:
                if st.button("🗑", key=f"del_{sbid}", use_container_width=True):
                    del st.session_state.projects[st.session_state.active_project]["storyboards"][sbid]
                    if active_sb_id == sbid:
                        st.session_state.active_storyboard = None
                        st.session_state.goto_editor       = False
                    st.rerun()
            st.markdown('<hr style="margin:4px 0;border-color:#1e1e3a;">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 1 — EDITOR
# ════════════════════════════════════════════════════════════
with tabs[default_tab if default_tab == 1 else 1]:
    if not active_sb:
        st.info("Open or create a storyboard from the **Storyboards** tab.")
    else:
        has_scenes = bool(active_sb.get("scenes"))
        with st.expander("⚙️  Generate / Input Controls", expanded=not has_scenes):
            c1, c2 = st.columns(2)
            with c1:
                num_scenes = st.slider("Scenes to generate", 3, 12, 6, key="num_scenes_slider")
                input_type = st.radio("Source", ["Plain Text", "PDF Document"], horizontal=True, key="input_type_radio")
            with c2:
                final_text = ""
                if input_type == "Plain Text":
                    final_text = st.text_area("Paste content", height=130,
                        placeholder="e.g. Working of a Steam Engine, Photosynthesis…",
                        key="plain_text_input")
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

            if gen_btn:
                if not final_text.strip():
                    st.warning("Paste content or upload a PDF first.")
                else:
                    with st.spinner(f"Generating {num_scenes} scenes with Groq…"):
                        new_sc = generate_scenes_groq(final_text, num_scenes)
                    if new_sc:
                        save_scenes(new_sc)
                        st.session_state.editing_scene = None
                        st.session_state.goto_editor   = True
                        st.success(f"✓ {len(new_sc)} scenes generated!")
                        st.rerun()

        scenes = active_sb.get("scenes", [])

        if not scenes:
            st.markdown("""
            <div style="text-align:center;padding:5rem 2rem;color:#334155;
                        border:1px dashed #1e1e3a;border-radius:16px;margin-top:1rem;">
              <div style="font-size:3rem;">🎞</div>
              <div style="font-size:15px;font-weight:600;color:#475569;margin-top:0.5rem;">No scenes yet</div>
              <div style="font-size:13px;margin-top:0.3rem;">Expand the controls above and hit Generate.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            n_images = sum(1 for s in scenes if s.get("scene_image"))
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        padding:0.6rem 1rem;background:#0d0d1a;border:1px solid #1e1e3a;
                        border-radius:12px;margin:0.5rem 0 1.2rem 0;">
              <div style="font-size:13px;font-weight:700;color:#e2e8f0;">
                📋 {active_sb['name']}
              </div>
              <div style="font-size:12px;color:#475569;font-family:'JetBrains Mono',monospace;">
                {len(scenes)} SCENES &nbsp;·&nbsp; {n_images} IMAGES
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

                h1, h2, h3, h4 = st.columns([0.06, 0.52, 0.18, 0.24])
                with h1:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#2563eb,#7c3aed);color:white;
                                font-size:10px;font-weight:800;letter-spacing:0.1em;
                                padding:5px 8px;border-radius:12px;text-align:center;
                                font-family:'JetBrains Mono',monospace;margin-top:6px;">{snum:02d}</div>
                    """, unsafe_allow_html=True)
                with h2:
                    st.markdown(f"""
                    <div style="font-size:15px;font-weight:700;color:#f1f5f9;padding-top:4px;">{title}</div>
                    """, unsafe_allow_html=True)
                with h3:
                    edit_lbl = "✅ Done" if editing else "✏️ Edit Scene"
                    if st.button(edit_lbl, key=f"edit_toggle_{i}", use_container_width=True):
                        st.session_state.editing_scene = None if editing else i
                        st.rerun()
                with h4:
                    img_lbl = "🔄 Regenerate Image" if img_b64 else "🖼 Generate Image"
                    gen_img = st.button(img_lbl, key=f"gen_img_{i}", use_container_width=True)

                if editing:
                    with st.container():
                        st.markdown("""<div style="background:#0a0a1a;border:1px solid #2563eb;
                                        border-radius:12px;padding:1rem 1.1rem;margin:0.6rem 0;">
                        """, unsafe_allow_html=True)
                        ea, eb = st.columns(2)
                        with ea:
                            new_title  = st.text_input("Scene Title", value=title, key=f"e_title_{i}")
                            new_assets = st.text_input("Assets (comma-separated GLB names)",
                                                       value=", ".join(assets), key=f"e_assets_{i}")
                            new_labels = st.text_input("Labels (comma-separated UI text)",
                                                       value=", ".join(labels), key=f"e_labels_{i}")
                        with eb:
                            new_narr = st.text_area("Narration", value=narr, height=110, key=f"e_narr_{i}")
                            new_vd   = st.text_area("Visual Description", value=vd, height=75, key=f"e_vd_{i}")
                        new_anim = st.text_area("Animation Logic", value=anim, height=90, key=f"e_anim_{i}")

                        sv, _ = st.columns([1, 4])
                        with sv:
                            if st.button("💾 Save Changes", key=f"save_{i}", use_container_width=True):
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
                        st.markdown("</div>", unsafe_allow_html=True)

                else:
                    c_img, c_a, c_b, c_n = st.columns([1, 1, 1, 2])

                    with c_img:
                        if img_b64:
                            st.markdown(
                                f'<img class="scene-img" src="data:image/png;base64,{img_b64}"/>',
                                unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="height:145px;background:#0d0d1a;border:1px dashed #2d2d5a;
                                        border-radius:8px;display:flex;align-items:center;
                                        justify-content:center;flex-direction:column;gap:6px;">
                              <span style="font-size:2rem;opacity:0.4;">🖼</span>
                              <span style="font-size:11px;color:#334155;">No image yet</span>
                            </div>""", unsafe_allow_html=True)

                    with c_a:
                        tags = "".join([pill(a, "#0f1f3d", "#60a5fa") for a in assets]) \
                               or '<span style="color:#334155;font-size:11px;">—</span>'
                        st.markdown(section_box(
                            "🔷 3D Assets (GLB)", "#3b82f6",
                            f'<div style="line-height:1.9;">{tags}</div>',
                            "#0d1117", "#1e3a5f"
                        ), unsafe_allow_html=True)

                    with c_b:
                        ltags = "".join([pill(l, "#0f2d1a", "#4ade80") for l in labels]) \
                                or '<span style="color:#334155;font-size:11px;">—</span>'
                        st.markdown(section_box(
                            "🟢 UI Labels", "#4ade80",
                            f'<div style="line-height:1.9;">{ltags}</div>',
                            "#0d1a12", "#1a3d25"
                        ), unsafe_allow_html=True)

                    with c_n:
                        narr_html = f'<div style="font-size:12px;color:#f1f5f9;line-height:1.75;font-style:italic;">{narr or "—"}</div>'
                        st.markdown(section_box(
                            "🎙 Narration", "#fb7185", narr_html,
                            "#1a0d1a", "#3d1a2e", left_accent="#fb7185"
                        ), unsafe_allow_html=True)

                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                    c_anim, c_vd = st.columns(2)

                    with c_anim:
                        anim_lines = [l.strip() for l in
                                      anim.replace("\\n", "\n").replace("\r\n", "\n").split("\n")
                                      if l.strip()]
                        steps = "".join([
                            f'<div style="display:flex;gap:8px;margin-bottom:5px;align-items:flex-start;">'
                            f'<span style="min-width:18px;height:18px;border-radius:50%;'
                            f'background:linear-gradient(135deg,#d97706,#f59e0b);color:#000;'
                            f'font-size:9px;font-weight:800;display:flex;align-items:center;'
                            f'justify-content:center;flex-shrink:0;margin-top:2px;">{idx+1}</span>'
                            f'<span style="font-size:12px;color:#fde68a;line-height:1.5;">'
                            f'{line.lstrip("0123456789.) ") if line[:1].isdigit() else line}'
                            f'</span></div>'
                            for idx, line in enumerate(anim_lines)
                        ]) or '<span style="color:#334155;font-size:11px;">—</span>'
                        st.markdown(section_box(
                            "⚡ Animation Logic (GLB Safe)", "#f59e0b", steps,
                            "#1a1400", "#3d2e00", left_accent="#f59e0b"
                        ), unsafe_allow_html=True)

                    with c_vd:
                        vd_html = f'<div style="font-size:12px;color:#c4b5fd;line-height:1.7;">{vd or "—"}</div>'
                        st.markdown(section_box(
                            "🎨 Visual Description", "#a78bfa", vd_html,
                            "#120d1a", "#2d1a4a", left_accent="#a78bfa"
                        ), unsafe_allow_html=True)

                if gen_img:
                    provider = "Gemini 3.1 Flash" if GEMINI_API_KEY else "Pollinations Flux"
                    with st.spinner(f"Generating 3D storyboard frame for Scene {snum:02d} via {provider}…"):
                        b64 = generate_scene_image(sc)
                    if b64:
                        scenes[i]["scene_image"] = b64
                        save_scenes(scenes)
                        st.success(f"✓ 3D storyboard frame generated for Scene {snum:02d}!")
                        st.rerun()

                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                _, dc = st.columns([8, 1])
                with dc:
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
        c_exp, c_imp = st.columns(2)

        with c_exp:
            st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:0.12em;color:#475569;text-transform:uppercase;margin-bottom:0.75rem;">Export</div>', unsafe_allow_html=True)
            if scenes:
                # Clean export copy
                export_scenes = []
                for sc in scenes:
                    e = dict(sc)
                    if "assets" not in e:
                        e["assets"] = e.pop("required_assets", e.pop("models_3d", []))
                    e.pop("required_assets", None)
                    e.pop("models_3d", None)
                    e.setdefault("labels", [])
                    export_scenes.append(e)

                inc_imgs = st.checkbox("Include generated images in JSON export", value=False)
                if not inc_imgs:
                    export_no_img = [dict(e) for e in export_scenes]
                    for e in export_no_img:
                        e.pop("scene_image", None)
                else:
                    export_no_img = export_scenes

                payload_out = {"name": active_sb["name"], "created": active_sb.get("created",""), "scenes": export_no_img}

                # ── JSON Export
                st.download_button(
                    "📥 Download Storyboard JSON",
                    data=json.dumps(payload_out, indent=2),
                    file_name=f"{active_sb['name'].replace(' ','_')}_storyboard.json",
                    mime="application/json",
                    use_container_width=True
                )

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                # ── PDF Export
                st.markdown("""
                <div style="font-size:10px;color:#475569;margin-bottom:6px;">
                  PDF export includes all scene data + generated images (if any).
                  Requires <code>reportlab</code> and <code>Pillow</code>.
                </div>
                """, unsafe_allow_html=True)

                if st.button("📄 Generate PDF Storyboard", key="gen_pdf_btn", use_container_width=True):
                    with st.spinner("Building PDF storyboard…"):
                        pdf_bytes, pdf_err = generate_storyboard_pdf(active_sb["name"], scenes)
                    if pdf_bytes:
                        st.session_state["_pdf_bytes"] = pdf_bytes
                        st.session_state["_pdf_name"]  = active_sb["name"]
                        st.success(f"✓ PDF ready — {len(pdf_bytes)//1024} KB")
                        st.rerun()
                    else:
                        st.error(f"PDF generation failed: {pdf_err}")

                if "_pdf_bytes" in st.session_state and st.session_state.get("_pdf_name") == active_sb["name"]:
                    st.download_button(
                        "⬇️ Download PDF",
                        data=st.session_state["_pdf_bytes"],
                        file_name=f"{active_sb['name'].replace(' ','_')}_storyboard.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                st.markdown("---")
                st.markdown("**Scene Table Preview**")
                hdr  = "| # | Title | Assets | Labels | Narration |"
                sep2 = "|---|-------|--------|--------|-----------|"
                rows_md = [
                    f"| {s.get('scene_number','?')} | {s.get('title','')} "
                    f"| {', '.join(get_scene_assets(s))} "
                    f"| {', '.join(s.get('labels',[]))} "
                    f"| {s.get('narration','')[:80]}{'…' if len(s.get('narration',''))>80 else ''} |"
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
                        st.error("Unrecognised format.")
                        imp_sc = []
                    if imp_sc:
                        if st.button("⬆ Apply Imported Scenes", key="apply_import"):
                            save_scenes(imp_sc)
                            st.session_state.editing_scene = None
                            st.session_state.goto_editor   = True
                            st.rerun()
                except Exception as e:
                    st.error(f"Parse error: {e}")
