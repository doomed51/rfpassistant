"""Prompt templates for RFP analysis."""


def get_rfp_analysis_prompt() -> str:
    """
    Get the main RFP analysis prompt for Claude.
    
    Returns:
        Formatted prompt string requesting structured JSON output
    """
    return """You are an expert RFP analyst helping consulting teams quickly understand and respond to Requests for Proposals.

Analyze this RFP document thoroughly and extract the following information:

1. **Client Problems** (3-7 items): Identify the core issues, challenges, or pain points the client is trying to resolve. Look for business problems, operational challenges, strategic goals, or gaps they're trying to fill.

2. **Specific Requirements** (comprehensive list): Extract ALL must-have requirements, deliverables, technical specifications, compliance needs, and constraints. Include:
   - Technical requirements
   - Functional requirements
   - Deliverables and milestones
   - Team qualifications
   - Compliance/regulatory requirements
   - Budget constraints
   - Format requirements

3. **Gotchas & Ambiguities** (critical items): Identify red flags, unclear specifications, contradictory requirements, unrealistic expectations, missing information, or items that need clarification before proposal submission.

4. **Timeline** (all dates): Extract every important date mentioned:
   - Q&A deadline
   - Proposal submission deadline
   - Project start date
   - Project end date
   - Milestones
   - Other relevant dates

5. **Next Steps** (3-5 action items): Recommend specific, actionable steps for the proposal team to take immediately. Be concrete and tactical.

6. **Alignment Questions** (3-5 strategic questions): Generate the most important strategic questions the team should discuss and answer before drafting the proposal. These should help clarify positioning, approach, team composition, and win strategy.

Return your analysis in STRICT JSON format with this exact structure:

{
  "client_problems": [
    "Problem statement 1",
    "Problem statement 2"
  ],
  "requirements": [
    "Requirement 1",
    "Requirement 2"
  ],
  "gotchas": [
    "Gotcha/ambiguity 1",
    "Gotcha/ambiguity 2"
  ],
  "timeline": [
    {
      "event": "Q&A Deadline",
      "date": "YYYY-MM-DD"
    },
    {
      "event": "Proposal Submission",
      "date": "YYYY-MM-DD"
    }
  ],
  "next_steps": [
    "Action item 1",
    "Action item 2"
  ],
  "alignment_questions": [
    "Strategic question 1?",
    "Strategic question 2?"
  ]
}

IMPORTANT: 
- Return ONLY the JSON object, no other text
- Use double quotes for JSON strings
- Ensure all dates are in YYYY-MM-DD format
- If a section has no clear information, include an empty array []
- Be thorough and specific in your analysis"""


def get_followup_prompt(analysis: dict, question: str) -> str:
    """
    Generate a follow-up prompt for additional analysis.
    
    Args:
        analysis: The original RFP analysis dictionary
        question: User's follow-up question
    
    Returns:
        Formatted follow-up prompt with context
    """
    return f"""Based on this RFP analysis:

{analysis}

Please answer this question: {question}

Provide a clear, concise answer focused on actionable insights for the proposal team."""
