
import traceback

from src.service.agentservice import AgentService
from fastapi import APIRouter, Query, Request, HTTPException, Response , Depends
from typing import Optional
import json
# from src.services.service import *
from src.models.models import * 
from src.repositories.database import * 
from src.repositories.repository import * 
from src.utils.logger.log import log_error 
from src.utils.helpers  import  * 
router = APIRouter()
@router.post("/chat", response_model=APIResponse)
async def chat(request: ChatRequest, db=Depends(get_db)):
    try:
        repo = CoffeeRepository(db)
        service = AgentService(repo)
        result = await service.chat(
            request.message,
            request.customer_id
        )

        return success_response(
            message="Chat processed successfully",
            data=result
        )

    except Exception as e:
        log_error (repo , message=traceback.format_exc())
        # raise 
        return error_response(
            message="Failed to process chat",
            error=e,
            code=400
        )