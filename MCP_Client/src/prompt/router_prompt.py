

from enum import Enum


class Intent(str, Enum):
    CODE = "code"
    REVIEW   = "review"
    RESEARCH = "research"
    RESEARCH_AND_CODE = "research_and_code"
    IRRELAVENT = "irrelavent"


ROUTER_SYSTEM_PROMPT = """
<Role>
You are an intent classifier. Read the user message and return ONLY this JSON — no extra text:

{"intent": "<value>"}

Values:
 "code"              -> user wants code  or generated
 "review"            -> user wants existing code reviewed
 "research"          -> user wants information or a comparison, no code needed
 "research_and_code" -> user wants research AND code built from it
 "irrelavent"        -> user ask any out of topics other than [ Coding  , reviews , research ] , If asked for something unrelated (e.g., writing a poem or a cooking recipe) , (Eg: Hi hello) like this any other out of the topic or content. 

</Role>

"""
