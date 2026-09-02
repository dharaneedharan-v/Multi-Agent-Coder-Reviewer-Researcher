

import urllib.parse
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

from src.settings import config

Base = declarative_base()


class Database:
    
    #      Singleton state                                                                                       
    _instance:    "Database | None" = None
    _initialized: bool              = False
    #      __new__ enforces Singleton                                                                 
    def __new__(cls) -> "Database":
        if cls._instance is None:
            print(f"[Singleton] Creating NEW Database instance")
            cls._instance = super().__new__(cls)
        else:
            print(f"[Singleton] Reusing EXISTING Database instance — id={id(cls._instance)}")
        return cls._instance

    # __init__ runs once thanks to _initialized guard                       
    def __init__(self):
        

        if self._initialized:
            return              # already set up — skip
        print(f"[Singleton] Initializing engine — id={id(self)}")
        self.engine       = self._create_engine()
        self.SessionLocal = sessionmaker(
            bind       = self.engine,
            autoflush  = False,
            autocommit = False,
        )
        Database._initialized = True

    # Engine factory                                                                                         
    def _create_engine(self):
        
        encoded_pw = urllib.parse.quote(config.db_password)
        db_url = (
            f"postgresql+psycopg://{config.db_username}:{encoded_pw}"
            f"@{config.db_host}:{config.db_port}/{config.db_name}"
        )

        return create_engine(db_url, pool_pre_ping=True)

    #      Session generator                                                                                   
    def get_session(self)  -> Generator:
       
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    #      Utilities                                                                                                   
    def inspector(self, engine=None):
        return inspect(engine or self.engine)

    def test_connection(self)  -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as exc:
            print(f"[Database] Connection failed: {exc}")
            return False


# Module level Singleton instance                                                               
# Every import of `db` gets the SAME object
db = Database()


# FastAPI dependency                                                                                           
def get_db()  -> Generator:
    
    yield from db.get_session()