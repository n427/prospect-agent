from agent import executor as research_agent
import anthropic, json
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()

def generate_emails(company_name: str, website: str, contact_name: str = "the founder", sender_name: str = "the team") -> dict:
    print(f'Researching {company_name}...')
    steps = []
    research = research_agent.invoke(
        {"input": f"Research {company_name} ({website}). Summarize what they do, their size, recent news, and key marketing challenges."},
        {"callbacks": []},
    )
    # Capture intermediate steps if available
    if "intermediate_steps" in research:
        for action, observation in research["intermediate_steps"]:
            steps.append({
                "tool": action.tool,
                "input": action.tool_input,
                "output": str(observation)[:800],
            })

    context = research["output"]
    prompt = f"""
    You are a senior outreach specialist at GR0, a top digital marketing agency.
    COMPANY RESEARCH:
    {context}
    Write 3 cold email variants to {contact_name} at {company_name}.
    Each email should be under 100 words, have a subject line, and be distinct:
    1. DIRECT: State the value proposition immediately
    2. CURIOSITY: Lead with an interesting observation about their business
    3. PAIN: Open with a specific challenge they likely face
    Sign each email from {sender_name} at GR0.
    Absolutely NO em-dashes
    Return ONLY a JSON object with keys: direct, curiosity, pain.
    Each key maps to: {{ "subject": str, "body": str }}
    """
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()
    raw = raw.replace("```json","").replace("```","").strip()
    emails = json.loads(raw)
    return {'research': context, 'emails': emails, 'steps': steps}

if __name__ == '__main__':
    result = generate_emails("Glossier", "https://glossier.com", "Emily Weiss")
    for variant, content in result['emails'].items():
        print(f'\n=== {variant.upper()} ===')
        print(f"Subject: {content['subject']}")
        print(content['body'])