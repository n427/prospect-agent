from agent import executor as research_agent
import anthropic, json
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()

def generate_emails(company_name: str, website: str, contact_name: str = "the founder", sender_name: str = "the team") -> dict:
    print(f'Researching {company_name}...')
    steps = []
    research = research_agent.invoke(
        {"input": f"Research {company_name} ({website}). Summarize what they do, their size, recent news, and key waste management or sustainability challenges they face."},
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
    You are a senior outreach specialist at Dyrt, a waste analytics company that helps large venues, stadiums, and commercial facilities cut waste costs, hit sustainability targets, and comply with recycling mandates using real-time data.
    COMPANY RESEARCH:
    {context}
    Write 3 cold email variants to {contact_name} at {company_name}.
    Each email should be under 100 words, have a subject line, and be distinct:
    1. DIRECT: State Dyrt's value proposition immediately in the context of their waste or sustainability operations
    2. CURIOSITY: Lead with an interesting observation about their facility's waste or sustainability footprint
    3. PAIN: Open with a specific waste management or compliance challenge they likely face
    Sign each email from {sender_name} at Dyrt.
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
    result = generate_emails("Intuit Dome", "https://intuitdome.com", "Gillian Zucker")
    for variant, content in result['emails'].items():
        print(f'\n=== {variant.upper()} ===')
        print(f"Subject: {content['subject']}")
        print(content['body'])