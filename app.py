import base64
import hashlib
import io
import json
import re
import time
import uuid
import zipfile
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


FREE_MODE_NOTE = "Free mode: no API key. Images use public AI models with local fallback."
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"
POLLINATION_MODELS = {
    "Best quality": ["seedream", "flux", "turbo"],
    "Photoreal": ["flux", "seedream", "turbo"],
    "Fast": ["turbo", "flux", "seedream"],
}


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
        "nav_choice": "Storyboards",
        "editing_scene": None,
        "image_quality": "Best quality",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    if not st.session_state.active_project:
        st.session_state.active_project = next(iter(st.session_state.projects))


init_state()


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


STOP_WORDS = {
    "about", "after", "again", "also", "because", "before", "between", "could",
    "every", "first", "from", "have", "into", "like", "more", "most", "only",
    "other", "over", "such", "than", "that", "their", "there", "these", "this",
    "through", "under", "using", "were", "when", "where", "which", "while",
    "with", "within", "without", "would", "your",
}


def split_sentences(text):
    cleaned = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    return [part.strip() for part in parts if len(part.strip()) > 8]


def chunk_sentences(sentences, count):
    if not sentences:
        return []
    count = max(1, min(count, len(sentences)))
    size = max(1, round(len(sentences) / count))
    chunks = []
    for idx in range(0, len(sentences), size):
        chunks.append(sentences[idx: idx + size])
    while len(chunks) > count:
        chunks[-2].extend(chunks.pop())
    return chunks


def keywords(text, limit=5):
    words = re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", text.lower())
    counts = {}
    for word in words:
        if word in STOP_WORDS:
            continue
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts, key=lambda word: (-counts[word], word))
    return ranked[:limit]


def title_from_text(text, fallback):
    found = keywords(text, 4)
    if not found:
        return fallback
    return " ".join(word.capitalize() for word in found[:4])


def asset_name(word):
    safe = re.sub(r"[^a-z0-9]+", "_", word.lower()).strip("_")
    return f"{safe or 'concept'}_model.glb"


def concise_source_excerpt(text, limit=320):
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    cut = cleaned[:limit].rsplit(" ", 1)[0].rstrip(".,;:")
    return f"{cut}..."


def visual_description_for_scene(title, body, labels):
    excerpt = concise_source_excerpt(body, 360)
    label_text = ", ".join(labels[:4]) if labels else "the main ideas"
    kind_hint = scene_kind(
        {
            "title": title,
            "visual_description": body,
            "narration": body,
            "labels": labels,
            "assets": [],
        }
    )
    layout_notes = {
        "timeline": "Use a chronological left-to-right timeline with dated milestones and clear progression.",
        "cycle": "Use a circular cycle diagram with arrows showing repetition and cause-effect movement.",
        "cell": "Use a magnified biological cutaway with organelles or body structures arranged accurately.",
        "space": "Use a deep-space composition with planets, orbit paths, scale contrast, and rim lighting.",
        "map": "Use a topographic map-like layout with routes, regions, markers, and spatial relationships.",
        "data": "Use a clean data visualization scene with dimensional bars, comparison markers, and measured contrast.",
        "process": "Use a step-by-step flow scene with arrows showing transformation from start to outcome.",
        "concept": "Use a central 3D concept model surrounded by supporting objects and annotation callouts.",
    }
    return (
        f"Create an accurate educational 3D visualization about '{title}'. "
        f"Represent this exact source content: {excerpt} "
        f"Key visual elements must include: {label_text}. "
        f"{layout_notes.get(kind_hint, layout_notes['concept'])} "
        "Keep the composition clear, topic-specific, cinematic, and suitable for a textbook explainer."
    )


def generate_scenes(source_text, count, auto_count):
    sentences = split_sentences(source_text)
    if not sentences:
        sentences = [source_text.strip()]
    if auto_count:
        count = min(15, max(4, round(len(sentences) / 3)))
    chunks = chunk_sentences(sentences, count)
    scenes = []
    for idx, chunk in enumerate(chunks, start=1):
        body = " ".join(chunk).strip()
        keys = keywords(body, 5)
        labels = [word.capitalize() for word in keys[:4]] or [f"Key Point {idx}"]
        scene_assets = [asset_name(word) for word in (keys[:4] or ["main_concept", "supporting_visual"])]
        if len(scene_assets) < 2:
            scene_assets.append("supporting_visual.glb")
        narration = " ".join(chunk[:2]).strip()
        if len(narration) > 280:
            narration = narration[:277].rstrip() + "..."
        title = title_from_text(body, f"Scene {idx}")
        scenes.append(
            {
                "scene_number": idx,
                "title": title,
                "assets": scene_assets,
                "labels": labels,
                "animation": "\n".join(
                    [
                        "1. Establish the main visual and key subject.",
                        "2. Bring in supporting objects and labels.",
                        "3. Highlight the most important relationship or process.",
                        "4. Hold on a clean final composition for narration.",
                    ]
                ),
                "visual_description": visual_description_for_scene(title, body, labels),
                "narration": narration,
                "scene_image": None,
            }
        )
    return renumber_scenes(scenes)


def extract_image_text(b64_image, mime_type):
    return (
        "Image uploaded by the user. Free mode cannot read text from images "
        "without an OCR package or external AI service. Add the image text manually "
        "in the Plain text source for best results."
    )


def wrap_lines(draw, text, font, max_width, max_lines=4):
    words = re.sub(r"\s+", " ", text or "").strip().split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        box = draw.textbbox((0, 0), trial, font=font)
        if box[2] - box[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if words and len(lines) == max_lines:
        used = " ".join(lines)
        if len(used) < len(" ".join(words)):
            lines[-1] = lines[-1].rstrip(".") + "..."
    return lines


def text_block(draw, xy, text, font, fill, max_width, line_gap=8, max_lines=4):
    x, y = xy
    for line in wrap_lines(draw, text, font, max_width, max_lines):
        draw.text((x, y), line, fill=fill, font=font)
        box = draw.textbbox((x, y), line, font=font)
        y = box[3] + line_gap
    return y


def scene_kind(scene):
    text = " ".join(
        [
            scene.get("title", ""),
            scene.get("visual_description", ""),
            scene.get("narration", ""),
            " ".join(scene.get("labels", [])),
            " ".join(assets(scene)),
        ]
    ).lower()
    groups = [
        ("timeline", ["timeline", "history", "date", "year", "era", "century"]),
        ("cycle", ["cycle", "loop", "orbit", "repeat", "circular"]),
        ("cell", ["cell", "nucleus", "dna", "membrane", "organ", "tissue", "biology"]),
        ("space", ["planet", "space", "star", "orbit", "galaxy", "solar"]),
        ("map", ["map", "region", "country", "river", "route", "land", "migration"]),
        ("data", ["chart", "graph", "data", "compare", "increase", "decrease", "number"]),
        ("process", ["process", "flow", "step", "reaction", "transform", "sequence"]),
    ]
    for kind, words in groups:
        if any(word in text for word in words):
            return kind
    return "concept"


def theme_palette(scene):
    palettes = [
        ["#6ea8ff", "#50d5c8", "#f3bd5b", "#b99bff", "#6bd98d"],
        ["#ff8b8b", "#ffd166", "#6bd98d", "#70d6ff", "#cdb4db"],
        ["#80ed99", "#57cc99", "#38a3a5", "#22577a", "#c7f9cc"],
        ["#f4a261", "#e76f51", "#2a9d8f", "#e9c46a", "#a8dadc"],
    ]
    digest = hashlib.md5((scene.get("title", "") + scene.get("visual_description", "")).encode()).hexdigest()
    return palettes[int(digest[:2], 16) % len(palettes)]


def draw_arrow(draw, start, end, fill, width=5):
    draw.line((start, end), fill=fill, width=width)
    sx, sy = start
    ex, ey = end
    angle = 0 if ex == sx else (ey - sy) / max(1, abs(ex - sx))
    direction = 1 if ex >= sx else -1
    head = [(ex, ey), (ex - 18 * direction, ey - 10 - angle * 4), (ex - 18 * direction, ey + 10 - angle * 4)]
    draw.polygon(head, fill=fill)


def ai_image_prompt(scene):
    visual = scene.get("visual_description", "")
    title = scene.get("title", "")
    narration = scene.get("narration", "")
    labels = ", ".join(scene.get("labels", []))
    asset_list = ", ".join(assets(scene))
    animation = scene.get("animation", "").replace("\\n", "\n")
    return (
        "Premium educational 3D CGI storyboard frame, cinematic 16:9, high detail, sharp focus. "
        f"Main topic: {title}. "
        f"FOLLOW THIS VISUAL DESCRIPTION EXACTLY: {visual}. "
        f"Important objects or assets to show: {asset_list}. "
        f"Important concepts to show visually: {labels}. "
        f"Action or moment: {animation}. "
        f"Narration context: {narration}. "
        "Use accurate subject-specific objects, realistic scale relationships, professional studio lighting, "
        "clear foreground/midground/background, rich materials, educational museum exhibit quality. "
        "Avoid random fantasy elements. Avoid unrelated objects. No watermark, no logo, no UI, no captions, no text."
    )


def generate_ai_image(scene):
    prompt_text = ai_image_prompt(scene)[:2200]
    prompt = requests.utils.quote(prompt_text)
    seed_src = f"{scene.get('title', '')}|{scene.get('visual_description', '')}|{scene.get('scene_number', 0)}"
    seed = int(hashlib.md5(seed_src.encode("utf-8")).hexdigest()[:8], 16)
    model_group = st.session_state.get("image_quality", "Best quality")
    errors = []
    for model in POLLINATION_MODELS.get(model_group, POLLINATION_MODELS["Best quality"]):
        url = (
            POLLINATIONS_URL.format(prompt=prompt)
            + f"?width=1536&height=864&model={model}&nologo=true&enhance=true&private=true&seed={seed}"
        )
        try:
            response = requests.get(url, timeout=150)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type:
                raise RuntimeError("The free image service did not return an image.")
            return base64.b64encode(response.content).decode("utf-8")
        except Exception as exc:
            errors.append(f"{model}: {exc}")
    raise RuntimeError("; ".join(errors))


def generate_image(scene):
    try:
        return generate_ai_image(scene)
    except Exception:
        return generate_local_image(scene)


def generate_local_image(scene):
    try:
        from PIL import Image as PILImage
        from PIL import ImageDraw, ImageFont
    except Exception as exc:
        raise RuntimeError(f"Pillow is required for free local image generation: {exc}")

    width, height = 1280, 720
    image = PILImage.new("RGB", (width, height), "#07080c")
    draw = ImageDraw.Draw(image)
    palette = theme_palette(scene)
    title = scene.get("title", "Storyboard Scene")
    labels = scene.get("labels", [])[:4] or ["Main idea", "Detail", "Process"]
    visual = scene.get("visual_description", "")
    narration = scene.get("narration", "")
    kind = scene_kind(scene)

    for y in range(height):
        shade = int(7 + (y / height) * 24)
        draw.line([(0, y), (width, y)], fill=(shade, shade + 2, shade + 9))

    try:
        title_font = ImageFont.truetype("arial.ttf", 46)
        heading_font = ImageFont.truetype("arial.ttf", 28)
        small_font = ImageFont.truetype("arial.ttf", 24)
        tiny_font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        title_font = ImageFont.load_default()
        heading_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        tiny_font = ImageFont.load_default()

    # Main stage
    draw.rounded_rectangle((54, 178, 1226, 566), radius=26, fill="#0f121a", outline="#2a3040", width=2)
    draw.rounded_rectangle((76, 202, 840, 540), radius=22, fill="#131824", outline="#3a4356", width=2)

    if kind == "timeline":
        y = 370
        draw.line((135, y, 782, y), fill=palette[0], width=8)
        points = [(150, y), (345, y), (540, y), (735, y)]
        for idx, point in enumerate(points):
            color = palette[idx % len(palette)]
            draw.ellipse((point[0] - 30, point[1] - 30, point[0] + 30, point[1] + 30), fill=color, outline="#eef2ff", width=3)
            text_block(draw, (point[0] - 70, point[1] + 46), labels[idx % len(labels)], tiny_font, "#eef2ff", 140, 4, 2)
    elif kind == "cycle":
        center = (458, 370)
        radius = 132
        for idx, label in enumerate(labels[:4]):
            angle_points = [(458, 238), (590, 370), (458, 502), (326, 370)]
            x, y = angle_points[idx]
            draw.ellipse((x - 48, y - 48, x + 48, y + 48), fill=palette[idx], outline="#eef2ff", width=3)
            text_block(draw, (x - 54, y + 60), label, tiny_font, "#eef2ff", 120, 4, 2)
        draw.arc((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), 15, 330, fill="#3a4356", width=8)
        draw_arrow(draw, (570, 302), (608, 344), "#3a4356", 5)
    elif kind == "cell":
        draw.ellipse((210, 238, 700, 512), fill="#16251f", outline=palette[1], width=6)
        draw.ellipse((380, 300, 530, 450), fill=palette[3], outline="#eef2ff", width=3)
        for idx, label in enumerate(labels[:4]):
            x = 250 + idx * 115
            y = 290 + (idx % 2) * 118
            draw.ellipse((x - 34, y - 22, x + 34, y + 22), fill=palette[idx], outline="#eef2ff", width=2)
            draw.line((x + 34, y, 845, 255 + idx * 54), fill="#3a4356", width=2)
            text_block(draw, (862, 242 + idx * 54), label, tiny_font, "#eef2ff", 220, 3, 1)
    elif kind == "space":
        for idx in range(26):
            x = 100 + (idx * 73) % 700
            y = 220 + (idx * 47) % 300
            draw.ellipse((x, y, x + 3, y + 3), fill="#eef2ff")
        draw.ellipse((300, 270, 540, 510), fill=palette[0], outline="#eef2ff", width=4)
        draw.ellipse((520, 250, 610, 340), fill=palette[2], outline="#eef2ff", width=3)
        draw.arc((215, 245, 670, 525), 195, 350, fill="#3a4356", width=4)
        text_block(draw, (650, 278), labels[0], heading_font, "#eef2ff", 170, 4, 2)
    elif kind == "map":
        land = [(180, 300), (280, 238), (410, 270), (530, 235), (670, 318), (625, 455), (470, 492), (320, 450), (210, 505)]
        draw.polygon(land, fill="#18311f", outline=palette[2])
        draw.line((230, 455, 355, 380, 470, 405, 610, 315), fill=palette[0], width=7)
        for idx, label in enumerate(labels[:3]):
            x, y = [(230, 455), (355, 380), (610, 315)][idx]
            draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=palette[idx], outline="#eef2ff", width=2)
            text_block(draw, (x + 24, y - 12), label, tiny_font, "#eef2ff", 170, 3, 1)
    elif kind == "data":
        base_y = 492
        for idx, label in enumerate(labels[:4]):
            x = 170 + idx * 145
            bar_h = 90 + (idx * 43) % 170
            draw.rounded_rectangle((x, base_y - bar_h, x + 86, base_y), radius=8, fill=palette[idx], outline="#eef2ff", width=2)
            text_block(draw, (x - 8, base_y + 16), label, tiny_font, "#eef2ff", 120, 3, 2)
        draw.line((130, base_y, 760, base_y), fill="#3a4356", width=4)
    else:
        points = [(210, 360), (385, 292), (560, 382), (725, 310)]
        for idx, point in enumerate(points[: max(3, min(4, len(labels)))]):
            color = palette[idx % len(palette)]
            x, y = point
            draw.rounded_rectangle((x - 78, y - 54, x + 78, y + 54), radius=18, fill=color, outline="#eef2ff", width=3)
            text_block(draw, (x - 58, y - 16), labels[idx % len(labels)], tiny_font, "#07080c", 116, 3, 2)
            if idx < 3:
                draw_arrow(draw, (x + 82, y), (points[idx + 1][0] - 84, points[idx + 1][1]), "#3a4356", 5)

    # Header and visual description panel
    draw.rounded_rectangle((54, 42, 1226, 154), radius=22, fill="#101218", outline="#2a3040", width=2)
    text_block(draw, (82, 66), title, title_font, "#eef2ff", 760, 4, 1)
    draw.rounded_rectangle((870, 66, 1198, 130), radius=14, fill="#17223a", outline="#31568a", width=2)
    draw.text((895, 88), f"{kind.upper()} FRAME", fill="#9cc7ff", font=small_font)

    draw.rounded_rectangle((870, 202, 1202, 540), radius=18, fill="#101218", outline="#2a3040", width=2)
    draw.text((894, 228), "VISUAL DESCRIPTION", fill=palette[0], font=tiny_font)
    text_block(draw, (894, 260), visual or "Clean educational storyboard visualization.", small_font, "#cfd7ea", 272, 7, 7)
    draw.text((894, 474), "KEY LABELS", fill=palette[2], font=tiny_font)
    text_block(draw, (894, 502), ", ".join(labels), tiny_font, "#eef2ff", 272, 5, 2)

    draw.rounded_rectangle((60, 596, 1220, 672), radius=16, fill="#101218", outline="#2a3040", width=2)
    text_block(draw, (88, 618), narration, small_font, "#ffdbe0", 1080, 6, 2)

    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


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


def storyboard_export_payload(storyboard, scenes, include_images):
    export_scenes = []
    for scene in scenes:
        item = dict(scene)
        item["assets"] = assets(item)
        item.pop("required_assets", None)
        item.pop("models_3d", None)
        if not include_images:
            item.pop("scene_image", None)
        export_scenes.append(item)
    return {
        "name": storyboard.get("name", "Storyboard"),
        "created": storyboard.get("created", ""),
        "scenes": export_scenes,
    }


def safe_filename(name, suffix):
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", name or "storyboard").strip("_")
    return f"{base or 'storyboard'}{suffix}"


def images_zip_bytes(storyboard_name, scenes):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        count = 0
        for idx, scene in enumerate(scenes, start=1):
            if not scene.get("scene_image"):
                continue
            title = re.sub(r"[^A-Za-z0-9_-]+", "_", scene.get("title", f"scene_{idx}")).strip("_")
            filename = f"scene_{idx:02d}_{title or 'image'}.png"
            archive.writestr(filename, base64.b64decode(scene["scene_image"]))
            count += 1
        if count == 0:
            archive.writestr("README.txt", "No generated scene images were found in this storyboard.")
    buffer.seek(0)
    return buffer.getvalue()


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

        st.markdown(
            """
            <div class="api-pill">
              <span class="dot ok"></span>
              Free image mode
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.caption(FREE_MODE_NOTE)
        st.session_state.image_quality = st.selectbox(
            "Image generation style",
            list(POLLINATION_MODELS.keys()),
            index=list(POLLINATION_MODELS.keys()).index(st.session_state.get("image_quality", "Best quality")),
            help="Best quality tries the strongest free public model first, then falls back automatically.",
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
if st.session_state.get("nav_choice") != st.session_state.active_tab:
    st.session_state.nav_choice = st.session_state.active_tab

nav = st.radio(
    "Workspace navigation",
    nav_options,
    horizontal=True,
    key="nav_choice",
    label_visibility="collapsed",
)
st.session_state.active_tab = nav


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

        with st.expander("Generate scenes free locally", expanded=not scenes):
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
                        with st.spinner("Preparing image source in free local mode..."):
                            final_text = extract_image_text(image_b64, image_mime)
                    if not final_text:
                        st.warning("Add source content first.")
                        st.stop()
                    with st.spinner("Creating storyboard scenes locally..."):
                        new_scenes = generate_scenes(final_text, scene_count, auto_count)
                    if not new_scenes:
                        st.error("No scenes were returned.")
                        st.stop()
                    save_scenes(new_scenes)
                    scenes = active_storyboard().get("scenes", [])
                    st.success(f"Created {len(scenes)} scenes.")
                    if auto_images:
                        bar = st.progress(0, "Generating free AI images...")
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
                '<div class="empty-state"><strong>No scenes yet</strong>Generate scenes locally or add one manually.</div>',
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
                        bar = st.progress(0, "Generating free AI images...")
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
                                with st.spinner("Generating free AI image..."):
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
                image_count = sum(1 for scene in scenes if scene.get("scene_image"))
                st.caption(f"{len(scenes)} scenes ready. {image_count} scenes include images.")
                include_images = st.checkbox("Include images in JSON", value=False)
                payload = storyboard_export_payload(storyboard, scenes, include_images)
                json_bytes = json.dumps(payload, indent=2).encode("utf-8")
                st.download_button(
                    "Download JSON",
                    data=json_bytes,
                    file_name=safe_filename(storyboard["name"], "_storyboard.json"),
                    mime="application/json",
                    use_container_width=True,
                    key="download_storyboard_json",
                )
                if image_count:
                    st.download_button(
                        "Download Images ZIP",
                        data=images_zip_bytes(storyboard["name"], scenes),
                        file_name=safe_filename(storyboard["name"], "_images.zip"),
                        mime="application/zip",
                        use_container_width=True,
                        key="download_images_zip",
                    )
                pdf_key = f"pdf_bytes_{st.session_state.active_sb}"
                pdf_name_key = f"pdf_name_{st.session_state.active_sb}"
                if st.button("Build PDF", use_container_width=True, key="build_pdf"):
                    with st.spinner("Building PDF..."):
                        pdf, err = pdf_export(storyboard["name"], scenes)
                    if err:
                        st.error(err)
                    else:
                        st.session_state[pdf_key] = pdf
                        st.session_state[pdf_name_key] = storyboard["name"]
                        st.success("PDF ready.")
                if st.session_state.get(pdf_key) and st.session_state.get(pdf_name_key) == storyboard["name"]:
                    st.download_button(
                        "Download PDF",
                        data=st.session_state[pdf_key],
                        file_name=safe_filename(storyboard["name"], ".pdf"),
                        mime="application/pdf",
                        use_container_width=True,
                        key="download_storyboard_pdf",
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
