"""Lightweight intent detection for screenshot analysis.

This module implements a simple, deterministic heuristic-based intent
classifier that inspects OCR/extracted text and suggests a high-level
intent plus recommended next actions. It's intentionally small and
deterministic so it can be used before we wire an LLM-based router.
"""

from typing import Dict, List


def _extract_text(content: Dict) -> str:
    if not content:
        return ""
    if isinstance(content.get("ocr"), dict):
        return content["ocr"].get("text", "") or ""
    return content.get("text", "") or ""


def detect_intent(content: Dict) -> Dict:
    """Analyze extracted screenshot content and return intent metadata.

    Returns a dictionary with keys: `intent`, `confidence`, `reasoning`,
    and `suggested_actions`.
    """
    text = _extract_text(content).strip()
    low = text.lower()

    intents: List[tuple] = [
        ("bug_report", ["error", "stack", "exception", "traceback", "failed"]),
        ("code_snippet", ["def ", "class ", "import ", "console.log", "printf("]),
        ("invoice_or_receipt", ["invoice", "total", "amount", "receipt", "balance"]),
        ("product_lookup", ["price", "buy", "add to cart", "$", "€"]),
        ("authentication", ["password", "login", "sign in", "2fa", "otp"]),
        ("form_fill", ["name", "address", "email", "phone", "submit"]),
        ("contact_info", ["@", "mailto:", "tel:", "phone:"]),
    ]

    matched: List[str] = []
    for intent, keywords in intents:
        for kw in keywords:
            if kw in low:
                matched.append((intent, kw))
                break

    if matched:
        # Choose the first matched intent (priority by list order)
        chosen_intent = matched[0][0]
        reasons = [m[1] for m in matched]
        confidence = min(0.95, 0.5 + 0.15 * len(matched))
        suggested = {
            "bug_report": ["extract_error_block", "create_issue", "summarize_traceback"],
            "code_snippet": ["format_code", "run_static_analysis", "create_gist"],
            "invoice_or_receipt": ["extract_amounts", "parse_invoice", "save_record"],
            "product_lookup": ["search_products", "extract_prices", "open_shopping_flow"],
            "authentication": ["mask_sensitive_data", "warn_user", "offer_password_manager"],
            "form_fill": ["auto_fill_form", "extract_fields", "generate_payload"],
            "contact_info": ["save_contact", "open_mail_client"],
        }.get(chosen_intent, [])

        return {
            "intent": chosen_intent,
            "confidence": float(confidence),
            "reasoning": f"Matched keywords: {', '.join(reasons)}",
            "suggested_actions": suggested,
        }

    # Fallback: if there is a lot of text, assume text_extraction; else unknown.
    if len(low) > 80:
        return {
            "intent": "text_extraction",
            "confidence": 0.6,
            "reasoning": "Long text detected; likely document or block of text.",
            "suggested_actions": ["summarize_text", "extract_entities"],
        }

    return {
        "intent": "unknown",
        "confidence": 0.35,
        "reasoning": "No strong heuristic matches",
        "suggested_actions": [],
    }
