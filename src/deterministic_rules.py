"""Deterministic calculation rules for DocuLens AI.
PRD requirement: Application code computes counts, numeric range comparisons,
contract review priority, and quiz scores deterministically.
"""
import re
from typing import Dict, Any, List, Tuple, Optional
from src.config import HIGH_PRIORITY_TOPICS, MEDIUM_PRIORITY_TOPICS, CONTRACT_CHECKLIST_TOPICS

# -----------------------------------------------------------------------
# Medical Range Comparison (PRD M02, M03)
# -----------------------------------------------------------------------
def parse_numeric(val_str: str) -> Optional[float]:
    """Extract a numeric float from a string, or None if not cleanly numeric."""
    if not val_str:
        return None
    val_clean = val_str.strip().replace(",", "")
    # Check for pure number (with optional decimal and sign)
    match = re.search(r"^[-+]?\d*\.?\d+", val_clean)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    return None

def compute_medical_range(
    raw_result: str,
    raw_interval: str,
    reported_flag: str = "None"
) -> Dict[str, Any]:
    """
    PRD M02 & M03:
    Compute Below range, Within range, or Above range only when numeric result
    and reference interval can be parsed unambiguously.
    Treat boundary values as within the interval.
    For qualitative, absent, or ambiguous ranges, return 'Cannot assess from the supplied range'.
    Detect conflict between reported lab flag and numeric calculation.
    """
    result_num = parse_numeric(raw_result)
    
    # If result is qualitative or cannot be parsed as numeric
    if result_num is None:
        return {
            "comparison": "Cannot assess from the supplied range",
            "reason": "Result is qualitative or non-numeric",
            "is_outside_range": False,
            "has_conflict": False,
            "verification_note": None
        }

    if not raw_interval or raw_interval.lower() in ["not stated", "not applicable", "n/a", "none", "pending validation"]:
        return {
            "comparison": "Cannot assess from the supplied range",
            "reason": "Reference interval is missing or qualitative",
            "is_outside_range": False,
            "has_conflict": False,
            "verification_note": None
        }

    interval_str = raw_interval.strip()
    
    # Pattern 1: Range "low - high" (e.g. "70 - 99", "3.5 - 5.0", "4.0 to 5.6")
    range_match = re.search(r"(\d*\.?\d+)\s*(?:-|–|—|to)\s*(\d*\.?\d+)", interval_str)
    if range_match:
        try:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
            
            # Boundary values are treated as within interval
            if result_num < low:
                comparison = "Below range"
                is_outside = True
            elif result_num > high:
                comparison = "Above range"
                is_outside = True
            else:
                comparison = "Within range"
                is_outside = False
                
            return _evaluate_flag_conflict(comparison, is_outside, reported_flag, interval_str, result_num)
        except ValueError:
            pass

    # Pattern 2: Upper bound only ("< 0.034" or "<= 100")
    upper_match = re.search(r"^[<≤]\s*(\d*\.?\d+)", interval_str)
    if upper_match:
        try:
            limit = float(upper_match.group(1))
            if result_num <= limit:
                comparison = "Within range"
                is_outside = False
            else:
                comparison = "Above range"
                is_outside = True
            return _evaluate_flag_conflict(comparison, is_outside, reported_flag, interval_str, result_num)
        except ValueError:
            pass

    # Pattern 3: Lower bound only ("> 50" or ">= 50")
    lower_match = re.search(r"^[>≥]\s*(\d*\.?\d+)", interval_str)
    if lower_match:
        try:
            limit = float(lower_match.group(1))
            if result_num >= limit:
                comparison = "Within range"
                is_outside = False
            else:
                comparison = "Below range"
                is_outside = True
            return _evaluate_flag_conflict(comparison, is_outside, reported_flag, interval_str, result_num)
        except ValueError:
            pass

    return {
        "comparison": "Cannot assess from the supplied range",
        "reason": "Interval format ambiguous or non-standard",
        "is_outside_range": False,
        "has_conflict": False,
        "verification_note": None
    }

def _evaluate_flag_conflict(
    comparison: str,
    is_outside: bool,
    reported_flag: str,
    interval_str: str,
    result_num: float
) -> Dict[str, Any]:
    """Check if laboratory flag contradicts deterministic range calculation."""
    flag_upper = (reported_flag or "").strip().upper()
    has_conflict = False
    verification_note = None

    if flag_upper in ["H", "HIGH", "ABNORMAL"] and comparison == "Within range":
        has_conflict = True
        verification_note = f"Disagreement noted: Laboratory reported '{reported_flag}', but value ({result_num}) falls within interval ({interval_str}). Verification requested."
    elif flag_upper in ["L", "LOW"] and comparison == "Within range":
        has_conflict = True
        verification_note = f"Disagreement noted: Laboratory reported '{reported_flag}', but value ({result_num}) falls within interval ({interval_str}). Verification requested."
    elif flag_upper in ["NORMAL", "NEGATIVE"] and comparison in ["Above range", "Below range"]:
        has_conflict = True
        verification_note = f"Disagreement noted: Laboratory reported '{reported_flag}', but calculated as '{comparison}'. Verification requested."

    return {
        "comparison": comparison,
        "reason": f"Evaluated against interval [{interval_str}]",
        "is_outside_range": is_outside,
        "has_conflict": has_conflict,
        "verification_note": verification_note
    }

# -----------------------------------------------------------------------
# Contract Priority & Derived Metrics (PRD D04, D05)
# -----------------------------------------------------------------------
def compute_contract_metrics(
    contract_findings: List[Dict[str, Any]],
    is_complete: bool = True
) -> Dict[str, Any]:
    """
    PRD D04 & D05:
    High: missing or unclear payment, termination, or dispute resolution.
    Medium: another missing or unclear checklist topic.
    Low: informational observations.
    Overall: High if any is High, else Medium if any is Medium, else Low.
    Show 'No flagged checklist issues' when checklist is clear.
    Show 'Review incomplete' if extraction or analysis is incomplete.
    """
    if not is_complete:
        return {
            "overall_priority": "Review incomplete",
            "priority_rule": "Extraction or analysis did not finish completely.",
            "unique_issues_count": 0,
            "missing_topics_count": 0,
            "actions_count": 0,
            "all_topics_clear": False
        }

    high_count = 0
    med_count = 0
    missing_count = 0
    flagged_issues_count = 0
    actions_count = 0

    for finding in contract_findings:
        topic = finding.get("checklist_topic", "")
        status = finding.get("status", "")
        action = finding.get("suggested_action")
        priority = finding.get("review_priority", "Low")
        
        is_missing = "not found" in status.lower()
        is_unclear = "unclear" in status.lower() or "vague" in status.lower()

        if is_missing:
            missing_count += 1
            flagged_issues_count += 1
        elif is_unclear:
            flagged_issues_count += 1

        if action and action.strip() and action.lower() != "none":
            actions_count += 1

        # Check priority level
        if priority.upper() == "HIGH":
            high_count += 1
        elif priority.upper() == "MEDIUM":
            med_count += 1

    if high_count > 0:
        overall_priority = "High"
        priority_rule = "High review attention required: Unclear or missing key clause(s) in Payment Terms, Termination, or Dispute Resolution."
    elif med_count > 0:
        overall_priority = "Medium"
        priority_rule = "Medium review attention required: Missing or unclear secondary clause(s) such as Obligations, Duration/Renewal, or Governing Law."
    elif flagged_issues_count > 0:
        overall_priority = "Low"
        priority_rule = "Low review attention: Informational observations or minor wording clarifications only."
    else:
        overall_priority = "No flagged checklist issues"
        priority_rule = "All standard checklist topics are explicitly stated with clear terms."

    return {
        "overall_priority": overall_priority,
        "priority_rule": priority_rule,
        "unique_issues_count": flagged_issues_count,
        "missing_topics_count": missing_count,
        "actions_count": actions_count,
        "all_topics_clear": (flagged_issues_count == 0)
    }

# -----------------------------------------------------------------------
# Quiz Scoring (PRD S05)
# -----------------------------------------------------------------------
def calculate_quiz_score(
    quiz_questions: List[Dict[str, Any]],
    user_answers: Dict[int, int]
) -> Dict[str, Any]:
    """
    PRD S05:
    Calculate score from actual question count.
    Show correct and incorrect choices, explanations, and percentage.
    """
    total = len(quiz_questions)
    if total == 0:
        return {"score": 0, "total": 0, "percentage": 0.0, "details": []}

    correct_count = 0
    details = []

    for idx, q in enumerate(quiz_questions):
        q_id = q.get("question_id", idx + 1)
        correct_idx = q.get("correct_index", 0)
        user_choice = user_answers.get(q_id, None)
        is_correct = (user_choice == correct_idx)

        if is_correct:
            correct_count += 1

        details.append({
            "question_id": q_id,
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "user_choice": user_choice,
            "correct_choice": correct_idx,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
            "source_id": q.get("source_id", ""),
            "source_passage": q.get("source_passage", "")
        })

    percentage = round((correct_count / total) * 100, 1)
    
    return {
        "score": correct_count,
        "total": total,
        "percentage": percentage,
        "passed": percentage >= 60.0,
        "details": details
    }

