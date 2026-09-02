
import tempfile
import subprocess
import traceback
import logging

from langchain_core.tools import tool
from src.routes.routes import router
from src.repositories.repository import CoffeeRepository
from src.repositories.database import db
from src.utils.logger.log import log_error
from duckduckgo_search import DDGS
from langchain_core.tools import tool
from typing import List

logger = logging.getLogger(__name__)

repo = CoffeeRepository(db.SessionLocal())


@router.tool()
def format_python(code: str):
    """Use this Tool for Format Python code from  the User """
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(code.encode())
            filename = f.name

        subprocess.run(
            ["black", filename],
            capture_output=True,
            text=True
        )

        with open(filename, "r") as f:
            formatted_code = f.read()
        print("===============================Format Tool Response===============")
        print(formatted_code)
        print("==================================================================")


        return {"formatted_code": formatted_code}

    except Exception:
        log_error("format_python", message=traceback.format_exc())
        raise


@router.tool()
def lint_python(code: str):
    """Use this Tool to Lint Python code from the User."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
            f.write(code.encode())
            filename = f.name

        result = subprocess.run(
            ["ruff", "check", filename],
            capture_output=True,
            text=True
        )
        print("===============================Lint Tool result params  Response===============",result.stdout)
        print("===============================Lint Tool Return Code  Response===============",result.returncode)
        print("===============================Lint Tool Return Code != 0   Response===============",result.returncode != 0 )

        return {
            "lint_output": result.stdout,
            "errors": result.returncode != 0
        }

    except Exception:
        log_error("lint_python", message=traceback.format_exc())
        raise



@router.tool()
def duckduckgo_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo.

    Args:
        query:       Search query string.
        max_results: Max number of results (default 5).

    Returns:
        Formatted string of results with title, URL, and snippet.
    """
    try:
        with DDGS() as ddgs:
            results: List[dict] = list(ddgs.text(query, max_results=max_results))
            print("===================================SEARCH QUERY")
            print(results)
            print("======================END======================")

        if not results:
            return f"No results found for: '{query}'"

        formatted = []
        for i, r in enumerate(results, start=1):
            formatted.append(
                f"[{i}] {r.get('title', 'No title')}\n"
                f"    URL     : {r.get('href', 'N/A')}\n"
                f"    Snippet : {r.get('body', 'No snippet')}\n"
            )
        return "\n".join(formatted)

    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}", exc_info=True)
        return f"Search failed: {e}" 
