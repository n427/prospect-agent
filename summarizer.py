import anthropic, httpx, json
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()

def fetch_page_text(url: str) -> str:
    try:
        r = httpx.get(url, timeout=10, follow_redirects=True)
        import re
        return re.sub(r"<[^>]+>", " ", r.text)[:4000]
    except Exception as e:
        return f"Could not fetch page: {e}"
    
def summarize_prospect(url: str) -> dict:
    page_text = fetch_page_text(url)

    prompt = f"""
    You are a B2B sales researcher. Analyze this company webpage and return
    ONLY a JSON object with these exact keys:
    - company_name
    - industry
    - company_size (e.g. "10-50 employees")
    - what_they_do (1 sentence)
    - pain_points (list of 3 strings)
    - outreach_angle (why a digital marketing agency should reach out)
    Webpage content:
    {page_text}
    """

    message = client.messages.create(
        model = "claude-opus-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

if __name__ == '__main__':
    result = summarize_prospect("https://stripe.com")
    print(json.dumps(result, indent=2))