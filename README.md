
```python
├─── MCP_Client
│   ├─── src
│   │   ├─── agent
│   │   │   ├─── coder_agent.py
│   │   │   ├─── research_agent.py
│   │   │   └─── review_agent.py
│   │   ├─── migrations
│   │   │   ├─── factory
│   │   │   │   └─── factory.py
│   │   │   ├─── __init__.py
│   │   │   ├─── create_tables.py
│   │   │   └─── seeder.py
│   │   ├─── models
│   │   │   └─── models.py
│   │   ├─── prompt
│   │   │   ├─── coder_prompt.py
│   │   │   ├─── research_prompt.py
│   │   │   ├─── review_prompt.py
│   │   │   └─── router_prompt.py
│   │   ├─── repositories
│   │   │   ├─── schema
│   │   │   │   └─── schema.py
│   │   │   ├─── database.py
│   │   │   └─── repository.py
│   │   ├─── routes
│   │   │   └─── routes.py
│   │   ├─── service
│   │   │   ├─── agentservice.py
│   │   │   └─── graph.py
│   │   ├─── utils
│   │   │   ├─── exceptions
│   │   │   │   ├─── custom_exception.py
│   │   │   │   ├─── error_code.py
│   │   │   │   ├─── error.py
│   │   │   │   └─── global_exception.py
│   │   │   ├─── LLM
│   │   │   │   └─── invoke.py
│   │   │   ├─── logger
│   │   │   │   └─── log.py
│   │   │   ├─── __init__.py
│   │   │   └─── helpers.py
│   │   └─── settings.py
│   ├─── .gitignore
│   ├─── .python-version
│   ├─── env.txt
│   ├─── main.py
│   ├─── pyproject.toml
│   ├─── README.md
│   └─── requiements.py
├─── MCP_Server
│   ├─── src
│   │   ├─── repositories
│   │   │   ├─── schema
│   │   │   │   └─── schema.py
│   │   │   ├─── database.py
│   │   │   └─── repository.py
│   │   ├─── routes
│   │   │   └─── routes.py
│   │   ├─── tools
│   │   │   └─── tools.py
│   │   └─── utils
│   │       ├─── logger
│   │       │   └─── log.py
│   │       └─── helper.py
│   ├─── .gitignore
│   ├─── .python-version
│   ├─── main.py
│   ├─── pyproject.toml
│   └─── README.md
└─── .gitignore

```
