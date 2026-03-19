# =============================================================
# prompts.py — Prompt templates for each pipeline step
# =============================================================


def cleaning_prompt(raw_text: str) -> str:
    """
    Step 1: Clean and normalize raw business input.
    Returns a prompt string for the LLM.
    """
    return f"""You are an expert business analyst. Clean and normalize the following raw business input text.

RULES:
- Fix typos and grammatical errors
- Remove filler words, off-topic chatter, and redundancies
- Normalize formatting: consistent bullet points, remove extra whitespace
- Preserve ALL original information and intent — do not summarize or remove details
- Return ONLY the cleaned text, no explanations or preamble

RAW INPUT:
---
{raw_text}
---

CLEANED OUTPUT:"""


def extraction_prompt(cleaned_text: str) -> str:
    """
    Step 2: Extract structured summary and user stories from cleaned text.
    Returns a prompt string for the LLM.
    """
    return f"""You are a senior business analyst and product manager.
Extract structured requirements from the following cleaned business input.

Return a STRICTLY VALID JSON object with NO markdown fences, NO extra text.

Required JSON structure:
{{
  "summary": "3-5 sentence executive summary covering: core problem, proposed solution, scope, timeline, and budget",
  "userStories": [
    {{
      "as": "role (e.g. Sales Representative)",
      "iWant": "the feature or capability",
      "soThat": "the business value or outcome",
      "acceptanceCriteria": ["criterion 1", "criterion 2", "criterion 3"]
    }}
  ]
}}

RULES:
- Generate 4-6 distinct, actionable user stories covering major requirements
- Each user story must have 2-3 concrete acceptance criteria
- Summary must be business-focused and concise
- Output ONLY valid JSON, nothing else

CLEANED INPUT:
---
{cleaned_text}
---"""


def insight_prompt(cleaned_text: str, user_stories: list) -> str:
    """
    Step 3: Generate risks and KPIs from cleaned text and extracted user stories.
    Returns a prompt string for the LLM.
    """
    stories_context = "\n".join(
        f"- As a {s.get('as', '')}, I want {s.get('iWant', '')}"
        for s in user_stories
    )

    return f"""You are a risk management expert and business strategist.
Analyze the following business initiative and generate structured risks and KPIs.

Return a STRICTLY VALID JSON object with NO markdown fences, NO extra text.

Required JSON structure:
{{
  "risks": [
    {{
      "title": "short risk name",
      "level": "High|Medium|Low",
      "description": "clear description of the risk and its potential impact",
      "mitigation": "specific, actionable mitigation strategy"
    }}
  ],
  "kpis": [
    {{
      "name": "KPI name",
      "target": "quantitative target (e.g. 90% accuracy, <2 seconds, 50000 users)",
      "measurement": "how this will be measured and tracked"
    }}
  ]
}}

RULES:
- Generate 4-6 risks across High, Medium, and Low severity
- Generate 4-6 measurable KPIs tied directly to the project goals
- All KPIs must be quantitative and time-bound where possible
- Output ONLY valid JSON, nothing else

BUSINESS CONTEXT:
---
{cleaned_text}
---

USER STORIES IDENTIFIED:
{stories_context}"""
