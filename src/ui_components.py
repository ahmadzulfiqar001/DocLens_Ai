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





def render_priority_badge(priority: str):
    """Renders a native Streamlit badge for review priority without any raw HTML leakage."""
    import streamlit as st
    p_clean = priority.strip().lower()
    if p_clean == "high":
        if hasattr(st, "badge"):
            st.badge("High Priority", icon="⚠️", color="red")
        else:
            st.error("⚠️ High Priority")
    elif p_clean == "medium":
        if hasattr(st, "badge"):
            st.badge("Medium Priority", icon="⚖️", color="orange")
        else:
            st.warning("⚖️ Medium Priority")
    elif p_clean == "low":
        if hasattr(st, "badge"):
            st.badge("Low Priority", icon="ℹ️", color="blue")
        else:
            st.info("ℹ️ Low Priority")
    elif "no flagged" in p_clean:
        if hasattr(st, "badge"):
            st.badge("No Flagged Issues", icon="✅", color="green")
        else:
            st.success("✅ No Flagged Issues")
    else:
        if hasattr(st, "badge"):
            st.badge(priority, icon="ℹ️", color="blue")
        else:
            st.info(priority)

def render_medical_comparison_badge(comparison: str, has_conflict: bool = False):
    """Renders a native Streamlit badge for medical range evaluations without any raw HTML leakage."""
    import streamlit as st
    comp_clean = comparison.strip().lower()
    if has_conflict:
        if hasattr(st, "badge"):
            st.badge(f"{comparison} (Conflict)", icon="⚡", color="red")
        else:
            st.error(f"⚡ {comparison} (Conflict)")
        return
    if "above" in comp_clean:
        if hasattr(st, "badge"):
            st.badge("Above range", icon="🔺", color="red")
        else:
            st.error("🔺 Above range")
    elif "below" in comp_clean:
        if hasattr(st, "badge"):
            st.badge("Below range", icon="🔻", color="orange")
        else:
            st.warning("🔻 Below range")
    elif "within" in comp_clean:
        if hasattr(st, "badge"):
            st.badge("Within range", icon="✅", color="green")
        else:
            st.success("✅ Within range")
    else:
        if hasattr(st, "badge"):
            st.badge("Cannot assess from range", icon="❓", color="gray")
        else:
            st.caption("❓ Cannot assess from range")


