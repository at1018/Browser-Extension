# Persona Engine

The Persona Engine classifies the most likely user persona from screenshot analysis results while preserving backward compatibility with existing endpoint behavior.

## Architecture

- `backend/app/persona/persona_engine.py` orchestrates persona classification.
- `backend/app/persona/persona_classifier.py` combines rule-based and LLM-assisted signals.
- `backend/app/persona/persona_rules.py` extracts keyword/object/intention signals from OCR, provider output, and metadata.
- `backend/app/persona/persona_registry.py` stores persona definitions, traits, and confidence floors.
- `backend/app/persona/persona_models.py` defines the typed persona context and result schemas.

## Pipeline Integration

The analysis flow now includes a Persona Engine phase after OCR, provider analysis, and intent classification.

Output includes:

- `persona` — selected persona after hybrid classification and confidence-based fallback
- `results.persona_analysis` — detailed classification output, including signals, confidence, and reasoning

## Configuration

New settings available in `backend/app/core/config.py`:

- `PERSONA_MIN_CONFIDENCE` — minimum confidence for engine output to override request persona
- `PERSONA_RULE_WEIGHT` — relative weight of rule-based signals
- `PERSONA_LLM_WEIGHT` — relative weight of LLM-assisted persona signals

## Backward Compatibility

If the engine cannot classify a persona with sufficient confidence, the request-provided persona is preserved in the API response.
