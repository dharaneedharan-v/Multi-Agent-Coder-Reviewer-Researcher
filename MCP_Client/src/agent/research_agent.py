
import logging
import os

from src.prompt.research_prompt import RESEARCHER_SYSTEM_PROMPT
from src.tools.duck import duckduckgo_search
from src.utils.LLM.invoke import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

logger = logging.getLogger(__name__)

MCP_CONFIG = {
    "research": {
        "transport": "streamable_http",
        "url": "http://127.0.0.1:8000/mcp",
    }
}

class Research :
    def __init__(self):
        self.llm = get_llm(max_tokens=2048, temperature=0.2)
        self.agent = None
            
    async def run_researcher_agent(self ,question: str) -> str:
    
        # llm = get_llm(max_tokens=2000, temperature=0.3)

        try:
            client = MultiServerMCPClient(MCP_CONFIG)

            async with client.session("research") as session:
                tools = await load_mcp_tools(session)
                print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")
                logger.info(f"[Researcher Agent] Loaded {len(tools)}  tools")
                self.agent = create_react_agent(
                    model=self.llm,
                    tools=tools,
                    prompt =SystemMessage(content=RESEARCHER_SYSTEM_PROMPT),
                )
                logger.info("[Research Agent Invoking...........................]")
                response = await self.agent.ainvoke(
                    {"messages": [HumanMessage(content=question)]}
                )
                res = response["messages"][-2].content
                # print(res)

                result: str = response["messages"][-1].content
                print("==================================RESERACH CONTENT GIVEN TO LLM ==============================================================")
                # print(result)
                print(res)
                print("=================================== END =============================================================")
                print("========================================= RESPONSE FROM THE RESEARCH AGENT================================== ")
                print(result)
                print("=================================== END =============================================================")
                logger.info("[ResearcherAgent] Done.")
                return result

        except Exception as e:
            logger.error(f"[ResearcherAgent] Error: {e}", exc_info=True)
            raise
