


import asyncio
import sys

# CRITICAL: Must be first - before ANY other imports
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from src.settings import config
from src.routes.routes import router
from src.repositories.Database import Database
from src.utils.exceptions.global_exception_handlers import global_register_exception_handlers
from src.utils.logger.log import setup_logger, logger

# Global variables
app_config = None
db_connection = None

def initialize_config():
    """Initialize configuration from environment variables"""
    global app_config, db_connection
    try:
        app_config = config
        db_connection = Database()
        
        log_level = getattr(logging, app_config.log_level.upper(), logging.INFO)
        logging.getLogger().setLevel(log_level)
        
        logger.info("Configuration initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize configuration: {e}")
        return False

def create_app():
    """Create and configure the FastAPI app"""
    app = FastAPI(
        title="LangGraph Coding MultiAgetnt Application API",
        description="LangGraph Coding MultiAgetnt Application API TASK-1",
        version="1.0.1"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )
    
    app.include_router(router)
    global_register_exception_handlers(app)
    return app

def run_local_server():
    """Run the server locally with uvicorn"""
    
    # Event loop policy already set at module level
    logger.info("Starting in local development mode.")
    
    if not initialize_config():
        logger.error("Failed to initialize configuration")
        exit(1)
    
    if not db_connection.test_connection():
        logger.error("Database connection test failed")
        exit(1)
    
    # Run migrations
    try:
        from src.migrations.create_tables import Migration
        migration = Migration()
        migration.create_tables()
        logger.info("Database tables created successfully")
        
        try:
            from src.migrations.seeder import DatabaseSeeder 
            Feed = DatabaseSeeder()
            Feed.seed()
        except Exception as e:
            logger.error(f'Seeder Failed: {e}')
    except Exception as e:
        logger.warning(f"Migration failed: {e}")
    
    port = int(app_config.port)
    host = app_config.host
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Database: {app_config.db_host}:{app_config.db_port}/{app_config.db_name}")
    logger.info("Successfully database Connected!")
    
    app = create_app()
    
    # Use uvicorn.Server to respect event loop policy
    config_uvicorn = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=False,
        log_level=app_config.log_level.lower(),
        access_log=True,
        loop="asyncio"
    )
    
    server = uvicorn.Server(config_uvicorn)
    server.run()

if __name__ == "__main__":
    try:
        run_local_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        exit(1)



# remove the condtonal edges from graph building. 
#  import command 
# return {** state } to return command (goto = "m=next_node , upatde = nwe_state")
# routing inside the node 
# 
# remove def router_after_()
#  

