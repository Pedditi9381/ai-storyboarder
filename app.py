import base64
import io
import json
import re
import time
import uuid
from datetime import datetime

import PyPDF2
import requests
import streamlit as st


st.set_page_config(
    page_title="LPVision Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

:root {
  --bg: #07080c;
  --surface: #101218;
  --surface-2: #171a22;
  --surface-3: #202532;
  --line: #2a3040;
  --line-strong: #3a4356;
  --text: #eef2ff;
  --muted: #9aa4b8;
  --faint: #687187;
  --blue: #6ea8ff;
  --cyan: #50d5c8;
  --green: #6bd98d;
  --amber: #f3bd5b;
  --red: #ff7f86;
  --violet: #b99bff;
  --font: "Inter", system-ui, sans-serif;
  --mono: "JetBrains Mono", monospace;
}

* { box-sizing: border-box; }
html, body, [class*="css"] {
  background: var(--bg) !important;
  color: var(--text);
  font-family: var(--font);
}

#MainMenu, footer, header { visibility: hidden; }
.main { background: var(--bg) !important; }
.block-container {
  max-width: 1440px !important;
  padding: 1.1rem 1.4rem 3rem !important;
}

section[data-testid="stSidebar"] {
  background: #0d0f15 !important;
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] .block-container {
  padding: 1rem .85rem !important;
}

h1, h2, h3, p { margin: 0; }
label {
  color: var(--faint) !important;
  font: 700 10px/1.3 var(--mono) !important;
  letter-spacing: .08em !important;
  text-transform: uppercase !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  border-radius: 8px !important;
  box-shadow: none !important;
}
.stTextArea textarea:focus,
.stTextInput input:focus,
.stNumberInput input:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 2px rgba(110,168,255,.16) !important;
}

.stButton > button,
.stDownloadButton > button {
  min-height: 36px;
  background: var(--surface-2) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  border-radius: 8px !important;
  font: 700 12px/1 var(--font) !important;
  transition: .15s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
  background: var(--surface-3) !important;
  border-color: var(--blue) !important;
  color: #fff !important;
}

[data-testid="stFileUploadDropzone"] {
  background: var(--surface) !important;
  border: 1px dashed var(--line-strong) !important;
  border-radius: 8px !important;
}

.streamlit-expanderHeader {
  background: var(--surface-2) !important;
  border: 1px solid var(--line) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-weight: 700 !important;
}
.streamlit-expanderContent {
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  border-top: 0 !important;
  border-radius: 0 0 8px 8px !important;
}
.stAlert {
  background: var(--surface-2) !important;
  border: 1px solid var(--line) !important;
  border-radius: 8px !important;
}
hr { border-color: var(--line) !important; }

.brand {
  padding: .35rem 0 1rem;
  border-bottom: 1px solid var(--line);
  margin-bottom: .9rem;
}
.brand-title {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -.01em;
}
.brand-sub {
  color: var(--faint);
  font: 700 10px/1.8 var(--mono);
  letter-spacing: .14em;
  text-transform: uppercase;
}
.api-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 5px 9px;
  color: var(--muted);
  font: 700 10px/1 var(--mono);
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--red);
}
.dot.ok { background: var(--green); }

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: .75rem 0 1rem;
  border-bottom: 1px solid var(--line);
  margin-bottom: 1rem;
}
.crumb {
  color: var(--faint);
  font: 700 11px/1 var(--mono);
  text-transform: uppercase;
  letter-spacing: .08em;
}
.page-title {
  margin-top: 6px;
  font-size: 24px;
  line-height: 1.1;
  font-weight: 800;
  letter-spacing: -.02em;
}
.metric-line {
  color: var(--muted);
  font: 700 11px/1 var(--mono);
}

.tab-note {
  color: var(--faint);
  font-size: 12px;
  margin-top: -4px;
  margin-bottom: 10px;
}

div[role="radiogroup"] {
  gap: 6px;
  border-bottom: 1px solid var(--line);
  margin: -2px 0 14px;
  padding-bottom: 10px;
}
div[role="radiogroup"] label {
  min-height: 34px;
  padding: 0 13px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
  color: var(--muted) !important;
  font: 800 11px/1 var(--mono) !important;
  letter-spacing: .06em !important;
}
div[role="radiogroup"] label:has(input:checked) {
  background: #162033;
  border-color: #31568a;
  color: var(--text) !important;
}

.empty-state {
  border: 1px dashed var(--line-strong);
  background: var(--surface);
  border-radius: 10px;
  padding: 3rem 1.2rem;
  text-align: center;
  color: var(--muted);
}
.empty-state strong {
  display: block;
  color: var(--text);
  font-size: 15px;
  margin-bottom: 6px;
}

.scene-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: .85rem;
  margin-bottom: .8rem;
}
.scene-head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.scene-num {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: #17223a;
  color: var(--blue);
  border: 1px solid #26426f;
  font: 800 12px/1 var(--mono);
}
.scene-title {
  font-size: 16px;
  font-weight: 800;
}
.scene-meta {
  color: var(--faint);
  font: 700 10px/1.7 var(--mono);
  text-transform: uppercase;
  letter-spacing: .06em;
}
.panel {
  height: 100%;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: .7rem .75rem;
}
.panel-label {
  color: var(--faint);
  font: 800 10px/1 var(--mono);
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-bottom: 8px;
}
.panel-body {
  color: var(--muted);
  font-size: 12.5px;
  line-height: 1.65;
}
.narration {
  color: #ffdbe0;
  font-style: italic;
}
.chip {
  display: inline-flex;
  align-items: center;
  margin: 0 5px 5px 0;
  padding: 4px 8px;
  border-radius: 999px;
  background: #17223a;
  color: var(--blue);
  font: 700 11px/1 var(--mono);
}
.chip.green {
  background: #10251b;
  color: var(--green);
}
.img-frame {
  width: 100%;
  overflow: hidden;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: #07080c;
}
.img-frame img {
  display: block;
  width: 100%;
}
.placeholder {
  height: 170px;
  display: grid;
  place-items: center;
  color: var(--faint);
  border: 1px dashed var(--line-strong);
  border-radius: 8px;
  background: var(--surface-2);
  font: 700 11px/1 var(--mono);
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


OPENAI_URL = "https://api.openai.com/v1/responses"
IMAGE_URL = "https://api.openai.com/v1/images/generations"


def now_label():
    return datetime.now().strftime("%b %d, %Y")


def init_state():
    if "projects" not in st.session_state:
        pid = str(uuid.uuid4())
        st.session_state.projects = {
            pid: {
                "name": "My First Project",
                "created": now_label(),
                "storyboards": {},
            }
        }
    defaults = {
        "active_project": None,
        "active_sb": None,
        "active_tab": "Storyboards",
        "editing_scene": None,
        "image_model": "gpt-image-1.5",
        "text_model": "gpt-5-mini",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    if not st.session_state.active_project:
        st.session_state.active_project = next(iter(st.session_state.projects))


init_state()


def secret(name):
    try:
        return st.secrets.get(name)
    except Exception:
        return None


def openai_key():
    return secret("OPENAI_API_KEY") or st.session_state.get("openai_key", "").strip()


def openai_headers():
    return {
        "Authorization": f"Bearer {openai_key()}",
        "Content-Type": "application/json",
    }


def active_project():
    return st.session_state.projects[st.session_state.active_project]


def active_storyboard():
    sid = st.session_state.active_sb
    if not sid:
        return None
    return active_project().get("storyboards", {}).get(sid)


def save_scenes(scenes):
    pid = st.session_state.active_project
    sid = st.session_state.active_sb
    st.session_state.projects[pid]["storyboards"][sid]["scenes"] = renumber_scenes(scenes)


def renumber_scenes(scenes):
    for idx, scene in enumerate(scenes, start=1):
        scene["scene_number"] = idx
        scene.setdefault("assets", [])
        scene.setdefault("labels", [])
        scene.setdefault("animation", "")
        scene.setdefault("visual_description", "")
        scene.setdefault("narration", "")
        scene.setdefault("scene_image", None)
    return scenes


def assets(scene):
    return scene.get("assets") or scene.get("required_assets") or scene.get("models_3d") or []


def clean_json_text(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def response_text(payload):
    if not openai_key():
        raise RuntimeError("Add OPENAI_API_KEY in Streamlit secrets or the sidebar.")
    response = requests.post(
        OPENAI_URL,
        headers=openai_headers(),
        json=payload,
        timeout=90,
    )
    if response.status_code >= 400:
        try:
            msg = response.json().get("error", {}).get("message", response.text)
        except Exception:
            msg = response.text
        raise RuntimeError(f"OpenAI API error {response.status_code}: {msg}")
    data = response.json()
    if data.get("output_text"):
        return data["output_text"]
    parts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                parts.append(content.get("text", ""))
    return "\n".join(parts).strip()


def storyboard_schema():
    scene = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "scene_number",
            "title",
            "assets",
            "labels",
            "animation",
            "visual_description",
            "narration",
        ],
        "properties": {
            "scene_number": {"type": "integer"},
            "title": {"type": "string"},
            "assets": {
                "type": "array",
                "minItems": 2,
                "maxItems": 5,
                "items": {"type": "string"},
            },
            "labels": {
                "type": "array",
                "minItems": 1,
                "maxItems": 5,
                "items": {"type": "string"},
            },
            "animation": {"type": "string"},
            "visual_description": {"type": "string"},
            "narration": {"type": "string"},
        },
    }
    return {
        "type": "json_schema",
        "name": "storyboard_scenes",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["scenes"],
            "properties": {
                "scenes": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 15,
                    "items": scene,
                }
            },
        },
    }


def generate_scenes(source_text, count, auto_count):
    count_rule = (
        "Choose the best number of scenes from 4 to 15 based on the source."
        if auto_count
        else f"Create exactly {count} scenes."
    )
    prompt = f"""
You are ChatGPT acting as a senior educational storyboard writer and 3D animation planner.

{count_rule}

Use only the supplied source material for facts, names, dates, claims, and narration.
Make each scene clear enough for a visual production team.

Scene requirements:
- title: 3 to 7 words
- assets: 2 to 5 snake_case .glb file names
- labels: 1 to 5 short on-screen labels
- animation: numbered steps separated by new lines
- visual_description: vivid 3D render direction
- narration: 1 or 2 short sentences, faithful to the source

Source material:
{source_text[:12000]}
""".strip()

    payload = {
        "model": st.session_state.text_model,
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            }
        ],
        "text": {"format": storyboard_schema()},
    }
    raw = response_text(payload)
    data = json.loads(clean_json_text(raw))
    return renumber_scenes(data.get("scenes", []))


def extract_image_text(b64_image, mime_type):
    prompt = """
Extract all educational content visible in this image.
Include text, labels, dates, names, concepts, process steps, formulas, and diagram structure.
Return concise plain text that can be used to create a storyboard.
""".strip()
    payload = {
        "model": st.session_state.text_model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{b64_image}",
                    },
                ],
            }
        ],
    }
    return response_text(payload)


def image_prompt(scene):
    anim = scene.get("animation", "").replace("\\n", "\n")
    return f"""
Create a clean cinematic 3D educational storyboard frame.

Scene title: {scene.get("title", "")}
Narration context: {scene.get("narration", "")}
Animation moment: {anim}
Visual direction: {scene.get("visual_description", "")}
Objects/assets to represent: {", ".join(assets(scene))}
Labels to imply visually without text: {", ".join(scene.get("labels", []))}

Style:
- photorealistic 3D CGI
- clear subject hierarchy
- realistic materials and lighting
- dark neutral studio background
- educational, polished, premium
- 16:9 composition

Do not include readable text, captions, watermarks, logos, or UI.
""".strip()


def generate_image(scene):
    if not openai_key():
        raise RuntimeError("Add OPENAI_API_KEY in Streamlit secrets or the sidebar.")
    payload = {
        "model": st.session_state.image_model,
        "prompt": image_prompt(scene),
        "size": "1536x1024",
        "quality": "medium",
        "n": 1,
    }
    response = requests.post(
        IMAGE_URL,
        headers=openai_headers(),
        json=payload,
        timeout=150,
    )
    if response.status_code >= 400:
        try:
            msg = response.json().get("error", {}).get("message", response.text)
        except Exception:
            msg = response.text
        raise RuntimeError(f"OpenAI image error {response.status_code}: {msg}")
    item = response.json().get("data", [{}])[0]
    if item.get("b64_json"):
        return item["b64_json"]
    if item.get("url"):
        img = requests.get(item["url"], timeout=90)
        img.raise_for_status()
        return base64.b64encode(img.content).decode("utf-8")
    raise RuntimeError("OpenAI returned no image data.")


def pdf_export(storyboard_name, scenes):
    try:
        from PIL import Image as PILImage
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except Exception as exc:
        return None, f"Install reportlab and Pillow to export PDF. {exc}"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=13 * mm,
        rightMargin=13 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )
    style = ParagraphStyle(
        "base",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#eef2ff"),
    )
    title_style = ParagraphStyle(
        "title",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#eef2ff"),
        spaceAfter=8,
    )
    small_style = ParagraphStyle(
        "small",
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#9aa4b8"),
    )
    story = [
        Paragraph("LPVision Studio", title_style),
        Paragraph(f"{storyboard_name} · {len(scenes)} scenes · {datetime.now().strftime('%B %d, %Y')}", small_style),
        Spacer(1, 7),
    ]

    for scene in scenes:
        image_cell = Paragraph("No image", small_style)
        if scene.get("scene_image"):
            try:
                img_bytes = io.BytesIO(base64.b64decode(scene["scene_image"]))
                opened = PILImage.open(img_bytes)
                png = io.BytesIO()
                opened.save(png, "PNG")
                png.seek(0)
                image_cell = Image(png, width=66 * mm, height=44 * mm)
            except Exception:
                image_cell = Paragraph("Image error", small_style)

        details = [
            Paragraph(f"<b>Scene {scene.get('scene_number')}: {scene.get('title', '')}</b>", style),
            Paragraph(f"<b>Assets:</b> {', '.join(assets(scene)) or '-'}", style),
            Paragraph(f"<b>Labels:</b> {', '.join(scene.get('labels', [])) or '-'}", style),
            Paragraph(f"<b>Narration:</b> {scene.get('narration', '-')}", style),
            Paragraph(f"<b>Animation:</b><br/>{scene.get('animation', '-').replace(chr(10), '<br/>')}", style),
            Paragraph(f"<b>Visual:</b> {scene.get('visual_description', '-')}", style),
        ]
        table = Table([[image_cell, details]], colWidths=[70 * mm, 180 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#101218")),
                    ("BOX", (0, 0), (-1, -1), .7, colors.HexColor("#2a3040")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        story.extend([table, Spacer(1, 6)])

    def background(canvas, _doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#07080c"))
        canvas.rect(0, 0, landscape(A4)[0], landscape(A4)[1], fill=True, stroke=False)
        canvas.restoreState()

    doc.build(story, onFirstPage=background, onLaterPages=background)
    buffer.seek(0)
    return buffer.getvalue(), None


def chip_html(values, color="blue"):
    css_class = "chip green" if color == "green" else "chip"
    if not values:
        return '<span class="panel-body">None</span>'
    return "".join(f'<span class="{css_class}">{value}</span>' for value in values)


def panel(label, body, extra_class=""):
    return f"""
    <div class="panel">
      <div class="panel-label">{label}</div>
      <div class="panel-body {extra_class}">{body}</div>
    </div>
    """


def read_pdf(upload):
    reader = PyPDF2.PdfReader(upload)
    chunks = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks).strip()


def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="brand">
              <div class="brand-sub">LearningPad</div>
              <div class="brand-title">LPVision Studio</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        key_ok = bool(openai_key())
        st.markdown(
            f"""
            <div class="api-pill">
              <span class="dot {'ok' if key_ok else ''}"></span>
              OpenAI API {'connected' if key_ok else 'missing'}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not secret("OPENAI_API_KEY"):
            st.text_input(
                "OpenAI API Key",
                type="password",
                key="openai_key",
                placeholder="sk-...",
            )

        st.markdown("---")
        st.session_state.text_model = st.text_input(
            "ChatGPT model",
            value=st.session_state.text_model,
            help="Used for storyboards, scripts, and image text extraction.",
        )
        st.session_state.image_model = st.text_input(
            "Image model",
            value=st.session_state.image_model,
            help="Used for OpenAI image generation.",
        )

        st.markdown("---")
        st.caption("Projects")
        with st.expander("New project"):
            name = st.text_input("Project name", key="new_project_name")
            if st.button("Create project", use_container_width=True):
                if name.strip():
                    pid = str(uuid.uuid4())
                    st.session_state.projects[pid] = {
                        "name": name.strip(),
                        "created": now_label(),
                        "storyboards": {},
                    }
                    st.session_state.active_project = pid
                    st.session_state.active_sb = None
                    st.session_state.active_tab = "Storyboards"
                    st.rerun()

        for pid, project in st.session_state.projects.items():
            prefix = "• " if pid == st.session_state.active_project else ""
            label = f"{prefix}{project['name']} ({len(project.get('storyboards', {}))})"
            if st.button(label, key=f"project_{pid}", use_container_width=True):
                st.session_state.active_project = pid
                st.session_state.active_sb = None
                st.session_state.active_tab = "Storyboards"
                st.rerun()


sidebar()

project = active_project()
storyboards = project.get("storyboards", {})
storyboard = active_storyboard()
page_title = storyboard["name"] if storyboard else "Select or create a storyboard"

st.markdown(
    f"""
    <div class="topbar">
      <div>
        <div class="crumb">{project.get('name', 'Project')}</div>
        <div class="page-title">{page_title}</div>
      </div>
      <div class="metric-line">{len(storyboards)} storyboard{'s' if len(storyboards) != 1 else ''}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav_options = ["Storyboards", "Editor", "Export"]
if st.session_state.active_tab not in nav_options:
    st.session_state.active_tab = "Storyboards"

nav = st.radio(
    "Workspace navigation",
    nav_options,
    horizontal=True,
    key="active_tab",
    label_visibility="collapsed",
)


if nav == "Storyboards":
    st.markdown('<div class="tab-note">Create, import, open, and organize your storyboards.</div>', unsafe_allow_html=True)
    left, right = st.columns([.42, .58])
    with left:
        with st.container(border=True):
            new_name = st.text_input("Storyboard name", placeholder="e.g. Photosynthesis Chapter")
            if st.button("Create storyboard", type="primary", use_container_width=True):
                sid = str(uuid.uuid4())
                project["storyboards"][sid] = {
                    "name": new_name.strip() or f"Storyboard {len(storyboards) + 1}",
                    "created": now_label(),
                    "scenes": [],
                }
                st.session_state.active_sb = sid
                st.session_state.active_tab = "Editor"
                st.rerun()
            uploaded_json = st.file_uploader("Import storyboard JSON", type=["json"])
            if uploaded_json:
                try:
                    data = json.load(uploaded_json)
                    scenes = data if isinstance(data, list) else data.get("scenes", [])
                    if not isinstance(scenes, list):
                        raise ValueError("JSON must be a scene array or contain a scenes array.")
                    sid = str(uuid.uuid4())
                    project["storyboards"][sid] = {
                        "name": data.get("name", uploaded_json.name.replace(".json", "")) if isinstance(data, dict) else uploaded_json.name.replace(".json", ""),
                        "created": now_label(),
                        "scenes": renumber_scenes(scenes),
                    }
                    st.session_state.active_sb = sid
                    st.success("Storyboard imported.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Import failed: {exc}")

    with right:
        if not storyboards:
            st.markdown(
                '<div class="empty-state"><strong>No storyboards yet</strong>Create one on the left to start.</div>',
                unsafe_allow_html=True,
            )
        for sid, item in storyboards.items():
            scenes = item.get("scenes", [])
            image_count = sum(1 for scene in scenes if scene.get("scene_image"))
            c1, c2, c3 = st.columns([.7, .18, .12])
            with c1:
                active = "Active" if sid == st.session_state.active_sb else "Storyboard"
                st.markdown(
                    f"""
                    <div class="scene-card">
                      <div class="scene-title">{item.get('name', 'Untitled')}</div>
                      <div class="scene-meta">{active} | {len(scenes)} scenes | {image_count} images | {item.get('created', '')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c2:
                if st.button("Open", key=f"open_{sid}", use_container_width=True):
                    st.session_state.active_sb = sid
                    st.rerun()
            with c3:
                if st.button("Delete", key=f"delete_sb_{sid}", use_container_width=True):
                    del project["storyboards"][sid]
                    if st.session_state.active_sb == sid:
                        st.session_state.active_sb = None
                    st.rerun()


elif nav == "Editor":
    storyboard = active_storyboard()
    if not storyboard:
        st.info("Open or create a storyboard first.")
    else:
        scenes = storyboard.get("scenes", [])

        with st.expander("Generate scenes with ChatGPT", expanded=not scenes):
            c1, c2 = st.columns([.4, .6])
            with c1:
                source_type = st.radio("Source", ["Plain text", "PDF", "Image"], horizontal=True)
                auto_count = st.checkbox("Auto scene count", value=False)
                scene_count = 6 if auto_count else st.slider("Scenes", 3, 15, 6)
                auto_images = st.checkbox("Generate images after scenes", value=False)
            with c2:
                source_text = ""
                image_b64 = None
                image_mime = "image/png"
                if source_type == "Plain text":
                    source_text = st.text_area("Source content", height=190, placeholder="Paste lesson notes, textbook content, or a script.")
                elif source_type == "PDF":
                    pdf = st.file_uploader("Upload PDF", type=["pdf"])
                    if pdf:
                        source_text = read_pdf(pdf)
                        st.success(f"Extracted {len(source_text)} characters.")
                else:
                    image_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg", "webp"])
                    if image_file:
                        image_mime = image_file.type or "image/png"
                        image_b64 = base64.b64encode(image_file.getvalue()).decode("utf-8")
                        st.image(image_file, use_container_width=True)

            if st.button("Generate storyboard", type="primary", use_container_width=True):
                try:
                    final_text = source_text.strip()
                    if source_type == "Image":
                        if not image_b64:
                            st.warning("Upload an image first.")
                            st.stop()
                        with st.spinner("ChatGPT is extracting image content..."):
                            final_text = extract_image_text(image_b64, image_mime)
                    if not final_text:
                        st.warning("Add source content first.")
                        st.stop()
                    with st.spinner("ChatGPT is creating storyboard scenes..."):
                        new_scenes = generate_scenes(final_text, scene_count, auto_count)
                    if not new_scenes:
                        st.error("No scenes were returned.")
                        st.stop()
                    save_scenes(new_scenes)
                    scenes = active_storyboard().get("scenes", [])
                    st.success(f"Created {len(scenes)} scenes.")
                    if auto_images:
                        bar = st.progress(0, "Generating images with OpenAI...")
                        for idx, scene in enumerate(scenes):
                            scene["scene_image"] = generate_image(scene)
                            save_scenes(scenes)
                            bar.progress(int((idx + 1) / len(scenes) * 100), f"Image {idx + 1}/{len(scenes)}")
                            time.sleep(.1)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

        with st.expander("Add scene manually"):
            a, b = st.columns(2)
            with a:
                title = st.text_input("Title", key="manual_title")
                asset_text = st.text_input("Assets", key="manual_assets", placeholder="cell.glb, nucleus.glb")
                label_text = st.text_input("Labels", key="manual_labels")
            with b:
                narration = st.text_area("Narration", key="manual_narration", height=96)
                visual = st.text_area("Visual description", key="manual_visual", height=68)
            animation = st.text_area("Animation steps", key="manual_animation", height=76)
            image_upload = st.file_uploader("Optional scene image", type=["png", "jpg", "jpeg", "webp"], key="manual_image")
            if st.button("Add scene"):
                if not title.strip():
                    st.warning("Enter a title.")
                else:
                    scenes.append(
                        {
                            "scene_number": len(scenes) + 1,
                            "title": title.strip(),
                            "assets": [x.strip() for x in asset_text.split(",") if x.strip()],
                            "labels": [x.strip() for x in label_text.split(",") if x.strip()],
                            "animation": animation.strip(),
                            "visual_description": visual.strip(),
                            "narration": narration.strip(),
                            "scene_image": base64.b64encode(image_upload.getvalue()).decode("utf-8") if image_upload else None,
                        }
                    )
                    save_scenes(scenes)
                    st.rerun()

        if not scenes:
            st.markdown(
                '<div class="empty-state"><strong>No scenes yet</strong>Generate scenes with ChatGPT or add one manually.</div>',
                unsafe_allow_html=True,
            )
        else:
            summary, actions = st.columns([.72, .28])
            with summary:
                image_count = sum(1 for scene in scenes if scene.get("scene_image"))
                st.markdown(
                    f'<div class="metric-line">{len(scenes)} scenes | {image_count} images | {len(scenes) - image_count} missing images</div>',
                    unsafe_allow_html=True,
                )
            with actions:
                if st.button("Generate missing images", use_container_width=True):
                    try:
                        targets = [idx for idx, scene in enumerate(scenes) if not scene.get("scene_image")]
                        if not targets:
                            targets = list(range(len(scenes)))
                        bar = st.progress(0, "Generating images with OpenAI...")
                        for step, idx in enumerate(targets):
                            scenes[idx]["scene_image"] = generate_image(scenes[idx])
                            save_scenes(scenes)
                            bar.progress(int((step + 1) / len(targets) * 100), f"Image {step + 1}/{len(targets)}")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

            for idx, scene in enumerate(scenes):
                editing = st.session_state.editing_scene == idx
                st.markdown('<div class="scene-card">', unsafe_allow_html=True)
                h1, h2 = st.columns([.72, .28])
                with h1:
                    st.markdown(
                        f"""
                        <div class="scene-head">
                          <div class="scene-num">{scene.get('scene_number', idx + 1):02d}</div>
                          <div>
                            <div class="scene-title">{scene.get('title', 'Untitled')}</div>
                            <div class="scene-meta">{len(assets(scene))} assets | {len(scene.get('labels', []))} labels</div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with h2:
                    e1, e2, e3, e4, e5, e6 = st.columns(6)
                    with e1:
                        if st.button("Up", key=f"up_{idx}", use_container_width=True, disabled=idx == 0):
                            scenes[idx - 1], scenes[idx] = scenes[idx], scenes[idx - 1]
                            save_scenes(scenes)
                            st.rerun()
                    with e2:
                        if st.button("Down", key=f"down_{idx}", use_container_width=True, disabled=idx == len(scenes) - 1):
                            scenes[idx + 1], scenes[idx] = scenes[idx], scenes[idx + 1]
                            save_scenes(scenes)
                            st.rerun()
                    with e3:
                        if st.button("Copy", key=f"copy_{idx}", use_container_width=True):
                            duplicate = json.loads(json.dumps(scene))
                            duplicate["title"] = f"{duplicate.get('title', 'Scene')} Copy"
                            scenes.insert(idx + 1, duplicate)
                            save_scenes(scenes)
                            st.rerun()
                    with e4:
                        if st.button("Edit" if not editing else "Close", key=f"edit_{idx}", use_container_width=True):
                            st.session_state.editing_scene = None if editing else idx
                            st.rerun()
                    with e5:
                        if st.button("Image", key=f"img_{idx}", use_container_width=True):
                            try:
                                with st.spinner("Generating image with OpenAI..."):
                                    scenes[idx]["scene_image"] = generate_image(scene)
                                    save_scenes(scenes)
                                st.rerun()
                            except Exception as exc:
                                st.error(str(exc))
                    with e6:
                        if st.button("Delete", key=f"del_{idx}", use_container_width=True):
                            scenes.pop(idx)
                            save_scenes(scenes)
                            st.session_state.editing_scene = None
                            st.rerun()

                if editing:
                    st.markdown("---")
                    e_left, e_right = st.columns(2)
                    with e_left:
                        new_title = st.text_input("Title", value=scene.get("title", ""), key=f"title_{idx}")
                        new_assets = st.text_input("Assets", value=", ".join(assets(scene)), key=f"assets_{idx}")
                        new_labels = st.text_input("Labels", value=", ".join(scene.get("labels", [])), key=f"labels_{idx}")
                    with e_right:
                        new_narration = st.text_area("Narration", value=scene.get("narration", ""), key=f"narration_{idx}", height=96)
                        new_visual = st.text_area("Visual description", value=scene.get("visual_description", ""), key=f"visual_{idx}", height=68)
                    new_animation = st.text_area("Animation", value=scene.get("animation", ""), key=f"animation_{idx}", height=86)
                    replacement = st.file_uploader("Replace image", type=["png", "jpg", "jpeg", "webp"], key=f"replace_{idx}")
                    c_save, c_clear, _ = st.columns([.15, .15, .7])
                    with c_save:
                        if st.button("Save", key=f"save_{idx}", use_container_width=True):
                            scene.update(
                                {
                                    "title": new_title.strip(),
                                    "assets": [x.strip() for x in new_assets.split(",") if x.strip()],
                                    "labels": [x.strip() for x in new_labels.split(",") if x.strip()],
                                    "narration": new_narration.strip(),
                                    "visual_description": new_visual.strip(),
                                    "animation": new_animation.strip(),
                                }
                            )
                            if replacement:
                                scene["scene_image"] = base64.b64encode(replacement.getvalue()).decode("utf-8")
                            save_scenes(scenes)
                            st.session_state.editing_scene = None
                            st.rerun()
                    with c_clear:
                        if scene.get("scene_image") and st.button("Clear image", key=f"clear_{idx}", use_container_width=True):
                            scene["scene_image"] = None
                            save_scenes(scenes)
                            st.rerun()
                else:
                    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                    i_col, a_col, l_col, n_col = st.columns([.26, .22, .22, .30])
                    with i_col:
                        if scene.get("scene_image"):
                            st.markdown(
                                f'<div class="img-frame"><img src="data:image/png;base64,{scene["scene_image"]}"></div>',
                                unsafe_allow_html=True,
                            )
                            st.download_button(
                                "Download PNG",
                                base64.b64decode(scene["scene_image"]),
                                file_name=f"scene_{scene.get('scene_number', idx + 1):02d}.png",
                                mime="image/png",
                                key=f"download_img_{idx}",
                                use_container_width=True,
                            )
                        else:
                            st.markdown('<div class="placeholder">No image</div>', unsafe_allow_html=True)
                    with a_col:
                        st.markdown(panel("Assets", chip_html(assets(scene))), unsafe_allow_html=True)
                    with l_col:
                        st.markdown(panel("Labels", chip_html(scene.get("labels", []), "green")), unsafe_allow_html=True)
                    with n_col:
                        st.markdown(panel("Narration", scene.get("narration", "None"), "narration"), unsafe_allow_html=True)
                    a2, b2 = st.columns(2)
                    with a2:
                        st.markdown(panel("Animation", scene.get("animation", "None").replace("\n", "<br>")), unsafe_allow_html=True)
                    with b2:
                        st.markdown(panel("Visual Direction", scene.get("visual_description", "None")), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)


elif nav == "Export":
    storyboard = active_storyboard()
    if not storyboard:
        st.info("Open a storyboard first.")
    else:
        scenes = storyboard.get("scenes", [])
        export_col, import_col = st.columns(2)
        with export_col:
            st.subheader("Export")
            if not scenes:
                st.info("No scenes to export.")
            else:
                include_images = st.checkbox("Include images in JSON", value=False)
                export_scenes = []
                for scene in scenes:
                    item = dict(scene)
                    item["assets"] = assets(item)
                    item.pop("required_assets", None)
                    item.pop("models_3d", None)
                    if not include_images:
                        item.pop("scene_image", None)
                    export_scenes.append(item)
                st.download_button(
                    "Download JSON",
                    json.dumps(
                        {
                            "name": storyboard["name"],
                            "created": storyboard.get("created", ""),
                            "scenes": export_scenes,
                        },
                        indent=2,
                    ),
                    file_name=f"{storyboard['name'].replace(' ', '_')}_storyboard.json",
                    mime="application/json",
                    use_container_width=True,
                )
                if st.button("Build PDF", use_container_width=True):
                    with st.spinner("Building PDF..."):
                        pdf, err = pdf_export(storyboard["name"], scenes)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.pdf_bytes = pdf
                        st.session_state.pdf_name = storyboard["name"]
                        st.success("PDF ready.")
                if st.session_state.get("pdf_bytes") and st.session_state.get("pdf_name") == storyboard["name"]:
                    st.download_button(
                        "Download PDF",
                        st.session_state.pdf_bytes,
                        file_name=f"{storyboard['name'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                rows = [
                    {
                        "#": scene.get("scene_number", idx + 1),
                        "Title": scene.get("title", ""),
                        "Assets": ", ".join(assets(scene)),
                        "Labels": ", ".join(scene.get("labels", [])),
                        "Image": "Yes" if scene.get("scene_image") else "No",
                    }
                    for idx, scene in enumerate(scenes)
                ]
                st.dataframe(rows, use_container_width=True, hide_index=True)

        with import_col:
            st.subheader("Import into active storyboard")
            upload = st.file_uploader("Choose JSON", type=["json"], key="export_import_json")
            if upload:
                try:
                    data = json.load(upload)
                    imported = data if isinstance(data, list) else data.get("scenes", [])
                    if not isinstance(imported, list):
                        raise ValueError("JSON must be a scene array or contain scenes.")
                    if st.button("Replace current scenes", use_container_width=True):
                        save_scenes(imported)
                        st.rerun()
                except Exception as exc:
                    st.error(f"Import failed: {exc}")
