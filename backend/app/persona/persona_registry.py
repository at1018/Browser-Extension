from typing import Dict, Iterable, Optional

from app.persona.persona_models import PersonaDefinition

_PERSONA_DEFINITIONS: Dict[str, PersonaDefinition] = {
    'developer': PersonaDefinition(
        name='developer',
        description='Writes and debugs code, evaluates technical output, and expects implementation guidance.',
        traits=['technical', 'detail-oriented', 'debug-focused'],
        common_tools=['code editor', 'terminal', 'issue tracker'],
        confidence_floor=0.55,
    ),
    'designer': PersonaDefinition(
        name='designer',
        description='Focuses on visual layout, UX patterns, user flows, and interface clarity.',
        traits=['visual', 'user-centric', 'prototype-minded'],
        common_tools=['design tool', 'mockups', 'style guide'],
        confidence_floor=0.55,
    ),
    'qa': PersonaDefinition(
        name='qa',
        description='Looks for bugs, reproducibility, test cases, and product validation details.',
        traits=['quality-focused', 'methodical', 'risk-aware'],
        common_tools=['test plan', 'bug tracker', 'checklist'],
        confidence_floor=0.55,
    ),
    'analyst': PersonaDefinition(
        name='analyst',
        description='Analyzes data, metrics, and feature tradeoffs to make product or business decisions.',
        traits=['insight-driven', 'data-oriented', 'strategic'],
        common_tools=['dashboard', 'spreadsheet', 'report'],
        confidence_floor=0.55,
    ),
    'student': PersonaDefinition(
        name='student',
        description='Learns concepts, asks clarifying questions, and seeks simple examples and explanations.',
        traits=['curious', 'learning-focused', 'step-by-step'],
        common_tools=['tutorials', 'examples', 'notes'],
        confidence_floor=0.55,
    ),
    'shopper': PersonaDefinition(
        name='shopper',
        description='Compares products, pricing, and features with a goal of buying or researching a purchase.',
        traits=['comparison-oriented', 'value-focused', 'decision-driven'],
        common_tools=['product listing', 'reviews', 'pricing table'],
        confidence_floor=0.55,
    ),
    'unknown': PersonaDefinition(
        name='unknown',
        description='Unable to classify a persona with sufficient confidence.',
        traits=[],
        common_tools=[],
        confidence_floor=0.0,
    ),
}


def get_persona_definition(persona_name: str) -> PersonaDefinition:
    return _PERSONA_DEFINITIONS.get(persona_name.lower(), _PERSONA_DEFINITIONS['unknown'])


def list_persona_definitions() -> Iterable[PersonaDefinition]:
    return _PERSONA_DEFINITIONS.values()


def supported_personas() -> Dict[str, PersonaDefinition]:
    return _PERSONA_DEFINITIONS
