"""Groq API client wrapper with resilience, schema repair, and rate-limit handling.
Complies with PRD requirements for configurable models, secure keys, and bounded repair.
"""
import os
import json
import time
from typing import Dict, Any, Optional, Tuple, List

from src.config import DEFAULT_GROQ_MODEL

def get_api_key(explicit_key: Optional[str] = None) -> Optional[str]:
    """
    Resolve Groq API key securely in order:
    1. Explicitly provided key (e.g. from user sidebar input)
    2. Streamlit secrets (`st.secrets["GROQ_API_KEY"]`)
    3. Environment variable (`os.environ["GROQ_API_KEY"]`)
    """
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()

    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets and st.secrets["GROQ_API_KEY"]:
            return str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass

    env_key = os.environ.get("GROQ_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    return None

def call_groq_json_analysis(
    prompt: str,
    model: str = DEFAULT_GROQ_MODEL,
    api_key: Optional[str] = None,
    max_tokens: int = 4096
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Execute structured analysis call to Groq with response_format={"type": "json_object"}.
    Includes single bounded repair attempt if JSON is malformed (PRD requirement).
    Returns (parsed_dict, None) or (None, error_message).
    """
    resolved_key = get_api_key(api_key)
    if not resolved_key:
        return None, (
            "Groq API Key is not configured. Please add GROQ_API_KEY to your "
            "'.streamlit/secrets.toml' file, set the GROQ_API_KEY environment variable, "
            "or enter it in the sidebar settings."
        )

    try:
        from groq import Groq, RateLimitError, APIError, APITimeoutError
    except ImportError:
        return None, "The 'groq' package is not installed. Please run: pip install -r requirements.txt"

    client = Groq(api_key=resolved_key)

    # Attempt primary JSON generation
    messages = [
        {"role": "system", "content": "You are a specialized document intelligence model. You MUST respond with valid JSON only."},
        {"role": "user", "content": prompt}
    ]

    raw_content = ""
    for attempt in range(2):  # Primary attempt (0) + 1 Repair attempt (1)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,  # Low temperature for factual precision & deterministic structure
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content or ""
            parsed = json.loads(raw_content)
            return parsed, None

        except json.JSONDecodeError as jde:
            if attempt == 0:
                # Bounded repair attempt (PRD requirement)
                messages.append({"role": "assistant", "content": raw_content})
                messages.append({
                    "role": "user",
                    "content": (
                        f"Your previous response caused a JSON parsing error: {str(jde)}. "
                        "Please reformat and return ONLY the corrected, strictly valid JSON object. "
                        "Do not include markdown codeblocks or extra text."
                    )
                })
                time.sleep(0.5)
                continue
            else:
                return None, f"Failed to parse structured JSON after 1 repair attempt: {str(jde)}"

        except RateLimitError as rle:
            return None, (
                "Groq API Rate Limit reached. Please wait a few seconds and click Retry. "
                f"Details: {str(rle)}"
            )

        except APITimeoutError:
            return None, "Groq API request timed out. Please check your network connection and click Retry."

        except APIError as apie:
            return None, f"Groq API Error: {str(apie)}"

        except Exception as e:
            return None, f"Unexpected error during analysis: {str(e)}"

    return None, "Analysis failed to produce valid structured output."

def call_groq_grounded_chat(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_GROQ_MODEL,
    api_key: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Execute grounded chat completion call to Groq.
    Returns (assistant_text, None) or (None, error_message).
    """
    resolved_key = get_api_key(api_key)
    if not resolved_key:
        return None, "Groq API Key is missing. Please configure it in sidebar settings or secrets."

    try:
        from groq import Groq, RateLimitError, APIError, APITimeoutError
    except ImportError:
        return None, "The 'groq' package is not installed."

    client = Groq(api_key=resolved_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=1500
        )
        answer = response.choices[0].message.content or ""
        return answer, None

    except RateLimitError as rle:
        return None, f"Rate limit reached on Groq API. Please wait a moment: {str(rle)}"
    except APITimeoutError:
        return None, "Chat request timed out. Please try asking again."
    except APIError as apie:
        return None, f"Groq API Error: {str(apie)}"
    except Exception as e:
        return None, f"Unexpected chat error: {str(e)}"

