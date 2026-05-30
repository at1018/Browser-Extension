# Question Analysis Prompt

Return JSON:
{
  "intent": "question_text",
  "question": "...",
  "context": "...",
  "suggested_actions": ["answer_question","search_docs"]
}

Instruction: If the screenshot contains a user question, extract it and provide context.
