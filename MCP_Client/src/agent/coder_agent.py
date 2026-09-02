import logging
import os
from typing import Optional

from src.prompt.code_prompt import CODER_SYSTEM_PROMPT
from src.utils.LLM.invoke import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)

CONTEXT7_MCP_CONFIG = {
    "context7": {
        "transport": "streamable_http",
        "url": "https://mcp.context7.com/mcp",
        "headers": {
            "CONTEXT7_API_KEY": os.getenv("CONTEXT7_API_KEY", ""),
        },
    }
}

class Coder :
    def __init__(self):
        self.llm = get_llm(max_tokens=2048, temperature=0.2)
        self.agent = None
        
    async def run_coder_agent(
            self,
        question: str,
        research_context: Optional[str] = None,
        review_issues: Optional[str] = None,
    ) -> str:

        # llm = get_llm(max_tokens=2048, temperature=0.2)

        # Build enriched prompt
        print("this is input paramas -> Question , Research , review :" , question , review_issues  , research_context)
        
        parts = [question]
        if research_context:
            parts.append(
                f"\n\n### Research Context (use this to guide your implementation)\n"
                f"{research_context}"
            )
        if review_issues:
            parts.append(
                f"\n\n### Review Issues to Fix\n"
                f"The previous code failed review. Fix these issues:\n"
                f"{review_issues}"
            )
        enriched_question = "\n".join(parts)

        try:
            # client = MultiServerMCPClient(CONTEXT7_MCP_CONFIG)

            # async with client.session("context7") as session:
            #     tools = await load_mcp_tools(session)
            #     print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")
            #     # logger.info(f"[CoderAgent] Loaded {len(tools)} Context7 tools")

            self.agent = create_react_agent(
                model=self.llm,
                tools=[],
                prompt=SystemMessage(content=CODER_SYSTEM_PROMPT),
                # checkpointer=checkpointer
            )

            logger.info("[CoderAgent Invoking...........................]")
            response = await self.agent.ainvoke(
                {"messages": [HumanMessage(content=enriched_question)]}
            )

            result = response["messages"][-1].content
            # logger.info("[CoderAgent]----> Done")
            print("[CoderAgent]------------> ", result)
            return result

        except Exception as e:
            logger.error(f"[CoderAgent] Error: {e}", exc_info=True)
            raise
 