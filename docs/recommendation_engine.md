# Recommendation Engine

This module maps OCR, vision analysis, intent, and persona signals into actionable recommendations, root cause analysis, and severity assessments.

Components:
- `app/recommendation/recommendation_engine.py` — orchestrates detection, root cause inference, severity scoring, and recommendation generation.
- `app/recommendation/recommendation_rules.py` — rule-based issue detection vocabulary.
- `app/recommendation/root_cause_engine.py` — heuristic root cause inference.
- `app/recommendation/severity_engine.py` — severity heuristics.
- `app/recommendation/recommendation_registry.py` — plugin registry for custom handlers.
- `app/recommendation/recommendation_models.py` — Pydantic models for context and results.

Scoring Strategy:
- Rule matches produce a rule strength score.
- Root cause engine returns a confidence estimate.
- Combined confidence = 0.6 * normalized_rule_strength + 0.4 * root_confidence.

Severity model:
- `critical`, `high`, `medium`, `low`, `informational` based on issue type and production indicators.

Extension:
- Register new issue handlers via `register_handler(issue_type, handler)`.
