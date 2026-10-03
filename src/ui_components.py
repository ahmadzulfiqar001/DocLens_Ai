"""Reusable UI components, custom styling, bespoke vector logo, static AI avatar,
and layout helpers for DocuLens AI.
Delivers a high-contrast Cyber Emerald & Obsidian Noir aesthetic with glassmorphic cards,
radiant glowing accents, accessible typography, and authentic RTL Urdu support.
"""
import base64
import os
from typing import Optional, List, Dict, Any

def get_logo_data_uri() -> str:
    """Reads assets/logo.svg and returns a self-contained base64 data URI."""
    logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.svg")
    try:
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        pass
    return ""

# Custom CSS for High-Contrast Cyber Emerald & Obsidian Noir
CUSTOM_CSS = """
<style>
/* Modern typography import */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Noto+Nastaliq+Urdu:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Background atmospheric lighting: High-contrast Obsidian Noir with Emerald & Amber glows */
.stApp {
    background-color: #080B09;
    background-image: 
        radial-gradient(at 0% 0%, rgba(0, 229, 153, 0.10) 0px, transparent 48%),
        radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.08) 0px, transparent 45%),
        radial-gradient(at 50% 100%, rgba(245, 158, 11, 0.04) 0px, transparent 50%);
    background-attachment: fixed;
    color: #F8FAFC;
}

/* Glassmorphic Container Cards with crisp contrasting borders */
.dl-card {
    background: #0E1613;
    border: 1px solid rgba(0, 229, 153, 0.20);
    border-radius: 14px;
    padding: 1.35rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.dl-card:hover {
    border-color: rgba(0, 229, 153, 0.45);
    box-shadow: 0 14px 30px -4px rgba(0, 229, 153, 0.20), 0 10px 10px -5px rgba(0, 0, 0, 0.6);
}

.dl-card-glow-primary, .dl-card-glow-emerald, .dl-card-glow-indigo {
    border-left: 4px solid #00E599;
}

.dl-card-glow-amber {
    border-left: 4px solid #F59E0B;
}

.dl-card-glow-rose {
    border-left: 4px solid #FF4D6D;
}

/* Metric Stats Cards */
.stat-box {
    background: #111A16;
    border: 1px solid rgba(0, 229, 153, 0.22);
    border-radius: 12px;
    padding: 1rem 0.9rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.stat-value {
    font-size: 1.95rem;
    font-weight: 800;
    line-height: 1.2;
    margin: 0.25rem 0;
    background: linear-gradient(135deg, #FFFFFF 0%, #A7F3D0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94A3B8;
}

/* High-Contrast Pill Badges */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.badge-high {
    background: rgba(255, 77, 109, 0.18);
    color: #FF8FA3;
    border: 1px solid rgba(255, 77, 109, 0.45);
}

.badge-med {
    background: rgba(245, 158, 11, 0.18);
    color: #FCD34D;
    border: 1px solid rgba(245, 158, 11, 0.45);
}

.badge-low {
    background: rgba(20, 184, 166, 0.18);
    color: #5EEAD4;
    border: 1px solid rgba(20, 184, 166, 0.45);
}

.badge-clear {
    background: rgba(0, 229, 153, 0.18);
    color: #34D399;
    border: 1px solid rgba(0, 229, 153, 0.45);
}

.badge-source {
    background: rgba(0, 229, 153, 0.14);
    color: #6EE7B7;
    border: 1px solid rgba(0, 229, 153, 0.35);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-weight: 600;
}

/* Source quotation callout */
.quote-callout {
    background: #090E0B;
    border-left: 3px solid #00E599;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    margin: 0.7rem 0;
    font-style: italic;
    color: #F1F5F9;
    font-size: 0.88rem;
}

/* Urdu RTL Presentation */
.rtl-text {
    direction: rtl;
    text-align: right;
    font-family: 'Noto Nastaliq Urdu', 'Segoe UI', Tahoma, sans-serif;
    line-height: 2.2;
    font-size: 1.05rem;
}

.ltr-inline {
    direction: ltr;
    display: inline-block;
    unicode-bidi: embed;
}

/* Medical Avatar Header Card */
.avatar-header {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    background: linear-gradient(135deg, rgba(0, 229, 153, 0.12) 0%, rgba(20, 184, 166, 0.08) 100%);
    border: 1px solid rgba(0, 229, 153, 0.28);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1.3rem;
}

.avatar-badge-tag {
    background: rgba(0, 229, 153, 0.18);
    border: 1px solid rgba(0, 229, 153, 0.4);
    color: #00E599;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    letter-spacing: 0.05em;
}

/* Button overrides for high-contrast neon cyber emerald accent */
div.stButton > button {
    background: linear-gradient(135deg, #059669 0%, #00E599 100%);
    color: #041B12 !important;
    font-weight: 700;
    border: 1px solid rgba(0, 229, 153, 0.3);
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    box-shadow: 0 4px 14px 0 rgba(0, 229, 153, 0.35);
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #047857 0%, #10B981 100%);
    color: #FFFFFF !important;
    box-shadow: 0 6px 20px 0 rgba(0, 229, 153, 0.55);
    transform: translateY(-1px);
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #0C1310;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(0, 229, 153, 0.15);
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    border-radius: 8px;
    color: #94A3B8;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background-color: #00E599 !important;
    color: #041B12 !important;
    font-weight: 700 !important;
}

/* Dropzone styling for File Uploader */
[data-testid="stFileUploaderDropzone"] {
    background-color: #0E1613 !important;
    border: 2px dashed rgba(0, 229, 153, 0.30) !important;
    border-radius: 12px !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #00E599 !important;
    background-color: rgba(0, 229, 153, 0.05) !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #070A09;
    border-right: 1px solid rgba(0, 229, 153, 0.14);
}
</style>
"""

# Static Avatar SVG (AI Medical / Report Assistant)
STATIC_AI_ASSISTANT_AVATAR_SVG = """<svg width="64" height="64" viewBox="0 0 68 68" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="34" cy="34" r="32" fill="url(#avatar_grad)" stroke="#00E599" stroke-width="2.5"/><circle cx="34" cy="34" r="28" fill="#0A110E"/><path d="M34 18V36M34 36C34 41 38 45 43 45C48 45 52 41 52 36V28" stroke="#34D399" stroke-width="2.5" stroke-linecap="round"/><path d="M34 36C34 41 30 45 25 45C20 45 16 41 16 36V28" stroke="#34D399" stroke-width="2.5" stroke-linecap="round"/><rect x="30" y="24" width="8" height="8" rx="2" fill="#00E599"/><path d="M34 22V34M28 28H40" stroke="#041B12" stroke-width="2.5" stroke-linecap="round"/><circle cx="16" cy="26" r="3" fill="#2DD4BF"/><circle cx="52" cy="26" r="3" fill="#2DD4BF"/><defs><linearGradient id="avatar_grad" x1="0" y1="0" x2="68" y2="68" gradientUnits="userSpaceOnUse"><stop stop-color="#00E599"/><stop offset="0.5" stop-color="#14B8A6"/><stop offset="1" stop-color="#059669"/></linearGradient></defs></svg>"""

def render_sidebar_header(app_name: str, app_version: str) -> str:
    """Renders the high-contrast logo and branding in the Streamlit sidebar without markdown split hazard."""
    logo_uri = get_logo_data_uri()
    img_html = f'<img src="{logo_uri}" width="38" height="38" style="vertical-align:middle;border-radius:8px;" />' if logo_uri else '🔍'
    return f"""<div style="display:flex;align-items:center;gap:10px;padding:4px 0 12px 0;"><div style="flex-shrink:0;">{img_html}</div><div><div style="font-size:1.32rem;font-weight:800;color:#FFFFFF;line-height:1.2;">Docu<span style="color:#00E599;">Lens</span> <span style="font-size:0.65rem;background:rgba(0,229,153,0.18);color:#00E599;padding:2px 5px;border-radius:4px;border:1px solid rgba(0,229,153,0.35);font-weight:800;vertical-align:middle;">AI</span></div><div style="font-size:0.72rem;color:#94A3B8;margin-top:2px;">v{app_version} • Grounded Document Intelligence</div></div></div>"""

def render_hero_banner(active_mode: str, active_language: str, app_tagline: str) -> str:
    """Renders the top application hero banner without markdown split hazard."""
    logo_uri = get_logo_data_uri()
    img_html = f'<img src="{logo_uri}" width="46" height="46" style="vertical-align:middle;border-radius:10px;" />' if logo_uri else '🔍'
    return f"""<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;"><div style="flex-shrink:0;">{img_html}</div><div><div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;"><h1 style="margin:0;font-size:2rem;font-weight:800;color:#FFFFFF;letter-spacing:-0.02em;line-height:1.2;">{active_mode}</h1><span class="badge-pill badge-source">{active_language}</span></div><p style="margin:3px 0 0 0;color:#94A3B8;font-size:0.88rem;">{app_tagline}</p></div></div>"""

def render_medical_avatar_banner():
    """Renders the static AI Report Assistant avatar banner compliant with PRD Section 4."""
    return f"""<div class="avatar-header"><div style="flex-shrink:0;">{STATIC_AI_ASSISTANT_AVATAR_SVG}</div><div style="flex-grow:1;"><div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.2rem;"><span style="font-size:1.15rem;font-weight:700;color:#FFFFFF;">AI Report Assistant</span><span class="avatar-badge-tag">AI Powered • Non-Diagnostic</span></div><p style="margin:0;font-size:0.82rem;color:#94A3B8;line-height:1.4;">Objective laboratory observations and educational test explanations. Does not diagnose health conditions, prescribe therapy, or replace consultation with a qualified clinical physician.</p></div></div>"""

def get_priority_badge(priority: str) -> str:
    """Returns an HTML badge pill for review priority."""
    p_clean = priority.strip().lower()
    if p_clean == "high":
        return '<span class="badge-pill badge-high">⚠️ High Priority</span>'
    elif p_clean == "medium":
        return '<span class="badge-pill badge-med">⚖️ Medium Priority</span>'
    elif p_clean == "low":
        return '<span class="badge-pill badge-low">ℹ️ Low Priority</span>'
    elif "no flagged" in p_clean:
        return '<span class="badge-pill badge-clear">✅ No Flagged Issues</span>'
    else:
        return f'<span class="badge-pill badge-low">{priority}</span>'

def get_medical_comparison_badge(comparison: str, has_conflict: bool = False) -> str:
    """Returns a styled HTML badge pill for medical range results."""
    comp_clean = comparison.strip().lower()
    if has_conflict:
        return f'<span class="badge-pill badge-high" title="Conflict between lab flag and numeric range">⚡ {comparison} (Conflict)</span>'
    if "above" in comp_clean:
        return '<span class="badge-pill badge-high">🔺 Above range</span>'
    elif "below" in comp_clean:
        return '<span class="badge-pill badge-med">🔻 Below range</span>'
    elif "within" in comp_clean:
        return '<span class="badge-pill badge-clear">✓ Within range</span>'
    else:
        return '<span class="badge-pill badge-low">❓ Cannot assess from range</span>'

def render_html(html_str: str):
    """Safely renders HTML without Markdown indentation or code block interpretation."""
    import textwrap
    import streamlit as st
    clean_html = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(clean_html)
    else:
        st.markdown(clean_html, unsafe_allow_html=True)
