


import json
import logging
from src.prompt.router_prompt import ROUTER_SYSTEM_PROMPT, Intent
from src.models.models import GraphState
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from src.utils.LLM.invoke import get_llm
from src.agent.coder_agent import Coder
from src.agent.research_agent import Research
from src.agent.review_agent import Review
logger = logging.getLogger(__name__)

MAX_REVIEW_RETRIES = 3

#  Nodes 

class Graph:

    def __init__(self, coder: Coder, review: Review, search: Research):
        self.code = coder
        self.review = review
        self.search = search

    async def router_node(self,state: GraphState) -> GraphState:
        llm      = get_llm(max_tokens=50, temperature=0.0)
        user_msg = state["messages"][-1].content
        
        response = await llm.ainvoke([
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=user_msg),
        ])

        raw = response.content.strip()
        logger.info(f"[ Router ] Raw LLM response ---------------> : {raw}")

        try:
            intent = json.loads(raw).get("intent", Intent.CODE)
            print("This is from the GRaphs Intent .............................................", intent)
            
        except json.JSONDecodeError:
            lower = raw.lower()
            if "review"in lower: 
                intent = Intent.REVIEW
            elif "research_and_code" in lower: 
                intent = Intent.RESEARCH_AND_CODE
            elif "research" in lower: 
                intent = Intent.RESEARCH
            elif "irrelavent" in lower:
                intent = Intent.IRRELAVENT
            else:
                intent = Intent.CODE

        logger.info(f"[Router] Intent -> {intent}")
        return {**state, "intent": intent, "retry_count": 0 }



    async def coder_node(self ,state: GraphState) -> GraphState:
        user_msg = state["messages"][-1].content
        research = state.get("research_context")
        issues   = state.get("review_issues")

        #   Decide mode
        if issues:
            coding_input = f"""
                            FIX THE CODE BASED ON REVIEW.
                            USER REQUEST:
                            {user_msg}
                            ISSUES:
                            {issues}
                            RESEARCH CONTEXT:
                            {research}
                            """
        else:
            coding_input = f"""
                            WRITE CODE FOR:
                            {user_msg}
                            RESEARCH CONTEXT:
                            {research}
                            """

        result = await self.code.run_coder_agent(
            question=coding_input,
            research_context=research,
            review_issues=issues,
        )

        return {
            **state,
            "final_response": result,
            "retry_count": state.get("retry_count", 0) + 1,
        }


    async def reviewer_node(self , state: GraphState) -> GraphState:
        user_msg = state["messages"][-1].content
        generated_code = state.get("final_response")

        #   Decide input source (user vs coder)
        if generated_code:
            review_input = f"""
                            You are reviewing GENERATED CODE.
                           
                            CODE:
                            {generated_code}
                            """
        else:
            review_input = f"""
                            You are reviewing USER PROVIDED CODE.
                            {user_msg}
                            """

        #   Call reviewer agent (already returns structured result)
        result = await self.review.run_reviewer_agent(review_input)

        retry_count = state.get("retry_count", 0)

        logger.info(
            f"[ReviewerNode] Verdict={'PASS' if result.passed else 'FAIL'} | "
            f"retry_count={retry_count}/{MAX_REVIEW_RETRIES}"
        )

        #   Final response handling
        if result.passed:
            final_response = state.get("final_response")

        elif retry_count >= MAX_REVIEW_RETRIES:
            logger.warning(
                f"[ReviewerNode] Max retries ({MAX_REVIEW_RETRIES}) reached — returning best effort."
            )
            final_response = (
                f"Max retries ({MAX_REVIEW_RETRIES}) reached.\n\n"
                f"Last generated code:\n\n{generated_code}\n\n"
                f"Remaining issues:\n{result.issues}"
            )
        else:
            final_response = None  # continue loop

        return {
            **state,
            "review_feedback": result.feedback,
            "review_passed": result.passed,
            "review_issues": result.issues,   #   directly use agent output
            "final_response": final_response,
        }


    async def researcher_node(self ,state: GraphState) -> GraphState:
        import re

        user_msg = state["messages"][-1].content
        review_issues = state.get("review_issues")

        #   Decide input source
        if review_issues:
            research_input = f"""
                                    You are fixing FAILED CODE.
                                    USER REQUEST:
                                    {user_msg}
                                    ISSUES FROM REVIEWER:
                                    {review_issues}
                                    Provide technical research to fix these issues.
                                """
        else:
            research_input = f"""
                                USER REQUEST:
                                {user_msg}
                                """

        result = await self.search.run_researcher_agent(research_input)

        result = re.sub(r"<thinking>.*?</thinking>\s*", "", result, flags=re.DOTALL).strip()

        return {
            **state,
            "research_context": result,
            "final_response": result if state["intent"] == Intent.RESEARCH else state.get("final_response"),
        }


    #  Routing functions 

    def route_after_router(self ,state: GraphState) -> str:
        intent = state.get("intent", Intent.CODE)
        if intent == Intent.REVIEW:
            return "reviewer"
        if intent in (Intent.RESEARCH, Intent.RESEARCH_AND_CODE):
            return "researcher"
        if intent == Intent.CODE :
            return "coder"
        if intent == Intent.IRRELAVENT :
            return END 
        return END    # Intent.CODE -> coder only, no review



    def route_after_researcher(self ,state: GraphState) -> str:
        intent = state.get("intent")
        
        # Pure research → done
        if intent == Intent.RESEARCH:
            return END
        
        # RESEARCH_AND_CODE or REVIEW retry loop → go to coder
        return "coder"  #  covers both RESEARCH_AND_CODE and REVIEW retries


    def route_after_coder( self , state: GraphState) -> str:
        """
        After coder runs:
        - If intent is CODE -> END (user asked for code, no review needed)
        - If intent is REVIEW or RESEARCH_AND_CODE -> reviewer
        """
    
        return "reviewer"    # REVIEW and RESEARCH_AND_CODE both go through reviewer


    def route_after_reviewer(self ,state: GraphState) -> str:
        
        if state.get("review_passed"):
            return END

        retry_count = state.get("retry_count", 0)
        if retry_count >= MAX_REVIEW_RETRIES:
            logger.warning(
                f"[ReviewerNode] Max retries ({MAX_REVIEW_RETRIES}) reached — returning best effort."
            )
            return END

        logger.info(f"[ReviewerNode] Retry {retry_count}/{MAX_REVIEW_RETRIES} — sending back to research.")
        return "researcher"


    # Build graph 

    def build_graph(self ,checkpointer = None ):
        g = StateGraph(GraphState)

        g.add_node("router",     self.router_node)
        g.add_node("researcher", self.researcher_node)
        g.add_node("coder",      self.coder_node)
        g.add_node("reviewer",   self.reviewer_node)

        g.set_entry_point("router")

        # router -> researcher / reviewer / coder 
        g.add_conditional_edges(
            "router", self.route_after_router,
            {"reviewer": "reviewer", "researcher": "researcher", "coder": "coder" , END : END },
        )

        # researcher -> coder (research_and_code) or END (research only)
        g.add_conditional_edges(
            "researcher", self.route_after_researcher,
            {"coder": "coder", END: END},
        )

        # coder -> reviewer (review / research_and_code) or END (code only)
        g.add_conditional_edges(
            "coder", self.route_after_coder,
            {"reviewer": "reviewer", END: END},
        )

        # reviewer -> coder (retry on FAIL) or END (PASS or max retries)
        g.add_conditional_edges(
            "reviewer", self.route_after_reviewer,
            {"coder": "coder", "researcher":"researcher" , END: END},
        )

        return g.compile(checkpointer= checkpointer)

    # graph = build_graph()
