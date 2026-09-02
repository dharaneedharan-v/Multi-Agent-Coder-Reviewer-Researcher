
import logging
from dataclasses import dataclass
import re
from src.prompt.review_prompt import REVIEWER_SYSTEM_PROMPT
from src.utils.LLM.invoke import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)
_MCP_CONFIG = {
    "review": {
        "transport": "streamable_http",
        "url": "http://127.0.0.1:8002/mcp",
        
    }
}
def extract_code(text: str) -> str:
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

@dataclass
class ReviewResult:
    passed:   bool
    feedback: str   # full reviewer response shown to user
    issues:   str   # extracted issues passed to coder on FAIL


class Review :
    def __init__(self):
        self.llm = get_llm(max_tokens=2048, temperature=0.1)
        self.agent = None
            
    async def run_reviewer_agent(self ,question: str) -> ReviewResult:
        """
        Stateless reviewer agent. Receives code/question, returns ReviewResult.
        No checkpointer — memory is handled by the graph in service.py.
        """
        # llm = get_llm(max_tokens=1500, temperature=0.1)
        print("This is the Question Param ---------------------[Review Agent Input]" , question)

        try:
            client = MultiServerMCPClient(_MCP_CONFIG)

            async with client.session("review") as session:
                tools = await load_mcp_tools(session)
                print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")
                # tool = []
                # for t in tools :
                #     if t.name == "format_code":
                #         tool.append(t)
                # print("Tool Used....\n" , tool)
                self.agent = create_react_agent(
                    model=self.llm,
                    tools=tools,
                    prompt=SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
                )

                
                clean_code = extract_code(question)
                print("this is the clean code to MCP Server\n",clean_code)
                review_input = f"""{clean_code}"""
                logger.info("[Review Agent Invoking...........................]")
                response = await self.agent.ainvoke(
                    {"messages": [HumanMessage(content=review_input)]}
                )

                feedback: str = response["messages"][-1].content
                upper         = feedback.upper()
                
                passed = ("[PASS]" in upper or "STATUS: [PASS]" in upper) and "[FAIL]" not in upper

                issues = ""
                if not passed:
                    fail_idx = upper.find("FAIL")
                    issues   = feedback[fail_idx:].strip() if fail_idx != -1 else feedback
                    print("The Issue is---------------> ", issues)
                    print("The Feedback is---------------> ", feedback )


                logger.info(f"[ReviewerAgent] Verdict: {'PASS' if passed else 'FAIL'}")
                print("Given  reviewer agent..................",response["messages"][-2].content)
                print("Recived  reviewer agent..................",response["messages"][-1].content)
                # for msg in response["messages"]:
                #     print(msg)
                return ReviewResult (passed=passed, feedback=feedback, issues=issues)

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e
            logger.error(f"[ReviewerAgent] Error: {e}", exc_info=True)
            raise