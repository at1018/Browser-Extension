# Code Analysis Prompt

Return JSON:
{
  "intent": "code",
  "language": "python|js|java|...",
  "code_blocks": [ {"start":0, "end":0, "text":"..."} ],
  "suggested_actions": ["format_code","run_static_analysis"]
}

Instruction: Extract code blocks and provide metadata like language and line ranges.
