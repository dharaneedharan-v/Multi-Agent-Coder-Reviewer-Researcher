
import os
import logging
from urllib.parse import quote_plus
import boto3
from langchain_aws import ChatBedrock

logger = logging.getLogger(__name__)


def get_bedrock_client():
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("REGION"),
    )


def get_llm(max_tokens: int = 2048, temperature: float = 0.7) -> ChatBedrock:
    return ChatBedrock(
        client=get_bedrock_client(),
        model_id=os.getenv("MODEL_ID"),
        provider="amazon",
        model_kwargs={
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
    )


def get_db_uri() -> str:
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    return (
        f"postgresql://{os.getenv('DB_USERNAME')}:{password}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
