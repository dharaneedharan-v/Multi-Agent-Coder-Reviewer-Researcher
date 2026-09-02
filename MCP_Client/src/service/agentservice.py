
import logging
import traceback
from src.repositories.repository import CoffeeRepository
from src.agent.coder_agent import Coder
from src.agent.research_agent import Research
from src.agent.review_agent import Review
from src.prompt.router_prompt import Intent
from src.service.graph import Graph
from src.utils.logger.log import log_error
from src.utils.LLM.invoke import get_db_uri
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

load_dotenv()
logger  = logging.getLogger(__name__)
DB_URI  = get_db_uri()


class AgentService:

    def __init__(self, repo: CoffeeRepository ):
        self.repo = repo
        self.coder_agent = Coder()
        self.review_agent = Review()
        self.search_agent = Research() 

        self.graph_var = Graph(
            coder=self.coder_agent, 
            review=self.review_agent, 
            search=self.search_agent
        )
        

    async def chat(self, message: str, customer_id: str) -> str:
        logger.info(f"[AgentService] customer={customer_id} | message={message}")
        print(f"Customer question: {message}")

        try:
            customer = self.repo.get_customer_by_id(customer_id)

            if not customer:
                logger.error("Customer ID not found")
                raise Exception("Customer not found")
            
            async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
                await checkpointer.setup()
                graph = self.graph_var.build_graph(checkpointer= checkpointer)

                checkpoint = await checkpointer.aget(
                    {"configurable": {"thread_id": str(customer_id)}} 
                )
                
                is_first_turn = checkpoint is None
                logger.info(f"[AgentService] is_first_turn={is_first_turn}")
                    
                initial_state = {
                    "messages":          [HumanMessage(content=message)],
                    "is_first_turn":     is_first_turn,
                    "intent":            None,
                    "research_context":  None,
                    "review_feedback":   None,
                    "review_passed":     None,
                    "review_issues":     None,
                    "final_response":    None,
                }

                result = await graph.ainvoke(
                    initial_state,
                    config={
                        "configurable": {"thread_id": str(customer_id)}
                    },
                )

                final_response = result.get("final_response")
                if   result.get("intent") == Intent.IRRELAVENT:
                    final_response ="I'm sorry, that request is outside my technical scope. Kindle Ask Questions that Related to the Techinal Question related to the Coding and Research and Code Review.....!!!!!\n I am Trained to Provide Content related to the Code , research , review of a code alone. \n As of My knowledge is Narrow Down to provide the Techinal Questions to Answers Alone.. !!!!!!!!!"
                if not final_response:
                    final_response = result["messages"][-1].content

            logger.info(f"[AgentService] Response: {final_response[:120]}...")
            print(f"Agent Response: {final_response}")
            return final_response

        except Exception as e:
            print("AgentService Error:", e)
            traceback.print_exc()
            log_error(self.repo, message=traceback.format_exc())
            raise
# graph = build_graph() 
# graph = build_graph()  for the Lagraph dev -----------