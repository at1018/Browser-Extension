# Persona Engine

The Persona Engine classifies the most likely user persona from screenshot analysis results while preserving backward compatibility with existing endpoint behavior.

## Architecture

- `backend/app/persona/persona_engine.py` orchestrates persona context creation, hybrid classification, and final persona resolution.
- `backend/app/persona/persona_classifier.py` combines rule-based signals and LLM-assisted signals into a weighted persona score.
- `backend/app/persona/persona_rules.py` contains the expanded persona knowledge base, intent mapping, object patterns, and rule-score aggregation.
- `backend/app/persona/persona_registry.py` stores persona definitions, traits, and confidence floors.
- `backend/app/persona/persona_models.py` defines typed persona context, signals, and result schemas.

## Scoring flow

1. OCR, caption, labels, objects, intent, provider reasoning, and historical metadata are collected into `PersonaContext`.
2. `persona_rules.aggregate_rule_scores()` extracts and weights signals for each persona.
3. `persona_classifier._score_llm_signals()` scans provider reasoning for additional persona cues.
4. Rule scores and LLM scores are combined by configured weights.
5. A confidence score is computed from:
   - winning persona strength
   - second-best gap
   - overall signal evidence
6. `PersonaEngine` resolves the final persona only if confidence exceeds the production threshold.

## Weighting strategy

- Rule signals are weighted by source:
  - OCR text: `1.4`
  - caption text: `1.1`
  - labels: `0.9`
  - object patterns: `1.2`
  - provider reasoning: `1.0`
  - historical metadata: `0.7`
- Intent matches are strongly amplified through `PERSONA_INTENT_WEIGHT`.
- Final combination uses `PERSONA_RULE_WEIGHT` and `PERSONA_LLM_WEIGHT`.

## Confidence algorithm

The confidence score is normalized to `0.0-1.0` and is based on:

- dominance: how much the top persona score leads over the runner-up
- evidence: the strength of the winning persona score
- gap: how clearly separated the top persona is from the next-best option

This makes strong single-persona matches yield high confidence, while mixed or ambiguous screens produce lower confidence.

## Thresholds and fallback

- `PERSONA_MIN_CONFIDENCE` defines the production-grade threshold for the engine to override the incoming request persona.
- If the computed confidence is below threshold, the original `persona` request value is preserved.
- `unknown` is returned only when evidence is weak or ambiguous and no persona confidently dominates.

## Diagnostics

Detailed debug metadata is available in `results.persona_analysis.metadata`:

- `rule_scores`
- `llm_scores`
- `combined_scores`
- `confidence_components`
- `selected_persona`
- `top_personas`
- `top_signals`
- `threshold`
- `decision`

## Examples

- Strong developer screenshot: high confidence from `tsconfig`, `code editor`, `github`, and `coding` intent.
- Mixed developer/designer screenshot: moderate confidence with both role signals reflected in `top_personas`.
- Weak evidence: fallback to the incoming persona or `unknown` when no persona clearly dominates.

## Extension guidelines

To add new persona vocabulary or broaden coverage:

1. Update `PERSONA_KEYWORD_SCORES` with domain-specific terms.
2. Add object-level cues to `OBJECT_PATTERNS`.
3. Enhance `INTENT_KEYWORD_SCORES` for stronger intent-to-persona mappings.
4. Adjust `PERSONA_INTENT_WEIGHT`, `PERSONA_RULE_WEIGHT`, or `PERSONA_LLM_WEIGHT` in `backend/app/core/config.py`.
5. Add unit tests covering new real-world scenarios.
