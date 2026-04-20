from langchain_anthropic import ChatAnthropic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from dotenv import load_dotenv
from summarizer import summarize_prospect 

import json
load_dotenv()

@tool
def research_company_website(url: str) -> str:
    """Fetch and summarize a company's website into structured JSON."""
    result = summarize_prospect(url)
    return json.dumps(result)

search_tool = TavilySearchResults(max_results=3)
tools = [search_tool, research_company_website]

llm = ChatAnthropic(model="claude-opus-4-5", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a B2B sales researcher for GR0, a digital marketing agency.
    Given a company name and website, use your tools to research them thoroughly.
    Find: what they do, their size, recent news, and why they might need digital marketing.
    Be concise and factual. Only use sources from 2026 and 2025."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

if __name__ == '__main__':
    result = executor.invoke({
    "input": "Research this company: Notion (https://notion.so). What do they do and why might they need better SEO?"
    })
    print("\n--- FINAL ANSWER ---")
    print(result["output"])