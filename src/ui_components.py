"""Reusable UI components, custom styling, static AI avatar, and layout helpers for DocuLens AI.
Delivers a premium, modern dashboard aesthetics with glassmorphic cards, glowing accents,
accessible typography, and seamless RTL support.
"""
from typing import Optional, List, Dict, Any

# Custom CSS for Streamlit
CUSTOM_CSS = """
<style>
/* Modern typography import */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Noto+Nastaliq+Urdu:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Background atmospheric lighting */
.stApp {
    background-color: #0B0F19;
    background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.09) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(14, 165, 233, 0.08) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(168, 85, 247, 0.05) 0px, transparent 50%);
    background-attachment: fixed;
    color: #F1F5F9;
}

/* Glassmorphic Container Cards */
.dl-card {
    background: rgba(22, 31, 48, 0.7);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.dl-card:hover {
    border-color: rgba(99, 102, 241, 0.3);
    box-shadow: 0 14px 30px -4px rgba(99, 102, 241, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
}

.dl-card-glow-indigo {
    border-left: 4px solid #6366F1;
}

.dl-card-glow-emerald {
    border-left: 4px solid #10B981;
}

.dl-card-glow-amber {
    border-left: 4px solid #F59E0B;
}

.dl-card-glow-rose {
    border-left: 4px solid #F43F5E;
}

/* Metric Stats Cards */
.stat-box {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 1.1rem 1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.stat-value {
    font-size: 1.9rem;
    font-weight: 800;
    line-height: 1.2;
    margin: 0.25rem 0;
    background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 100%);
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

/* Pill Badges */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.badge-high {
    background: rgba(239, 68, 68, 0.15);
    color: #FCA5A5;
    border: 1px solid rgba(239, 68, 68, 0.35);
}

.badge-med {
    background: rgba(245, 158, 11, 0.15);
    color: #FCD34D;
    border: 1px solid rgba(245, 158, 11, 0.35);
}

.badge-low {
    background: rgba(14, 165, 233, 0.15);
    color: #7DD3FC;
    border: 1px solid rgba(14, 165, 233, 0.35);
}

.badge-clear {
    background: rgba(16, 185, 129, 0.15);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.35);
}

.badge-source {
    background: rgba(99, 102, 241, 0.15);
    color: #A5B4FC;
    border: 1px solid rgba(99, 102, 241, 0.3);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
}

/* Source quotation callout */
.quote-callout {
    background: rgba(15, 23, 42, 0.75);
    border-left: 3px solid #6366F1;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    margin: 0.75rem 0;
    font-style: italic;
    color: #E2E8F0;
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
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.12) 0%, rgba(14, 165, 233, 0.08) 100%);
    border: 1px solid rgba(20, 184, 166, 0.25);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
}

.avatar-badge-tag {
    background: rgba(20, 184, 166, 0.2);
    border: 1px solid rgba(20, 184, 166, 0.4);
    color: #5EEAD4;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    letter-spacing: 0.05em;
}

/* Button overrides for sleek neon accent */
div.stButton > button {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
    color: #FFFFFF;
    font-weight: 600;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.4);
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%);
    box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.6);
    transform: translateY(-1px);
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(15, 23, 42, 0.6);
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    border-radius: 8px;
    color: #94A3B8;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background-color: #6366F1 !important;
    color: #FFFFFF !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #0E1322;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
"""

# Static Avatar SVG (AI Medical / Report Assistant)
STATIC_AI_ASSISTANT_AVATAR_SVG = """
<svg width="68" height="68" viewBox="0 0 68 68" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="34" cy="34" r="32" fill="url(#avatar_grad)" stroke="#14B8A6" stroke-width="2.5" stroke-dasharray="2 0"/>
  <circle cx="34" cy="34" r="28" fill="#0B132B"/>
  <!-- Stethoscope / Medical Cross Motif -->
  <path d="M34 18V36M34 36C34 41 38 45 43 45C48 45 52 41 52 36V28" stroke="#2DD4BF" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M34 36C34 41 30 45 25 45C20 45 16 41 16 36V28" stroke="#2DD4BF" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Cross Center -->
  <rect x="30" y="24" width="8" height="8" rx="2" fill="#14B8A6"/>
  <path d="M34 22V34M28 28H40" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Ear pieces -->
  <circle cx="16" cy="26" r="3" fill="#38BDF8"/>
  <circle cx="52" cy="26" r="3" fill="#38BDF8"/>
  <defs>
    <linearGradient id="avatar_grad" x1="0" y1="0" x2="68" y2="68" gradientUnits="userSpaceOnUse">
      <stop stop-color="#0EA5E9"/>
      <stop offset="0.5" stop-color="#14B8A6"/>
      <stop offset="1" stop-color="#6366F1"/>
    </linearGradient>
  </defs>
</svg>
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

