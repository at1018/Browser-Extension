# Chart Analysis Prompt

Return JSON:
{
  "intent": "chart_graph",
  "chart_type": "bar|line|pie|...",
  "data_summary": [ {"label":"...","value":0} ],
  "suggested_actions": ["extract_data","plot_table"]
}

Instruction: Detect charts and summarize data points where possible.
