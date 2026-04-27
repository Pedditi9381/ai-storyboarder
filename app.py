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

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="LPVision Studio", layout="wide", page_icon="🎬")

# ─── CSS + LIGHTBOX + BLENDER CONCEPTS ─────────────────────────────────────────
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

/* ── Enhanced Clickable scene image ── */
.scene-img-wrap { position:relative; cursor:zoom-in; display:block; }
.scene-img-wrap img { width:100%; border-radius:8px; object-fit:cover; border:1px solid #2d2d5a; display:block; transition:transform 0.15s,box-shadow 0.15s; }
.scene-img-wrap:hover img { transform:scale(1.02); box-shadow:0 0 0 2px #3b82f6,0 8px 32px rgba(59,130,246,0.25); }
.zoom-hint { position:absolute; bottom:6px; right:8px; font-size:10px; color:rgba(255,255,255,0.6); background:rgba(0,0,0,0.6); border-radius:4px; padding:2px 7px; pointer-events:none; }

/* ── Professional Lightbox ── */
#lpv-lightbox { display:none; position:fixed; z-index:99999; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.95); align-items:center; justify-content:center; backdrop-filter:blur(20px); }
#lpv-lightbox.open { display:flex; }
#lpv-lightbox .lightbox-content { display:flex; gap:30px; max-width:95vw; max-height:90vh; align-items:center; justify-content:center; position:relative; }
#lpv-lightbox .lightbox-image { max-width:70vw; max-height:85vh; border-radius:12px; box-shadow:0 0 60px rgba(59,130,246,0.5),0 0 0 2px #3b82f6; object-fit:contain; }
#lpv-lightbox .blender-info { background:linear-gradient(135deg, rgba(13,13,26,0.95), rgba(8,8,20,0.95)); backdrop-filter:blur(10px); border-radius:16px; border:1px solid #2d2d5a; padding:20px; max-width:320px; max-height:85vh; overflow-y:auto; scrollbar-width:thin; }
#lpv-lightbox .blender-info::-webkit-scrollbar { width:6px; }
#lpv-lightbox .blender-info::-webkit-scrollbar-track { background:#1a1a35; border-radius:3px; }
#lpv-lightbox .blender-info::-webkit-scrollbar-thumb { background:#3b82f6; border-radius:3px; }
#lpv-lightbox .info-title { font-size:20px; font-weight:700; color:#f1f5f9; margin-bottom:15px; border-bottom:2px solid #3b82f6; padding-bottom:8px; }
#lpv-lightbox .info-section { margin-bottom:18px; }
#lpv-lightbox .info-label { font-size:10px; font-weight:700; letter-spacing:0.1em; color:#3b82f6; text-transform:uppercase; margin-bottom:6px; }
#lpv-lightbox .info-text { font-size:13px; color:#cbd5e1; line-height:1.6; }
#lpv-lightbox .blender-tag { display:inline-block; background:#1e293b; color:#60a5fa; padding:4px 10px; border-radius:6px; font-size:11px; margin:3px 4px 3px 0; font-family:'JetBrains Mono',monospace; }
#lpv-close-btn { position:fixed; top:20px; right:30px; width:40px; height:40px; border-radius:50%; background:rgba(59,130,246,0.2); border:1px solid #3b82f6; color:#e2e8f0; font-size:28px; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all 0.2s; z-index:100001; }
#lpv-close-btn:hover { background:#3b82f6; color:white; transform:scale(1.1); }
.lightbox-nav { position:absolute; top:50%; transform:translateY(-50%); width:40px; height:40px; background:rgba(59,130,246,0.3); border:1px solid #3b82f6; border-radius:50%; display:flex; align-items:center; justify-content:center; cursor:pointer; transition:all 0.2s; z-index:100001; }
.lightbox-nav:hover { background:#3b82f6; transform:scale(1.1); }
.lightbox-nav.prev { left:20px; }
.lightbox-nav.next { right:20px; }
</style>

<!-- Professional Lightbox DOM -->
<div id="lpv-lightbox">
  <button id="lpv-close-btn" onclick="closeLightbox()">✕</button>
  <div class="lightbox-nav prev" onclick="navigateLightbox(-1)">‹</div>
  <div class="lightbox-nav next" onclick="navigateLightbox(1)">›</div>
  <div class="lightbox-content">
    <img id="lpv-lb-img" class="lightbox-image" src="" alt=""/>
    <div id="lpv-info-panel" class="blender-info"></div>
  </div>
</div>

<script>
let currentSceneData = null;
let currentIndex = 0;

function openLightbox(imgSrc, sceneData, index) {
  currentSceneData = sceneData;
  currentIndex = index;
  document.getElementById('lpv-lb-img').src = imgSrc;
  updateInfoPanel(sceneData);
  document.getElementById('lpv-lightbox').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function updateInfoPanel(sceneData) {
  const panel = document.getElementById('lpv-info-panel');
  if (!sceneData) return;
  
  // Format animation steps
  let animSteps = '';
  if (sceneData.animation) {
    const steps = sceneData.animation.split('\\n').filter(s => s.trim());
    animSteps = steps.map((step, i) => 
      `<div style="margin-bottom:8px;"><span style="color:#f59e0b;font-weight:600;">${i+1}.</span> <span style="color:#fde68a;">${step.trim()}</span></div>`
    ).join('');
  }
  
  // Format assets
  const assets = sceneData.assets || [];
  const assetTags = assets.map(a => `<span class="blender-tag">${a}</span>`).join('');
  
  // Format labels
  const labels = sceneData.labels || [];
  const labelTags = labels.map(l => `<span style="display:inline-block;background:#1a2d1a;color:#4ade80;padding:3px 8px;border-radius:5px;font-size:10px;margin:2px;">${l}</span>`).join('');
  
  panel.innerHTML = `
    <div class="info-title">🎬 ${sceneData.title || 'Untitled Scene'}</div>
    
    <div class="info-section">
      <div class="info-label">🎨 BLENDER 3D CONCEPTS</div>
      <div class="info-text">
        <strong>Static Camera Setup:</strong><br/>
        • Position: ${sceneData.camera_position || 'Front-Orthographic View'}<br/>
        • Focal Length: ${sceneData.focal_length || '50mm (Standard)'}<br/>
        • Depth of Field: ${sceneData.dof || 'f/5.6 for clarity'}<br/>
        • Composition: ${sceneData.composition || 'Rule of thirds, centered on subject'}<br/>
      </div>
    </div>
    
    <div class="info-section">
      <div class="info-label">🔧 TECHNIQUES</div>
      <div class="info-text">
        • Shading: ${sceneData.shading || 'Principled BSDF with PBR textures'}<br/>
        • Lighting: ${sceneData.lighting || 'Three-point lighting (key, fill, rim)'}<br/>
        • Rendering: ${sceneData.renderer || 'Cycles, 1024 samples, denoising'}<br/>
        • Animation: ${sceneData.animation_type || 'Keyframe interpolation (Bezier)'}<br/>
      </div>
    </div>
    
    <div class="info-section">
      <div class="info-label">📦 3D ASSETS</div>
      <div class="info-text">${assetTags || '—'}</div>
    </div>
    
    <div class="info-section">
      <div class="info-label">🏷️ UI LABELS</div>
      <div class="info-text">${labelTags || '—'}</div>
    </div>
    
    <div class="info-section">
      <div class="info-label">⚡ ANIMATION SEQUENCE</div>
      <div class="info-text">${animSteps || '<span style="color:#64748b;">—</span>'}</div>
    </div>
    
    <div class="info-section">
      <div class="info-label">📝 VISUAL DESCRIPTION</div>
      <div class="info-text">${sceneData.visual_description || '<span style="color:#64748b;">—</span>'}</div>
    </div>
    
    <div class="info-section">
      <div class="info-label">🎙️ NARRATION</div>
      <div class="info-text" style="font-style:italic;">${sceneData.narration || '<span style="color:#64748b;">—</span>'}</div>
    </div>
  `;
}

function closeLightbox() {
  document.getElementById('lpv-lightbox').classList.remove('open');
  document.getElementById('lpv-lb-img').src = '';
  document.getElementById('lpv-info-panel').innerHTML = '';
  currentSceneData = null;
  document.body.style.overflow = '';
}

function navigateLightbox(direction) {
  if (!window.allScenesData || !window.allScenesData.length) return;
  let newIndex = currentIndex + direction;
  if (newIndex < 0) newIndex = window.allScenesData.length - 1;
  if (newIndex >= window.allScenesData.length) newIndex = 0;
  
  const newScene = window.allScenesData[newIndex];
  if (newScene && newScene.image_b64) {
    const imgSrc = `data:image/png;base64,${newScene.image_b64}`;
    document.getElementById('lpv-lb-img').src = imgSrc;
    updateInfoPanel(newScene);
    currentIndex = newIndex;
    currentSceneData = newScene;
  }
}

document.getElementById('lpv-lightbox').addEventListener('click', function(e){ 
  if(e.target === this) closeLightbox(); 
});
document.addEventListener('keydown', function(e){ 
  if(e.key==='Escape') closeLightbox(); 
  if(e.key==='ArrowLeft' && document.getElementById('lpv-lightbox').classList.contains('open')) navigateLightbox(-1);
  if(e.key==='ArrowRight' && document.getElementById('lpv-lightbox').classList.contains('open')) navigateLightbox(1);
});
</script>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
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

# ─── API KEYS ──────────────────────────────────────────────────────────────────
GROQ_API_KEY   = st.secrets.get("GROQ_API_KEY",   None)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", None)
GROQ_URL       = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_MODELS  = [
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image-preview",
    "gemini-2.0-flash-preview-image-generation",
]
GEMINI_BASE    = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# ─── HELPERS ───────────────────────────────────────────────────────────────────
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
        sc.setdefault("camera_position", "Front-Orthographic View")
        sc.setdefault("focal_length", "50mm")
        sc.setdefault("dof", "f/5.6")
        sc.setdefault("composition", "Rule of thirds, centered on subject")
        sc.setdefault("shading", "Principled BSDF with PBR textures")
        sc.setdefault("lighting", "Three-point lighting with HDRI environment")
        sc.setdefault("renderer", "Cycles, 1024 samples, denoising")
        sc.setdefault("animation_type", "Keyframe interpolation (Bezier)")
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

def clickable_img_with_blender_info(b64, scene_data, snum, scene_idx, all_scenes):
    uri = f"data:image/png;base64,{b64}"
    scene_data_for_js = {
        "title": scene_data.get("title", ""),
        "assets": scene_data.get("assets", []),
        "labels": scene_data.get("labels", []),
        "animation": scene_data.get("animation", ""),
        "visual_description": scene_data.get("visual_description", ""),
        "narration": scene_data.get("narration", ""),
        "camera_position": scene_data.get("camera_position", "Front-Orthographic View"),
        "focal_length": scene_data.get("focal_length", "50mm"),
        "dof": scene_data.get("dof", "f/5.6"),
        "composition": scene_data.get("composition", "Rule of thirds, centered on subject"),
        "shading": scene_data.get("shading", "Principled BSDF with PBR textures"),
        "lighting": scene_data.get("lighting", "Three-point lighting with HDRI environment"),
        "renderer": scene_data.get("renderer", "Cycles, 1024 samples, denoising"),
        "animation_type": scene_data.get("animation_type", "Keyframe interpolation (Bezier)"),
        "image_b64": b64
    }
    
    # Store all scenes data for navigation
    all_scenes_data = []
    for idx, s in enumerate(all_scenes):
        if s.get("scene_image"):
            all_scenes_data.append({
                "title": s.get("title", ""),
                "assets": s.get("assets", []),
                "labels": s.get("labels", []),
                "animation": s.get("animation", ""),
                "visual_description": s.get("visual_description", ""),
                "narration": s.get("narration", ""),
                "camera_position": s.get("camera_position", "Front-Orthographic View"),
                "focal_length": s.get("focal_length", "50mm"),
                "dof": s.get("dof", "f/5.6"),
                "composition": s.get("composition", "Rule of thirds, centered on subject"),
                "shading": s.get("shading", "Principled BSDF with PBR textures"),
                "lighting": s.get("lighting", "Three-point lighting with HDRI environment"),
                "renderer": s.get("renderer", "Cycles, 1024 samples, denoising"),
                "animation_type": s.get("animation_type", "Keyframe interpolation (Bezier)"),
                "image_b64": s.get("scene_image", "")
            })
    
    # Embed all scenes data into JavaScript
    embed_script = f"""
    <script>
    if (typeof window.allScenesData === 'undefined') {{
        window.allScenesData = {json.dumps(all_scenes_data)};
    }}
    </script>
    """
    
    cap = f"Scene {snum:02d}  ·  {scene_data.get('title', '')}".replace("'", "&#39;")
    return (embed_script +
            f'<div class="scene-img-wrap" onclick="openLightbox(\'{uri}\', {json.dumps(scene_data_for_js)}, {scene_idx})">'
            f'<img src="{uri}" alt="{cap}"/>'
            f'<span class="zoom-hint">🔍 Click for Blender details & full view</span></div>')

# ─── GROQ helpers ──────────────────────────────────────────────────────────────
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

# ─── GROQ: SCENE GENERATION ────────────────────────────────────────────────────
def generate_scenes_groq(text, num_scenes):
    if not GROQ_API_KEY:
        st.error("Add GROQ_API_KEY to Streamlit Secrets."); return None
    sys_p = (f"You are a Senior 3D Instructional Animator. Convert the input into EXACTLY {num_scenes} storyboard scenes.\n"
             "Return ONLY a valid JSON array. No markdown fences. No explanation. No preamble.\n"
             "Each element must have exactly these keys:\n"
             "  scene_number (int), title (str 3-6 words), assets (array of 3-6 lowercase_glb_names),\n"
             "  labels (array of 2-5 short UI caption strings), animation (str: numbered steps as plain text),\n"
             "  visual_description (str: 2-3 sentences on camera/lighting/layout),\n"
             "  narration (str: 2-4 complete educational sentences spoken by narrator),\n"
             "  camera_position (str: recommended Blender camera position),\n"
             "  focal_length (str: recommended focal length),\n"
             "  dof (str: depth of field setting),\n"
             "  composition (str: composition guidelines),\n"
             "  shading (str: shading/ material approach),\n"
             "  lighting (str: lighting setup),\n"
             "  renderer (str: render settings),\n"
             "  animation_type (str: animation technique)\n"
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
        st.code(f"…{raw[max(0,e.pos-60):e.pos+60]}…"); return None
    except Exception as e:
        st.error(f"Generation failed: {e}"); return None

# ─── IMAGE PROMPT: ENHANCED WITH BLENDER CONCEPTS ─────────────────────────────
def build_image_prompt(sc):
    """
    Enhanced prompt with Blender-specific instructions for static camera shots.
    """
    title  = sc.get("title", "")
    assets = ", ".join(get_scene_assets(sc))
    labels = ", ".join(sc.get("labels", []))
    narr   = sc.get("narration", "")[:180]
    vd     = sc.get("visual_description", "")[:200]
    raw_a  = sc.get("animation", "").strip()
    lines  = [l.strip() for l in raw_a.replace("\\n","\n").split("\n") if l.strip()]
    anim   = " | ".join(lines) if lines else raw_a[:300]
    
    # Get Blender-specific settings with defaults
    cam_pos = sc.get("camera_position", "front-orthographic view at subject height")
    focal = sc.get("focal_length", "50mm standard lens")
    dof = sc.get("dof", "f/5.6 for moderate depth of field")
    comp = sc.get("composition", "rule of thirds, subject centered in frame")
    shade = sc.get("shading", "principled BSDF with PBR metallic/roughness workflow")
    light = sc.get("lighting", "three-point lighting: warm key light (3200K), cool fill (6500K), rim light from back")
    render = sc.get("renderer", "Cycles with 1024 samples, denoising, 16:9 aspect ratio")
    anim_type = sc.get("animation_type", "smooth keyframe interpolation for subtle movement")

    return (
        f"Professional 3D CGI educational animation storyboard frame. Static camera setup. "
        f"Scene: '{title}'. "
        f"PRIMARY — Animation action to depict (show the key visual moment of this step): {anim}. "
        f"3D GLB assets present: {assets}. "
        f"On-screen annotation labels: {labels}. "
        f"Educational context: {narr}. "
        f"Camera staging (STATIC): {cam_pos}. Focal length: {focal}. Depth of field: {dof}. Composition: {comp}. "
        f"Shading/Materials: {shade}. Lighting: {light}. "
        f"Render settings: {render}. Animation technique: {anim_type}. "
        "Render: Blender 4 Cycles photorealistic, clean hard-surface meshes, subdivision level 2, "
        "beveled edges for GLB-export topology, PBR metallic/roughness workflow, "
        "four-point HDRI studio lighting (amber key 3200K, blue fill 6500K, purple-teal rim, white bounce), "
        "deep charcoal studio #12121e with subtle floor reflection, AO baked, "
        "cinema depth-of-field f/2.8, 16:9 widescreen, objects arranged to clearly illustrate the animation step, "
        "static camera - no camera movement, no 2D art, no cartoon, no text overlays, no watermarks."
    )

# ─── GEMINI: SILENT QUOTA HANDLING ────────────────────────────────────────────
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
    """
    def log(m):
        if status_slot: status_slot.caption(m)

    if GEMINI_API_KEY:
        b64, err = generate_scene_image_gemini(sc)
        if b64:
            log("✓ via Gemini")
            return b64
        if err == "quota":
            log("Gemini quota reached — switching to Pollinations…")
        elif err not in ("no_key", "no_models", "200_no_image"):
            log("Gemini unavailable — switching to Pollinations…")
        # fall through silently

    b64, err = generate_scene_image_pollinations(sc)
    if b64:
        log("✓ via Pollinations")
        return b64
    log(f"⚠ Image failed: {err}")
    return None

# ─── PDF EXPORT (keep as before) ───────────────────────────────────────────────
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
        title=f"LPVision — {sb_name}", author="LPVision Studio")

    C = dict(bg=HexColor("#06060f"), card=HexColor("#0d0d1a"), bord=HexColor
