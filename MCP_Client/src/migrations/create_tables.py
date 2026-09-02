
from sqlalchemy import inspect


# from src.models.ragmodel import RAG_TABLE
from src.repositories.schema.schema import* 
from src.repositories.Database import Database


TABLE_ORDER_CREATION = [
    Customer.__tablename__,
    Error.__tablename__
   
]

MODEL_CLASSES = {
    Customer.__tablename__: Customer,
    Error.__tablename__: Error
   
}


class Migration:
    def __init__(self):
        self.db = Database()
        self.engine = self.db.engine
        self.inspector = inspect(self.engine)
    def create_tables(self):
    
        
        for table_name in TABLE_ORDER_CREATION:
            if not self.inspector.has_table(table_name):
                MODEL_CLASSES[table_name].__table__.create(bind=self.engine)

