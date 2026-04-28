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

# ─── CSS + LIGHTBOX ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

:root {
  --bg-void:    #04040c;
  --bg-card:    #080814;
  --bg-raised:  #0c0c1a;
  --bg-input:   #0a0a18;
  --bd-subtle:  #1a1a30;
  --bd-mid:     #252545;
  --bd-bright:  #3a3a6a;
  --accent-blue:  #4f8ef7;
  --accent-purp:  #9b6ff8;
  --accent-teal:  #2dd4bf;
  --accent-amber: #fbbf24;
  --accent-pink:  #f472b6;
  --accent-green: #34d399;
  --txt-primary:  #eef0f8;
  --txt-secondary:#8890b0;
  --txt-muted:    #454870;
  --glow-blue:    rgba(79,142,247,0.15);
  --glow-purp:    rgba(155,111,248,0.15);
}

html, body, [class*="css"] { 
  font-family: 'DM Sans', sans-serif; 
  background: var(--bg-void);
}
.main { background-color: var(--bg-void); color: var(--txt-primary); }
.block-container { padding: 0.75rem 1.25rem !important; max-width: 100% !important; }

section[data-testid="stSidebar"] { 
  background: var(--bg-card); 
  border-right: 1px solid var(--bd-subtle); 
  width: 240px !important; 
}
section[data-testid="stSidebar"] .block-container { padding: 0.85rem !important; }

#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar brand ── */
.sidebar-brand { 
  display:flex; align-items:center; gap:10px; 
  padding:0.5rem 0 1.25rem 0; 
  border-bottom:1px solid var(--bd-subtle); 
  margin-bottom:1rem; 
}
.sidebar-brand .logo { 
  width:34px; height:34px; border-radius:10px; 
  background:linear-gradient(135deg,#4f8ef7,#9b6ff8); 
  display:flex; align-items:center; justify-content:center; 
  font-family:'Syne',sans-serif; font-size:14px; font-weight:800; color:white;
  box-shadow: 0 0 16px rgba(79,142,247,0.4);
}
.sidebar-brand .brand-sub { font-size:10px; font-weight:600; color:var(--txt-muted); letter-spacing:0.2em; font-family:'DM Mono',monospace; }
.sidebar-brand .brand-name { font-size:15px; font-weight:800; color:var(--txt-primary); font-family:'Syne',sans-serif; letter-spacing:-0.01em; }

/* ── Buttons ── */
.stButton>button { 
  background:var(--bg-raised) !important; 
  color:var(--txt-secondary) !important; 
  border:1px solid var(--bd-mid) !important; 
  border-radius:8px !important; 
  font-size:12px !important; 
  font-weight:600 !important; 
  font-family:'DM Sans',sans-serif !important; 
  transition:all 0.18s ease !important;
  letter-spacing:0.01em !important;
}
.stButton>button:hover { 
  background:var(--bd-subtle) !important; 
  color:var(--txt-primary) !important; 
  border-color:var(--bd-bright) !important; 
  box-shadow: 0 0 12px var(--glow-blue) !important;
}
.stDownloadButton>button { 
  background:rgba(52,211,153,0.08) !important; 
  color:var(--accent-green) !important; 
  border:1px solid rgba(52,211,153,0.25) !important; 
  border-radius:8px !important; 
  font-family:'DM Sans',sans-serif !important; 
}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input { 
  background:var(--bg-input) !important; 
  color:var(--txt-primary) !important; 
  border:1px solid var(--bd-mid) !important; 
  border-radius:8px !important; 
  font-family:'DM Sans',sans-serif !important; 
  font-size:13px !important; 
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border-color: var(--accent-blue) !important;
  box-shadow: 0 0 0 2px rgba(79,142,247,0.15) !important;
}
label { color:var(--txt-muted) !important; font-size:11px !important; font-weight:600 !important; letter-spacing:0.05em !important; text-transform:uppercase !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { 
  background:transparent !important; 
  gap:0; 
  border-bottom:1px solid var(--bd-subtle); 
}
.stTabs [data-baseweb="tab"] { 
  background:transparent !important; 
  color:var(--txt-muted) !important; 
  font-family:'Syne',sans-serif !important; 
  font-size:12px !important; 
  font-weight:700 !important;
  letter-spacing:0.05em !important;
  border-bottom:2px solid transparent !important; 
  padding: 0.6rem 1.1rem !important;
  transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] { 
  color:var(--txt-primary) !important; 
  border-bottom-color:var(--accent-blue) !important; 
}
.stTabs [data-baseweb="tab-panel"] { padding:1rem 0 0 0 !important; }
.streamlit-expanderHeader { 
  background:var(--bg-raised) !important; 
  color:var(--txt-secondary) !important; 
  border:1px solid var(--bd-subtle) !important; 
  border-radius:8px !important; 
  font-family:'DM Sans',sans-serif !important;
}
[data-testid="stFileUploadDropzone"] { 
  background:var(--bg-input) !important; 
  border:1px dashed var(--bd-mid) !important; 
  border-radius:8px !important; 
}
.stAlert { 
  background:var(--bg-raised) !important; 
  border:1px solid var(--bd-subtle) !important; 
  border-radius:8px !important; 
  color:var(--txt-secondary) !important; 
}
hr { border-color:var(--bd-subtle) !important; }
.stRadio label { color:var(--txt-secondary) !important; }

/* ── Scene image — clickable with glow ── */
.scene-img-wrap { 
  position:relative; cursor:zoom-in; display:block;
  border-radius:10px; overflow:hidden;
}
.scene-img-wrap img { 
  width:100%; border-radius:10px; object-fit:cover; 
  border:1px solid var(--bd-mid); 
  display:block; 
  transition:transform 0.2s, box-shadow 0.2s; 
}
.scene-img-wrap:hover img { 
  transform:scale(1.03); 
  box-shadow: 0 0 0 2px var(--accent-blue), 0 12px 40px rgba(79,142,247,0.3); 
}
.zoom-hint { 
  position:absolute; bottom:8px; right:8px; 
  font-size:10px; color:rgba(255,255,255,0.7); 
  background:rgba(0,0,0,0.65); 
  border-radius:20px; padding:3px 9px; 
  pointer-events:none;
  font-family:'DM Mono',monospace;
  letter-spacing:0.04em;
  backdrop-filter: blur(4px);
}
.img-no-image {
  height:150px; background:var(--bg-raised); 
  border:1.5px dashed var(--bd-mid);
  border-radius:10px; 
  display:flex; align-items:center; justify-content:center;
  flex-direction:column; gap:6px;
}

/* ── Lightbox ── */
#lpv-lightbox { 
  display:none; position:fixed; z-index:99999; top:0; left:0; 
  width:100vw; height:100vh; 
  background:rgba(2,2,10,0.96); 
  align-items:center; justify-content:center; 
  backdrop-filter:blur(16px); 
  animation: lbFadeIn 0.2s ease;
}
@keyframes lbFadeIn { from{opacity:0} to{opacity:1} }
#lpv-lightbox.open { display:flex; }
#lpv-lb-img-wrap { 
  display:flex; flex-direction:column; align-items:center; gap:0;
  max-width:90vw;
}
#lpv-lb-img { 
  max-width:88vw; max-height:78vh; 
  border-radius:14px; 
  box-shadow: 0 0 80px rgba(79,142,247,0.35), 0 0 0 1px rgba(79,142,247,0.4);
  object-fit:contain;
  animation: lbImgPop 0.25s cubic-bezier(0.34,1.56,0.64,1);
}
@keyframes lbImgPop { from{transform:scale(0.88);opacity:0} to{transform:scale(1);opacity:1} }

#lpv-lb-close { 
  position:fixed; top:20px; right:28px; 
  font-size:28px; color:var(--txt-primary); cursor:pointer; 
  background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12);
  width:44px; height:44px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  line-height:1; opacity:0.8; transition:all 0.15s; 
  font-family:sans-serif;
}
#lpv-lb-close:hover { opacity:1; background:rgba(255,255,255,0.12); transform:scale(1.1); }

#lpv-lb-toolbar {
  display:flex; gap:10px; align-items:center; justify-content:center;
  padding:14px 0 0 0;
  flex-wrap:wrap;
}
.lb-btn {
  display:inline-flex; align-items:center; gap:7px;
  padding:9px 18px; border-radius:24px;
  font-family:'DM Sans',sans-serif; font-size:13px; font-weight:600;
  cursor:pointer; border:none; transition:all 0.18s;
  letter-spacing:0.01em;
}
.lb-btn-download {
  background:linear-gradient(135deg,#1e3a5f,#1a2d4a);
  color:#60a5fa; border:1px solid rgba(79,142,247,0.3);
}
.lb-btn-download:hover { background:linear-gradient(135deg,#2a4d7f,#25406a); box-shadow:0 0 16px rgba(79,142,247,0.3); }
.lb-btn-regen {
  background:linear-gradient(135deg,#1e1a3d,#2d1a5a);
  color:#a78bfa; border:1px solid rgba(155,111,248,0.3);
}
.lb-btn-regen:hover { background:linear-gradient(135deg,#2a2555,#3d2575); box-shadow:0 0 16px rgba(155,111,248,0.3); }
.lb-btn-blender {
  background:linear-gradient(135deg,#1a2d1a,#0f1f2d);
  color:#34d399; border:1px solid rgba(52,211,153,0.3);
}
.lb-btn-blender:hover { background:linear-gradient(135deg,#253d25,#152a3d); box-shadow:0 0 16px rgba(52,211,153,0.25); }
.lb-btn-close-m {
  background:rgba(255,255,255,0.06);
  color:var(--txt-secondary); border:1px solid rgba(255,255,255,0.1);
}
.lb-btn-close-m:hover { background:rgba(255,255,255,0.12); }

#lpv-lb-cap { 
  font-size:11px; color:var(--txt-muted); 
  font-family:'DM Mono',monospace; letter-spacing:0.06em;
  padding-top:4px;
}

/* ── Section boxes ── */
.sec-box {
  background: var(--bg-raised);
  border: 1px solid var(--bd-subtle);
  border-radius:10px;
  padding: 0.65rem 0.8rem;
  height:100%; box-sizing:border-box;
}
.sec-box-label {
  font-size:9px; font-weight:800; letter-spacing:0.18em;
  text-transform:uppercase; margin-bottom:7px;
  font-family:'DM Mono',monospace;
}

/* ── Pill tags ── */
.pill-tag {
  display:inline-block; margin:2px 3px 2px 0;
  padding:3px 10px; border-radius:20px;
  font-size:11px; font-weight:600;
  font-family:'DM Mono',monospace;
  letter-spacing:0.02em;
}

/* ── Scene card ── */
.scene-header {
  display:flex; align-items:center; gap:10px;
  padding: 0.4rem 0 0.3rem 0;
}
.scene-num-badge {
  background:linear-gradient(135deg,#2563eb,#7c3aed);
  color:white; font-size:10px; font-weight:800;
  font-family:'DM Mono',monospace;
  padding:5px 8px; border-radius:10px; min-width:32px;
  text-align:center; letter-spacing:0.05em;
}
.scene-title {
  font-family:'Syne',sans-serif;
  font-size:15px; font-weight:700; color:var(--txt-primary);
}
.scene-divider {
  height:1px;
  background:linear-gradient(90deg,rgba(79,142,247,0.1),rgba(155,111,248,0.3),rgba(79,142,247,0.1));
  margin: 0.5rem 0 1.1rem 0;
  border-radius:2px;
}

/* ── Blender badge ── */
.blender-badge {
  display:inline-flex; align-items:center; gap:5px;
  background:rgba(52,211,153,0.08); 
  border:1px solid rgba(52,211,153,0.2);
  border-radius:6px; padding:3px 10px;
  font-size:10px; font-weight:600; color:var(--accent-teal);
  font-family:'DM Mono',monospace; letter-spacing:0.04em;
}

/* ── Narration box (improved readability) ── */
.narration-text {
  font-size:13px; color:#f0e8ff; 
  line-height:1.85; font-style:italic;
  font-weight:400;
}
.narration-text strong { color:var(--accent-pink); font-style:normal; font-weight:600; }

/* ── Animation steps ── */
.anim-step {
  display:flex; gap:9px; margin-bottom:6px; align-items:flex-start;
}
.anim-step-num {
  min-width:20px; height:20px; border-radius:50%;
  background:linear-gradient(135deg,#d97706,#f59e0b);
  color:#000; font-size:9px; font-weight:800;
  display:flex; align-items:center; justify-content:center;
  flex-shrink:0; margin-top:2px;
  font-family:'DM Mono',monospace;
}
.anim-step-text { font-size:12px; color:#fde68a; line-height:1.55; }

/* ── Progress/status bar ── */
.gen-status {
  background:var(--bg-raised); border:1px solid var(--bd-mid);
  border-radius:8px; padding:0.6rem 1rem;
  font-size:12px; color:var(--txt-secondary);
  font-family:'DM Mono',monospace;
}
</style>

<!-- Lightbox DOM -->
<div id="lpv-lightbox">
  <button id="lpv-lb-close" onclick="closeLB()">&#x2715;</button>
  <div id="lpv-lb-img-wrap">
    <img id="lpv-lb-img" src="" alt=""/>
    <div id="lpv-lb-toolbar">
      <button class="lb-btn lb-btn-download" onclick="downloadLBImg()">⬇ Download Image</button>
      <button class="lb-btn lb-btn-blender" id="lb-blender-btn" onclick="copyBlenderPrompt()">🟢 Copy Blender Prompt</button>
      <button class="lb-btn lb-btn-regen" id="lb-regen-btn" onclick="regenFromLB()">🔄 Regenerate</button>
      <button class="lb-btn lb-btn-close-m" onclick="closeLB()">✕ Close</button>
    </div>
    <div id="lpv-lb-cap"></div>
  </div>
</div>
<script>
var _lbSceneIdx = -1;
var _lbBlenderPrompt = '';

function openLB(src, cap, sceneIdx, blenderPrompt) {
  document.getElementById('lpv-lb-img').src = src;
  document.getElementById('lpv-lb-cap').textContent = cap || '';
  document.getElementById('lpv-lightbox').classList.add('open');
  document.body.style.overflow = 'hidden';
  _lbSceneIdx = sceneIdx !== undefined ? sceneIdx : -1;
  _lbBlenderPrompt = blenderPrompt || '';
}
function closeLB() {
  document.getElementById('lpv-lightbox').classList.remove('open');
  document.getElementById('lpv-lb-img').src = '';
  document.body.style.overflow = '';
}
function downloadLBImg() {
  var src = document.getElementById('lpv-lb-img').src;
  var cap = document.getElementById('lpv-lb-cap').textContent || 'scene';
  var a = document.createElement('a');
  a.href = src;
  a.download = cap.replace(/[^a-z0-9]+/gi,'_').toLowerCase() + '.png';
  a.click();
}
function copyBlenderPrompt() {
  if (!_lbBlenderPrompt) { alert('No Blender prompt available for this scene.'); return; }
  navigator.clipboard.writeText(_lbBlenderPrompt).then(function(){
    var btn = document.getElementById('lb-blender-btn');
    var orig = btn.textContent;
    btn.textContent = '✓ Copied!';
    setTimeout(function(){ btn.textContent = orig; }, 2000);
  }).catch(function(){
    var ta = document.createElement('textarea');
    ta.value = _lbBlenderPrompt;
    document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
    alert('Blender prompt copied to clipboard!');
  });
}
function regenFromLB() {
  closeLB();
  if (_lbSceneIdx >= 0) {
    var btnId = 'gen_img_' + _lbSceneIdx;
    // Trigger the hidden streamlit button via click simulation
    setTimeout(function(){
      var btns = window.parent.document.querySelectorAll('button');
      // Send a message to parent
      window.parent.postMessage({type:'lpv_regen', idx: _lbSceneIdx}, '*');
    }, 200);
  }
}
document.getElementById('lpv-lightbox').addEventListener('click', function(e){ if(e.target===this) closeLB(); });
document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeLB(); });
</script>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "active_project": None, "active_storyboard": None,
        "editing_scene": None, "goto_editor": False, "gen_all_images": False,
        "regen_scene_idx": None
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
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

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
    return scenes

# ─── BLENDER PROMPT BUILDER ────────────────────────────────────────────────────
def build_blender_prompt(sc):
    """
    A production-ready Blender/Cycles prompt that a 3D artist can use directly.
    Focuses on exact object layout, materials, lighting, and camera — all Blender-native terminology.
    """
    title  = sc.get("title", "")
    assets = get_scene_assets(sc)
    labels = sc.get("labels", [])
    narr   = sc.get("narration", "")[:200]
    vd     = sc.get("visual_description", "")[:200]
    anim   = sc.get("animation", "").strip().replace("\\n", "\n")
    lines  = [l.strip() for l in anim.split("\n") if l.strip()]
    anim_str = " → ".join(lines[:4]) if lines else anim[:200]

    assets_str = ", ".join(assets) if assets else "primary subject"
    labels_str = ", ".join(labels) if labels else ""

    return (
        f"[BLENDER 4.x CYCLES RENDER PROMPT]\n\n"
        f"SCENE: {title}\n\n"
        f"3D OBJECTS TO MODEL (import as GLB or build in Blender):\n"
        f"  {assets_str}\n\n"
        f"KEY ANIMATION MOMENT TO FREEZE-FRAME:\n"
        f"  {anim_str}\n\n"
        f"CAMERA:\n"
        f"  Focal length: 50mm, Aperture f/2.8 (shallow DoF), 16:9 (1920×1080 or 1280×720)\n"
        f"  Composition: Rule-of-thirds, subject in left or center, action flow to right\n\n"
        f"LIGHTING SETUP (HDRI + manual):\n"
        f"  Key:   Area light 3200K 800W, upper-left 45°\n"
        f"  Fill:  Area light 6500K 200W, right side, low intensity\n"
        f"  Rim:   Point light teal #00d4cc 150W behind subject\n"
        f"  Bounce: Large white plane below-right for soft bounce\n"
        f"  World: HDRI studio grey, strength 0.3 (low, for subtle ambient)\n\n"
        f"MATERIALS (PBR Metallic-Roughness):\n"
        f"  Primary objects: Principled BSDF — Metallic 0.6, Roughness 0.3, slight anisotropy\n"
        f"  Accent parts: Emission node for glowing labels (hex #4f8ef7)\n"
        f"  Floor: Dark charcoal plane, Roughness 0.9, slight mirror for reflection\n\n"
        f"SCENE STAGING:\n"
        f"  {vd}\n"
        f"  Background: Studio void #12121e, no visible walls\n"
        f"  AO baked, Denoiser: OptiX or OpenImageDenoise, samples 256+\n\n"
        f"UI ANNOTATION LABELS (add as Text objects in Blender, Outlines only):\n"
        f"  {labels_str if labels_str else 'Label key parts with white text + blue outline'}\n\n"
        f"EDUCATIONAL CONTEXT:\n"
        f"  {narr}\n\n"
        f"RENDER SETTINGS:\n"
        f"  Engine: Cycles, GPU Compute\n"
        f"  Resolution: 1920×1080\n"
        f"  Samples: 256 (preview) / 512 (final)\n"
        f"  Color Management: Filmic, Medium High Contrast\n"
        f"  Output: PNG 16-bit, sRGB\n"
    )

# ─── IMAGE PROMPT: ANIMATION-LOGIC DRIVEN ─────────────────────────────────────
def build_image_prompt(sc):
    title  = sc.get("title", "")
    assets = ", ".join(get_scene_assets(sc))
    labels = ", ".join(sc.get("labels", []))
    narr   = sc.get("narration", "")[:180]
    vd     = sc.get("visual_description", "")[:200]
    raw_a  = sc.get("animation", "").strip()
    lines  = [l.strip() for l in raw_a.replace("\\n", "\n").split("\n") if l.strip()]
    anim   = " | ".join(lines) if lines else raw_a[:300]

    return (
        f"Professional 3D CGI educational animation storyboard frame. "
        f"Scene: '{title}'. "
        f"PRIMARY — Animation action to depict (show the key visual moment of this step): {anim}. "
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
    sys_p = (
        f"You are a Senior 3D Instructional Animator and Educational Script Writer. "
        f"Convert the input into EXACTLY {num_scenes} storyboard scenes.\n"
        "Return ONLY a valid JSON array. No markdown fences. No explanation. No preamble.\n"
        "Each element must have exactly these keys:\n"
        "  scene_number (int), title (str 3-6 words), assets (array of 3-6 lowercase_glb_names),\n"
        "  labels (array of 2-5 short UI caption strings), animation (str: numbered steps as plain text),\n"
        "  visual_description (str: 2-3 sentences on camera/lighting/layout — use Blender terminology),\n"
        "  narration (str: 2-4 PLAIN ENGLISH sentences a student can easily understand; "
        "use simple words, no jargon, explain concepts like you're talking to a curious 14-year-old; "
        "avoid passive voice; start with an action or observation)\n"
        "CRITICAL JSON RULES: Never use literal newline or tab characters inside any string value.\n"
        "Use the two-character sequence backslash-n to represent a line break inside a string.\n"
        "NARRATION RULES: Write narration in active voice. Use analogies when helpful. "
        "Keep sentences short (under 20 words each). Make every word count."
    )
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": sys_p},
                     {"role": "user",   "content": f"Create a 3D educational storyboard for:\n\n{text[:6000]}"}],
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

# ─── GEMINI IMAGE GEN ─────────────────────────────────────────────────────────
def _is_quota(code, msg):
    return code == 429 or "quota" in msg.lower() or "rate" in msg.lower()

def generate_scene_image_gemini(sc):
    if not GEMINI_API_KEY:
        return None, "no_key"
    prompt  = build_image_prompt(sc)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"],
                             "imageConfig": {"aspectRatio": "16:9", "imageSize": "1K"}}
    }
    last = "no_models"
    for model in GEMINI_MODELS:
        url = f"{GEMINI_BASE.format(model=model)}?key={GEMINI_API_KEY}"
        try:
            resp = requests.post(url, headers={"Content-Type": "application/json"},
                                 json=payload, timeout=90)
            if resp.status_code == 200:
                for part in (resp.json().get("candidates", [{}])[0]
                             .get("content", {}).get("parts", [])):
                    inline = part.get("inlineData", {})
                    if inline.get("mimeType", "").startswith("image/"):
                        return inline["data"], None
                last = "200_no_image"
            elif resp.status_code in (400, 404):
                last = f"{model}_unavailable"; continue
            else:
                try: msg = resp.json().get("error", {}).get("message", "")
                except: msg = resp.text[:200]
                if _is_quota(resp.status_code, msg):
                    return None, "quota"
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
        if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
            return base64.b64encode(resp.content).decode("utf-8"), None
        return None, f"pollinations_{resp.status_code}"
    except Exception as e:
        return None, str(e)

def generate_scene_image(sc, status_slot=None):
    def log(m):
        if status_slot: status_slot.caption(m)

    if GEMINI_API_KEY:
        b64, err = generate_scene_image_gemini(sc)
        if b64:
            log("✓ via Gemini"); return b64
        if err == "quota":
            log("Gemini quota → switching to Pollinations…")
        elif err not in ("no_key", "no_models", "200_no_image"):
            log("Gemini unavailable → switching to Pollinations…")

    b64, err = generate_scene_image_pollinations(sc)
    if b64:
        log("✓ via Pollinations"); return b64
    log(f"⚠ Image failed: {err}")
    return None

# ─── PDF EXPORT ────────────────────────────────────────────────────────────────
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

    C = dict(
        bg=HexColor("#04040c"), card=HexColor("#080814"), bord=HexColor("#1a1a30"),
        blue=HexColor("#4f8ef7"), purp=HexColor("#9b6ff8"), green=HexColor("#34d399"),
        ambr=HexColor("#fbbf24"), pink=HexColor("#f472b6"), text=HexColor("#eef0f8"),
        mute=HexColor("#454870"), teal=HexColor("#2dd4bf")
    )

    def S(n, **k):
        b = dict(fontName="Helvetica", fontSize=9, leading=13, textColor=C["text"], spaceAfter=2)
        b.update(k); return ParagraphStyle(n, **b)

    story = [
        Paragraph("LPVision Studio", S("H", fontSize=22, fontName="Helvetica-Bold", leading=26)),
        Paragraph(f"Storyboard Export · {sb_name}", S("sub", fontSize=11, textColor=C["mute"])),
        Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y at %H:%M')} · {len(scenes)} Scenes",
                  S("dt", fontSize=8, textColor=C["mute"])),
        HRFlowable(width="100%", thickness=1, color=C["bord"], spaceAfter=8)
    ]
    for i, sc in enumerate(scenes):
        snum  = sc.get("scene_number", i+1); title = sc.get("title", "Untitled")
        assets= get_scene_assets(sc);         labels= sc.get("labels", [])
        anim  = sc.get("animation", "").strip().replace("\\n", "\n")
        vd    = sc.get("visual_description", "").strip()
        narr  = sc.get("narration", "").strip(); b64 = sc.get("scene_image")

        img_cell = []
        if b64:
            try:
                pil = PILImage.open(io.BytesIO(base64.b64decode(b64)))
                b2  = io.BytesIO(); pil.save(b2, "PNG"); b2.seek(0)
                img_cell.append(RLImage(b2, width=70*mm, height=39.4*mm))
            except: img_cell.append(Paragraph("[Image error]", S("ie", fontSize=8, textColor=C["mute"])))
        else:
            img_cell.append(Paragraph("[ No Image ]", S("ni", fontSize=8, textColor=C["mute"], alignment=TA_CENTER)))

        al  = [l.strip() for l in anim.split("\n") if l.strip()]
        ah  = "<br/>".join([f"{k+1}. {l.lstrip('0123456789.) ')}" for k, l in enumerate(al)]) or "—"
        at  = "  ".join([f"[{a}]" for a in assets]) or "—"
        lt  = "  ".join([f"[{l}]" for l in labels]) or "—"

        data = [[
            [Paragraph(f"{snum:02d}", S("sn", fontSize=18, fontName="Helvetica-Bold",
                        textColor=C["blue"], alignment=TA_CENTER, leading=22))],
            img_cell,
            [Paragraph(f"SCENE {snum:02d}", S("sl", fontSize=6, fontName="Helvetica-Bold", textColor=C["mute"], spaceAfter=3)),
             Paragraph(title, S("st", fontSize=12, fontName="Helvetica-Bold", textColor=C["text"], leading=16)),
             Spacer(1, 4),
             Paragraph("3D ASSETS", S("al", fontSize=6, fontName="Helvetica-Bold", textColor=C["blue"], spaceAfter=2)),
             Paragraph(at, S("at", fontSize=7, textColor=C["blue"], leading=10)),
             Spacer(1, 3),
             Paragraph("UI LABELS", S("ll", fontSize=6, fontName="Helvetica-Bold", textColor=C["green"], spaceAfter=2)),
             Paragraph(lt, S("lt", fontSize=7, textColor=C["green"], leading=10))],
            [Paragraph("NARRATION", S("nl", fontSize=6, fontName="Helvetica-Bold", textColor=C["pink"], spaceAfter=3)),
             Paragraph(narr or "—", S("nb", fontSize=8, fontName="Helvetica-Oblique",
                        textColor=HexColor("#fce7f3"), leading=12))],
            [Paragraph("ANIMATION LOGIC", S("anl", fontSize=6, fontName="Helvetica-Bold", textColor=C["ambr"], spaceAfter=3)),
             Paragraph(ah, S("an", fontSize=7.5, textColor=HexColor("#fde68a"), leading=11)),
             Spacer(1, 5),
             Paragraph("VISUAL DESCRIPTION", S("vdl", fontSize=6, fontName="Helvetica-Bold", textColor=C["purp"], spaceAfter=3)),
             Paragraph(vd or "—", S("vd", fontSize=7.5, textColor=HexColor("#c4b5fd"), leading=11))]
        ]]
        tbl = Table(data, colWidths=[14*mm, 72*mm, 52*mm, 58*mm, 58*mm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C["card"]),
            ("BOX", (0, 0), (-1, -1), 1, C["bord"]),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, HexColor("#101020")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#0a1628")),
            ("LINEAFTER", (0, 0), (0, -1), 2, C["blue"]),
            ("LINEBEFORE", (3, 0), (3, -1), 2, C["pink"]),
            ("LINEBEFORE", (4, 0), (4, -1), 2, C["ambr"]),
        ]))
        story += [KeepTogether([tbl]), Spacer(1, 5)]

    story += [
        HRFlowable(width="100%", thickness=0.5, color=C["bord"], spaceBefore=6),
        Paragraph(f"LPVision Studio · {sb_name} · {len(scenes)} Scenes · © {datetime.now().year} LearningPad",
                  S("ft", fontSize=7, textColor=C["mute"], alignment=TA_CENTER))
    ]

    def on_page(canvas, doc):
        canvas.saveState(); canvas.setFillColor(C["bg"])
        canvas.rect(0, 0, landscape(A4)[0], landscape(A4)[1], fill=1, stroke=0); canvas.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0); return buf.getvalue(), None

# ─── UI HELPERS ────────────────────────────────────────────────────────────────
def pill_html(text, bg, color):
    return (f'<span class="pill-tag" style="background:{bg};color:{color};">{text}</span>')

def clickable_img_html(b64, scene_title, snum, blender_prompt):
    uri = f"data:image/png;base64,{b64}"
    cap = f"Scene {snum:02d}  ·  {scene_title}".replace("'", "&#39;").replace('"', '&quot;')
    bp  = blender_prompt.replace("'", "\\'").replace("\n", "\\n").replace('"', '\\"')[:2000]
    return (
        f'<div class="scene-img-wrap" onclick="openLB(\'{uri}\',\'{cap}\',{snum-1},\'{bp}\')">'
        f'<img src="{uri}" alt="{cap}"/>'
        f'<span class="zoom-hint">🔍 expand</span></div>'
    )

def no_image_html():
    return '''<div class="img-no-image">
      <span style="font-size:2rem;opacity:0.3;">🖼</span>
      <span style="font-size:11px;color:var(--txt-muted);">No image yet</span>
    </div>'''

def section_box_html(label, label_color, content_html, bg_override=None, left_accent=None):
    bg = bg_override or "var(--bg-raised)"
    acc = f"border-left:3px solid {left_accent};" if left_accent else ""
    return (
        f'<div class="sec-box" style="background:{bg};{acc}">'
        f'<div class="sec-box-label" style="color:{label_color};">{label}</div>'
        f'{content_html}</div>'
    )

def anim_steps_html(anim_raw):
    lines = [l.strip() for l in anim_raw.replace("\\n", "\n").replace("\r\n", "\n").split("\n") if l.strip()]
    if not lines:
        return '<span style="color:var(--txt-muted);font-size:11px;">—</span>'
    parts = []
    for idx, line in enumerate(lines):
        clean = line.lstrip("0123456789.) ") if line[:1].isdigit() else line
        parts.append(
            f'<div class="anim-step">'
            f'<div class="anim-step-num">{idx+1}</div>'
            f'<div class="anim-step-text">{clean}</div></div>'
        )
    return "".join(parts)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('''
    <div class="sidebar-brand">
      <div class="logo">LP</div>
      <div>
        <div class="brand-sub">LPVISION</div>
        <div class="brand-name">Studio</div>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div style="font-size:9px;font-weight:700;letter-spacing:0.2em;color:var(--txt-muted);text-transform:uppercase;margin-bottom:0.5rem;font-family:\'DM Mono\',monospace;">Projects</div>', unsafe_allow_html=True)

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
        lbl = f"{'▸ ' if is_active else ''}{proj['name']}  [{len(proj.get('storyboards',{}))}]"
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
    groq_ok = bool(GROQ_API_KEY); gem_ok = bool(GEMINI_API_KEY)
    st.markdown(f"""
    <div style="font-size:11px;color:var(--txt-muted);line-height:2.2;font-family:'DM Mono',monospace;">
      Groq&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:{'var(--accent-green)' if groq_ok else '#f87171'};">{'✓' if groq_ok else '✗'}</span>
      <span style="color:{'var(--accent-green)' if groq_ok else '#f87171'};font-size:10px;"> {'Connected' if groq_ok else 'Add GROQ_API_KEY'}</span><br>
      Gemini&nbsp;&nbsp;<span style="color:{'var(--accent-green)' if gem_ok else 'var(--accent-amber)'};">{'✓' if gem_ok else '⚠'}</span>
      <span style="color:{'var(--accent-green)' if gem_ok else 'var(--accent-amber)'};font-size:10px;"> {'Connected' if gem_ok else 'Pollinations fallback'}</span>
    </div>
    <div style="font-size:10px;color:var(--txt-muted);text-align:center;margin-top:12px;font-family:'DM Mono',monospace;">© 2026 LearningPad</div>
    """, unsafe_allow_html=True)

# ─── MAIN HEADER ───────────────────────────────────────────────────────────────
proj         = get_active_project()
proj_name    = proj.get("name", "Untitled")
storyboards  = proj.get("storyboards", {})
active_sb    = get_active_storyboard()
active_sb_id = st.session_state.active_storyboard

st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:0.5rem 0;border-bottom:1px solid var(--bd-subtle);margin-bottom:0.85rem;">
  <div style="display:flex;align-items:center;gap:10px;">
    <span style="font-size:13px;font-weight:500;color:var(--txt-muted);font-family:'DM Mono',monospace;">{proj_name}</span>
    <span style="color:var(--txt-muted);">›</span>
    <span style="font-size:15px;font-weight:800;color:var(--txt-primary);font-family:'Syne',sans-serif;letter-spacing:-0.01em;">
      {active_sb['name'] if active_sb else 'Select a Storyboard'}
    </span>
  </div>
  <div style="font-size:11px;color:var(--txt-muted);font-family:'DM Mono',monospace;">
    {len(storyboards)} storyboard{'s' if len(storyboards)!=1 else ''}
  </div>
</div>
""", unsafe_allow_html=True)

default_tab = 1 if st.session_state.goto_editor else 0
tabs = st.tabs(["📋 STORYBOARDS", "🎬 EDITOR", "📦 EXPORT / IMPORT"])

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
        st.markdown('<div style="text-align:center;padding:3rem;color:var(--txt-muted);">No storyboards yet — create one above.</div>', unsafe_allow_html=True)
    else:
        for sbid, sb in storyboards.items():
            n_sc = len(sb.get("scenes", [])); is_open = sbid == active_sb_id
            ci, co, cd = st.columns([6, 1.5, 1])
            with ci:
                c = 'var(--accent-blue)' if is_open else 'var(--txt-primary)'
                n_img = sum(1 for s in sb.get("scenes",[]) if s.get("scene_image"))
                st.markdown(f"""<div style="padding:0.5rem 0;">
                  <div style="font-size:14px;font-weight:700;color:{c};font-family:'Syne',sans-serif;">{'▸ ' if is_open else ''}{sb['name']}</div>
                  <div style="font-size:11px;color:var(--txt-muted);font-family:'DM Mono',monospace;margin-top:2px;">{sb.get('created','')} · {n_sc} scenes · {n_img} images</div>
                </div>""", unsafe_allow_html=True)
            with co:
                if st.button("Open →", key=f"open_{sbid}", use_container_width=True):
                    st.session_state.active_storyboard = sbid
                    st.session_state.editing_scene = None
                    st.session_state.goto_editor   = True
                    st.rerun()
            with cd:
                if st.button("🗑", key=f"del_{sbid}", use_container_width=True):
                    del st.session_state.projects[st.session_state.active_project]["storyboards"][sbid]
                    if active_sb_id == sbid:
                        st.session_state.active_storyboard = None
                        st.session_state.goto_editor = False
                    st.rerun()
            st.markdown('<hr style="margin:4px 0;border-color:var(--bd-subtle);">', unsafe_allow_html=True)

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
                num_scenes  = st.slider("Scenes to generate", 3, 12, 6, key="num_scenes_slider")
                input_type  = st.radio("Source", ["Plain Text", "PDF Document"], horizontal=True, key="input_type_radio")
            with c2:
                final_text = ""
                if input_type == "Plain Text":
                    final_text = st.text_area("Paste content", height=130,
                        placeholder="e.g. Working of a Steam Engine, Photosynthesis…", key="plain_text_input")
                    st.caption(f"{len(final_text)} chars")
                else:
                    pdf_up = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_uploader")
                    if pdf_up:
                        reader = PyPDF2.PdfReader(pdf_up)
                        for pg in reader.pages: final_text += (pg.extract_text() or "")
                        st.success(f"PDF extracted · {len(final_text)} chars")

            gc, cc = st.columns(2)
            with gc:
                gen_btn = st.button(f"🚀 Generate {num_scenes} Scenes", key="gen_btn", use_container_width=True)
            with cc:
                clr_btn = st.button("✕ Clear All Scenes", key="clear_btn", use_container_width=True)
            if clr_btn:
                save_scenes([]); st.session_state.editing_scene = None; st.rerun()
            if gen_btn:
                if not final_text.strip():
                    st.warning("Paste content or upload a PDF first.")
                else:
                    with st.spinner(f"Generating {num_scenes} scenes with Groq…"):
                        new_sc = generate_scenes_groq(final_text, num_scenes)
                    if new_sc:
                        save_scenes(new_sc); st.session_state.editing_scene = None
                        st.session_state.goto_editor = True
                        st.success(f"✓ {len(new_sc)} scenes generated!"); st.rerun()

        scenes = active_sb.get("scenes", [])

        if not scenes:
            st.markdown("""<div style="text-align:center;padding:5rem 2rem;
                color:var(--txt-muted); border:1.5px dashed var(--bd-subtle);
                border-radius:16px;margin-top:1rem;background:var(--bg-card);">
              <div style="font-size:3rem;margin-bottom:0.5rem;">🎞</div>
              <div style="font-size:15px;font-weight:700;color:var(--txt-secondary);font-family:'Syne',sans-serif;">No scenes yet</div>
              <div style="font-size:13px;margin-top:0.4rem;">Expand the controls above and hit Generate.</div>
            </div>""", unsafe_allow_html=True)
        else:
            n_images  = sum(1 for s in scenes if s.get("scene_image"))
            n_missing = len(scenes) - n_images

            # ── Header bar
            hc1, hc2 = st.columns([3, 1])
            with hc1:
                st.markdown(f"""
                <div style="padding:0.65rem 1rem;background:var(--bg-card);border:1px solid var(--bd-subtle);
                            border-radius:10px;margin-bottom:0.5rem;">
                  <span style="font-size:14px;font-weight:800;color:var(--txt-primary);font-family:'Syne',sans-serif;">{active_sb['name']}</span>
                  <span style="font-size:11px;color:var(--txt-muted);font-family:'DM Mono',monospace;margin-left:16px;">
                    {len(scenes)} SCENES &nbsp;·&nbsp; {n_images} IMAGES
                    {f"&nbsp;·&nbsp; <span style='color:var(--accent-amber);'>{n_missing} MISSING</span>" if n_missing else ""}
                  </span>
                </div>""", unsafe_allow_html=True)
            with hc2:
                gen_all_lbl = f"🖼 Generate All ({n_missing})" if n_missing else "🔄 Regen All"
                if st.button(gen_all_lbl, key="gen_all_btn", use_container_width=True):
                    st.session_state.gen_all_images = True; st.rerun()

            # ── GENERATE ALL FLOW
            if st.session_state.gen_all_images:
                st.session_state.gen_all_images = False
                targets = [i for i, s in enumerate(scenes) if not s.get("scene_image")]
                if not targets: targets = list(range(len(scenes)))
                total    = len(targets)
                prog_bar = st.progress(0, text="Starting…")
                stat_txt = st.empty()
                for step, idx in enumerate(targets):
                    sc   = scenes[idx]
                    snum = sc.get("scene_number", idx+1)
                    ttl  = sc.get("title", "")
                    stat_txt.markdown(
                        f'<div class="gen-status">Generating Scene {snum:02d} — <em>{ttl}</em>…</div>',
                        unsafe_allow_html=True)
                    slot = st.empty()
                    b64  = generate_scene_image(sc, slot)
                    if b64:
                        scenes[idx]["scene_image"] = b64
                        save_scenes(scenes)
                    prog_bar.progress(int((step+1)/total*100),
                                      text=f"Scene {snum:02d} done  ({step+1}/{total})")
                    time.sleep(0.3)
                prog_bar.progress(100, text="✓ All images done!")
                stat_txt.success(f"✓ {total} images generated!")
                time.sleep(1.2); st.rerun()

            # ── SCENE CARDS
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
                bp      = build_blender_prompt(sc)  # Blender prompt for this scene

                # ── Scene header row
                h1, h2, h3, h4 = st.columns([0.06, 0.50, 0.20, 0.24])
                with h1:
                    st.markdown(f'<div class="scene-num-badge">{snum:02d}</div>', unsafe_allow_html=True)
                with h2:
                    st.markdown(f'<div class="scene-title">{title}</div>', unsafe_allow_html=True)
                with h3:
                    if st.button("✅ Done" if editing else "✏️ Edit Scene",
                                 key=f"edit_toggle_{i}", use_container_width=True):
                        st.session_state.editing_scene = None if editing else i
                        st.rerun()
                with h4:
                    gen_img = st.button(
                        "🔄 Regenerate Image" if img_b64 else "🖼 Generate Image",
                        key=f"gen_img_{i}", use_container_width=True)

                # ── EDIT MODE
                if editing:
                    st.markdown('<div style="background:rgba(37,68,127,0.08);border:1px solid var(--accent-blue);'
                                'border-radius:12px;padding:1rem 1.1rem;margin:0.5rem 0;">',
                                unsafe_allow_html=True)
                    ea, eb = st.columns(2)
                    with ea:
                        new_title  = st.text_input("Scene Title", value=title, key=f"e_title_{i}")
                        new_assets = st.text_input("Assets (comma-separated GLB names)", value=", ".join(assets), key=f"e_assets_{i}")
                        new_labels = st.text_input("Labels (comma-separated UI text)", value=", ".join(labels), key=f"e_labels_{i}")
                    with eb:
                        new_narr = st.text_area("Narration (plain English, easy to understand)", value=narr, height=110, key=f"e_narr_{i}")
                        new_vd   = st.text_area("Visual Description (Blender terminology)", value=vd, height=75, key=f"e_vd_{i}")
                    new_anim = st.text_area("Animation Logic", value=anim, height=90, key=f"e_anim_{i}")

                    # Blender prompt preview
                    with st.expander("🟢 Preview Blender Prompt", expanded=False):
                        st.code(build_blender_prompt({
                            "title": new_title, "assets": [x.strip() for x in new_assets.split(",") if x.strip()],
                            "labels": [x.strip() for x in new_labels.split(",") if x.strip()],
                            "narration": new_narr, "visual_description": new_vd, "animation": new_anim
                        }), language="text")

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
                            st.session_state.editing_scene = None; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                # ── DISPLAY MODE
                else:
                    c_img, c_a, c_b, c_n = st.columns([1, 1, 1, 2])
                    with c_img:
                        if img_b64:
                            st.markdown(clickable_img_html(img_b64, title, snum, bp), unsafe_allow_html=True)
                            # Blender badge below image
                            st.markdown(
                                f'<div style="margin-top:5px;">'
                                f'<span class="blender-badge">🟢 Blender ready</span></div>',
                                unsafe_allow_html=True)
                        else:
                            st.markdown(no_image_html(), unsafe_allow_html=True)

                    with c_a:
                        tags = "".join([pill_html(a, "#0f1f3d", "#60a5fa") for a in assets]) \
                               or '<span style="color:var(--txt-muted);font-size:11px;">—</span>'
                        st.markdown(section_box_html("🔷 3D Assets · GLB", "#4f8ef7",
                            f'<div style="line-height:2;">{tags}</div>'), unsafe_allow_html=True)

                    with c_b:
                        ltags = "".join([pill_html(l, "#0f2d1a", "#34d399") for l in labels]) \
                                or '<span style="color:var(--txt-muted);font-size:11px;">—</span>'
                        st.markdown(section_box_html("🟢 UI Labels", "#34d399",
                            f'<div style="line-height:2;">{ltags}</div>'), unsafe_allow_html=True)

                    with c_n:
                        # Narration: plain English, easy to read
                        st.markdown(section_box_html("🎙 Narration",
                            "#f472b6",
                            f'<div class="narration-text">{narr or "—"}</div>',
                            left_accent="#f472b6"), unsafe_allow_html=True)

                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                    c_anim, c_vd, c_blender = st.columns([2, 2, 1])
                    with c_anim:
                        steps_html = anim_steps_html(anim)
                        st.markdown(section_box_html("⚡ Animation Logic", "#fbbf24", steps_html,
                            left_accent="#fbbf24"), unsafe_allow_html=True)
                    with c_vd:
                        st.markdown(section_box_html("🎨 Visual Description", "#9b6ff8",
                            f'<div style="font-size:12px;color:#c4b5fd;line-height:1.7;">{vd or "—"}</div>',
                            left_accent="#9b6ff8"), unsafe_allow_html=True)
                    with c_blender:
                        # Blender prompt inline download
                        bp_bytes = bp.encode("utf-8")
                        st.download_button(
                            label="🟢 Blender Prompt",
                            data=bp_bytes,
                            file_name=f"scene_{snum:02d}_blender.txt",
                            mime="text/plain",
                            key=f"dl_bp_{i}",
                            use_container_width=True
                        )
                        if img_b64:
                            img_bytes = base64.b64decode(img_b64)
                            st.download_button(
                                label="⬇ Image",
                                data=img_bytes,
                                file_name=f"scene_{snum:02d}_{title.replace(' ','_').lower()}.png",
                                mime="image/png",
                                key=f"dl_img_{i}",
                                use_container_width=True
                            )

                # ── Single image gen
                if gen_img:
                    with st.spinner(f"Generating image for Scene {snum:02d}…"):
                        slot = st.empty()
                        b64  = generate_scene_image(sc, slot)
                    if b64:
                        scenes[i]["scene_image"] = b64
                        save_scenes(scenes)
                        st.success(f"✓ Image generated for Scene {snum:02d}!"); st.rerun()

                # ── Delete + divider
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                _, dc = st.columns([8, 1])
                with dc:
                    if st.button("🗑 Delete", key=f"del_scene_{i}", use_container_width=True):
                        scenes.pop(i); save_scenes(scenes)
                        if st.session_state.editing_scene == i:
                            st.session_state.editing_scene = None
                        st.rerun()
                st.markdown('<div class="scene-divider"></div>', unsafe_allow_html=True)

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
            st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:0.15em;color:var(--txt-muted);text-transform:uppercase;margin-bottom:0.75rem;font-family:\'DM Mono\',monospace;">Export</div>', unsafe_allow_html=True)
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
                st.download_button("📥 Download Storyboard JSON",
                    data=json.dumps(payload_out, indent=2),
                    file_name=f"{active_sb['name'].replace(' ','_')}_storyboard.json",
                    mime="application/json", use_container_width=True)

                # ── Blender prompts pack
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                all_bp = "\n\n" + ("="*60 + "\n\n").join(
                    [build_blender_prompt(sc) for sc in scenes]
                )
                st.download_button("🟢 Download All Blender Prompts (.txt)",
                    data=all_bp.encode("utf-8"),
                    file_name=f"{active_sb['name'].replace(' ','_')}_blender_prompts.txt",
                    mime="text/plain", use_container_width=True)

                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:10px;color:var(--txt-muted);margin-bottom:6px;font-family:\'DM Mono\',monospace;">PDF export requires <code>reportlab</code> and <code>Pillow</code>.</div>', unsafe_allow_html=True)
                if st.button("📄 Generate PDF Storyboard", key="gen_pdf_btn", use_container_width=True):
                    with st.spinner("Building PDF…"):
                        pdf_bytes, pdf_err = generate_storyboard_pdf(active_sb["name"], scenes)
                    if pdf_bytes:
                        st.session_state["_pdf_bytes"] = pdf_bytes
                        st.session_state["_pdf_name"]  = active_sb["name"]
                        st.success(f"✓ PDF ready — {len(pdf_bytes)//1024} KB"); st.rerun()
                    else:
                        st.error(f"PDF failed: {pdf_err}")

                if "_pdf_bytes" in st.session_state and st.session_state.get("_pdf_name") == active_sb["name"]:
                    st.download_button("⬇️ Download PDF",
                        data=st.session_state["_pdf_bytes"],
                        file_name=f"{active_sb['name'].replace(' ','_')}_storyboard.pdf",
                        mime="application/pdf", use_container_width=True)

                st.markdown("---")
                st.markdown("**Scene Table Preview**")
                hdr    = "| # | Title | Assets | Labels | Narration |"
                sep2   = "|---|-------|--------|--------|-----------|"
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
            st.markdown('<div style="font-size:10px;font-weight:700;letter-spacing:0.15em;color:var(--txt-muted);text-transform:uppercase;margin-bottom:0.75rem;font-family:\'DM Mono\',monospace;">Import into Active Storyboard</div>', unsafe_allow_html=True)
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
                        if st.button("⬆ Apply Imported Scenes", key="apply_import"):
                            save_scenes(imp_sc); st.session_state.editing_scene = None
                            st.session_state.goto_editor = True; st.rerun()
                except Exception as e:
                    st.error(f"Parse error: {e}")
