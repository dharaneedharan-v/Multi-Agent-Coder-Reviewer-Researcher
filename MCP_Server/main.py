
# import asyncio
# import sys

# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# from fastmcp import FastMCP
# from src.routes.routes import router

# mcp = FastMCP("my-server")
# mcp.mount(router)
# mcp.run(transport="streamable-http" , port = 8002) 



from fastmcp import FastMCP
router = FastMCP("router")
from src.tools.tools import * 
     

