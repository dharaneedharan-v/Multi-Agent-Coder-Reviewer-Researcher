
import datetime
import inspect
import time
import traceback

from sqlalchemy.orm import Session
from src.repositories.schema.schema import * 

class CoffeeRepository:
    def __init__(self, db: Session):
        self.db = db
    def save_log_error(self, file_name: str, function_name: str, message: str):
        try:
            error = Error(
                file_name=file_name,
                function_name=function_name,
                message=message,
                error_time = datetime.datetime.now(datetime.timezone.utc)

            )
            self.db.add(error)
            self.db.commit()
        except Exception:

            self.db.rollback()
            # self.log_error(traceback.format_exc())
            raise 
    
    # Called directly inside repo function
    def _log_error(self, message: str):
        """Called inside repo itself — auto captures file and function."""
        try:
            frame = inspect.currentframe().f_back
            error = Error(
                file_name    =inspect.getfile(frame),
                function_name=frame.f_code.co_name,
                message      =message,
                error_time   =datetime.datetime.now(datetime.timezone.utc)

            )
            self.db.add(error)
            self.db.commit()
        except Exception:
            self.db.rollback()
        
    def get_customer_by_id (self , customer_id : int ):
        try :
            customer = (
                self.db.query(Customer)
                .filter (Customer.customer_id==customer_id)
                .first()
                )
            return customer 
        except Exception:
            self.db.rollback()
            self._log_error(traceback.format_exc())
            raise 
