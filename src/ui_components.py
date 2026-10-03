"""Reusable UI components, custom styling, bespoke vector logo, static AI avatar,
and layout helpers for DocuLens AI.
Delivers a high-contrast Cyber Emerald & Obsidian Noir aesthetic with glassmorphic cards,
radiant glowing accents, accessible typography, and authentic RTL Urdu support.
"""
from typing import Optional, List, Dict, Any

# Standalone DocuLens AI Vector Logo Icon SVG
DOCULENS_LOGO_ICON_SVG = """
<svg width="42" height="42" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="lensRingGrad" x1="0" y1="0" x2="200" y2="200" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#00E599"/>
      <stop offset="50%" stop-color="#10B981"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <linearGradient id="bladeGrad1" x1="50" y1="50" x2="150" y2="150" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#00E599" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="#047857" stop-opacity="0.25"/>
    </linearGradient>
    <radialGradient id="bgGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00E599" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#00E599" stop-opacity="0"/>
    </radialGradient>
    <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Ambient optical glow -->
  <circle cx="100" cy="100" r="92" fill="url(#bgGlow)"/>

  <!-- Calibration Track -->
  <circle cx="100" cy="100" r="86" stroke="url(#lensRingGrad)" stroke-width="2.5" stroke-dasharray="6 4" opacity="0.8"/>
  <circle cx="100" cy="100" r="92" stroke="#00E599" stroke-width="1.2" opacity="0.35"/>
  
  <!-- Optical Target Reticle Ticks -->
  <line x1="100" y1="6" x2="100" y2="18" stroke="#00E599" stroke-width="3" stroke-linecap="round"/>
  <line x1="100" y1="182" x2="100" y2="194" stroke="#00E599" stroke-width="3" stroke-linecap="round"/>
  <line x1="6" y1="100" x2="18" y2="100" stroke="#00E599" stroke-width="3" stroke-linecap="round"/>
  <line x1="182" y1="100" x2="194" y2="100" stroke="#00E599" stroke-width="3" stroke-linecap="round"/>

  <!-- Main Chassis Ring -->
  <circle cx="100" cy="100" r="70" fill="#0A110E" stroke="url(#lensRingGrad)" stroke-width="3.2" filter="url(#glowFilter)"/>

  <!-- Aperture Iris Blades -->
  <g opacity="0.95">
    <path d="M100 42 L138 64 L120 102 Z" fill="url(#bladeGrad1)" stroke="#00E599" stroke-width="1.2"/>
    <path d="M138 64 L158 100 L120 120 Z" fill="url(#bladeGrad1)" stroke="#00E599" stroke-width="1.2"/>
    <path d="M158 100 L138 136 L100 120 Z" fill="url(#bladeGrad1)" stroke="#00E599" stroke-width="1.2"/>
    <path d="M138 136 L100 158 L80 120 Z" fill="url(#bladeGrad1)" stroke="#00E599" stroke-width="1.2"/>
    <path d="M100 158 L62 136 L80 100 Z" fill="url(#bladeGrad1)" stroke="#00E599" stroke-width="1.2"/>
    <path d="M62 136 L42 100 L80 80 Z" fill="url(#bladeGrad1)" stroke="#00E599" stroke-width="1.2"/>
    <path d="M42 100 L62 64 L100 80 Z" fill="url(#bladeGrad1)" stroke="#00E599" stroke-width="1.2"/>
    <path d="M62 64 L100 42 L120 80 Z" fill="url(#bladeGrad1)" stroke="#00E599" stroke-width="1.2"/>
  </g>

  <!-- Central Optical Core Aperture -->
  <circle cx="100" cy="100" r="28" fill="#040806" stroke="#00E599" stroke-width="2.5"/>

  <!-- Glowing AI Intelligence Focal Star / Prism -->
  <path d="M100 78 Q100 100 78 100 Q100 100 100 122 Q100 100 122 100 Q100 100 100 78 Z" fill="#FFFFFF"/>
  <circle cx="100" cy="100" r="4.5" fill="#00E599"/>

  <!-- Precision Corner Reticles -->
  <circle cx="85" cy="85" r="1.5" fill="#34D399"/>
  <circle cx="115" cy="85" r="1.5" fill="#34D399"/>
  <circle cx="85" cy="115" r="1.5" fill="#34D399"/>
  <circle cx="115" cy="115" r="1.5" fill="#34D399"/>
</svg>
"""

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
        radial-gradient(at 0% 0%, rgba(0, 229, 153, 0.12) 0px, transparent 48%),
        radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.09) 0px, transparent 45%),
        radial-gradient(at 50% 100%, rgba(245, 158, 11, 0.05) 0px, transparent 50%);
    background-attachment: fixed;
    color: #F8FAFC;
}

/* Glassmorphic Container Cards with crisp contrasting borders */
.dl-card {
    background: rgba(14, 20, 17, 0.82);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(0, 229, 153, 0.18);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.6), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.dl-card:hover {
    border-color: rgba(0, 229, 153, 0.45);
    box-shadow: 0 14px 35px -4px rgba(0, 229, 153, 0.22), 0 10px 10px -5px rgba(0, 0, 0, 0.6);
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
    background: rgba(18, 26, 21, 0.75);
    border: 1px solid rgba(0, 229, 153, 0.2);
    border-radius: 14px;
    padding: 1.1rem 1rem;
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
    padding: 0.28rem 0.8rem;
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
    background: rgba(10, 17, 13, 0.88);
    border-left: 3px solid #00E599;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1.1rem;
    margin: 0.75rem 0;
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
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
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
    color: #041B12;
    font-weight: 700;
    border: 1px solid rgba(0, 229, 153, 0.3);
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    box-shadow: 0 4px 14px 0 rgba(0, 229, 153, 0.35);
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #047857 0%, #10B981 100%);
    color: #FFFFFF;
    box-shadow: 0 6px 20px 0 rgba(0, 229, 153, 0.55);
    transform: translateY(-1px);
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(14, 22, 18, 0.7);
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(0, 229, 153, 0.14);
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

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #080C0A;
    border-right: 1px solid rgba(0, 229, 153, 0.14);
}
</style>
"""

# Static Avatar SVG (AI Medical / Report Assistant)
STATIC_AI_ASSISTANT_AVATAR_SVG = """
<svg width="68" height="68" viewBox="0 0 68 68" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="34" cy="34" r="32" fill="url(#avatar_grad)" stroke="#00E599" stroke-width="2.5" stroke-dasharray="2 0"/>
  <circle cx="34" cy="34" r="28" fill="#0A110E"/>
  <!-- Stethoscope / Medical Cross Motif -->
  <path d="M34 18V36M34 36C34 41 38 45 43 45C48 45 52 41 52 36V28" stroke="#34D399" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M34 36C34 41 30 45 25 45C20 45 16 41 16 36V28" stroke="#34D399" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Cross Center -->
  <rect x="30" y="24" width="8" height="8" rx="2" fill="#00E599"/>
  <path d="M34 22V34M28 28H40" stroke="#041B12" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Sensor nodes -->
  <circle cx="16" cy="26" r="3" fill="#2DD4BF"/>
  <circle cx="52" cy="26" r="3" fill="#2DD4BF"/>
  <defs>
    <linearGradient id="avatar_grad" x1="0" y1="0" x2="68" y2="68" gradientUnits="userSpaceOnUse">
      <stop stop-color="#00E599"/>
      <stop offset="0.5" stop-color="#14B8A6"/>
      <stop offset="1" stop-color="#059669"/>
    </linearGradient>
  </defs>
</svg>
"""

def render_sidebar_header(app_name: str, app_version: str) -> str:
    """Renders the high-contrast logo and branding in the Streamlit sidebar."""
    return f"""
    <div style="padding: 0.4rem 0 0.9rem 0;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div style="flex-shrink: 0; line-height: 0;">
                {DOCULENS_LOGO_ICON_SVG}
            </div>
            <div>
                <div style="font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em; color: #FFFFFF; line-height: 1.2;">
                    Docu<span style="color: #00E599;">Lens</span> <span style="font-size: 0.7rem; background: rgba(0, 229, 153, 0.16); color: #00E599; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(0, 229, 153, 0.35); vertical-align: middle; font-weight: 800;">AI</span>
                </div>
                <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 0.2rem; font-weight: 500;">
                    v{app_version} • Grounded Document Intelligence
                </div>
            </div>
        </div>
    </div>
    """

def render_hero_banner(active_mode: str, active_language: str, app_tagline: str) -> str:
    """Renders the top application hero banner with glowing aperture emblem and mode badge."""
    return f"""
    <div style="margin-bottom: 1.1rem;">
        <div style="display: flex; align-items: center; gap: 0.85rem;">
            <div style="flex-shrink: 0; line-height: 0;">
                {DOCULENS_LOGO_ICON_SVG}
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
                    <h1 style="margin: 0; font-size: 2.1rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">
                        {active_mode}
                    </h1>
                    <span class="badge-pill badge-source">{active_language}</span>
                </div>
                <p style="margin: 0.3rem 0 0 0; color: #94A3B8; font-size: 0.92rem;">
                    {app_tagline}
                </p>
            </div>
        </div>
    </div>
    """

def render_medical_avatar_banner():
    """Renders the static AI Report Assistant avatar banner compliant with PRD Section 4."""
    return f"""
    <div class="avatar-header">
        <div style="flex-shrink: 0;">
            {STATIC_AI_ASSISTANT_AVATAR_SVG}
        </div>
        <div style="flex-grow: 1;">
            <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.2rem;">
                <span style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">AI Report Assistant</span>
                <span class="avatar-badge-tag">AI Powered • Non-Diagnostic</span>
            </div>
            <p style="margin: 0; font-size: 0.82rem; color: #94A3B8; line-height: 1.4;">
                Objective laboratory observations and educational test explanations. Does not diagnose health conditions,
                prescribe therapy, or replace consultation with a qualified clinical physician.
            </p>
        </div>
    </div>
    """

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

