
# import inspect
# import logging
# import sys
# import traceback
# import time
# from functools import wraps  # FIXED
# from src.repositories.schema.schema import Error
# from src.repositories.repository import *
# # from your_models import Error  # Import your DB Error model instead of csv.Error

# def setup_logger():
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
#         handlers=[logging.StreamHandler(sys.stdout)]
#     )

# def get_logger(name: str):
#     return logging.getLogger(name)


# # Configure logging once
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
#     handlers=[logging.StreamHandler(sys.stdout)]
# )
# logger = logging.getLogger(__name__)



# def log_error(repo, message: str):
#     """
#     Called from: routes, service, tools, resources, prompts
#     Gets file and function name automatically.
#     """
#     frame         = inspect.currentframe().f_back
#     file_name     = inspect.getfile(frame)
#     function_name = frame.f_code.co_name

#     repo.log_error(
#         file_name    =file_name,
#         function_name=function_name,
#         message      =message
#     )


# # def db_error(func):
# #     """
# #     Decorator that logs exceptions to both the database and the console.
# #     """
# #     @wraps(func)
# #     def wrapper(*args, **kwargs):
# #         try:
# #             return func(*args, **kwargs)
# #         except Exception as e:
# #             db = None
# #             for arg in args:
# #                 if hasattr(arg, "db"):
# #                     db = arg.db
# #                     break

# #             # Get caller info
# #             frame_info = inspect.stack()[1]
# #             file_name = frame_info.filename.split("\\")[-1]
# #             function_name = func.__name__
# #             error_message = traceback.format_exc()

# #             # Log to console
# #             # logger.error(
# #             #     f"Error in {function_name} ({file_name}): {str(e)}\n{error_message}"
# #             # )

# #             # Log to DB if available 
# #             if db:
# #                 try:
# #                     error_entry = Error(
# #                         file_name=file_name,
# #                         function_name=function_name,
# #                         message=error_message,
# #                         error_time=time.time()
# #                     )
# #                     db.add(error_entry)
# #                     db.commit()
# #                 except Exception as db_err:
# #                     logger.error(f"Failed to log error to DB: {db_err}")

# #             # Re-raise to stop execution OR comment out to continue
# #             raise
# #     return wrapper

import inspect
import logging
import sys
import traceback
import time
from functools import wraps
from src.repositories.schema.schema import Error
from src.repositories.repository import *

# --- COLOR CONFIGURATION ---
class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class ColoredFormatter(logging.Formatter):
    FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    
    LEVEL_COLORS = {
        logging.DEBUG: ConsoleColors.OKBLUE,
        logging.INFO: ConsoleColors.OKGREEN,
        logging.WARNING: ConsoleColors.WARNING,
        logging.ERROR: ConsoleColors.FAIL,
        logging.CRITICAL: ConsoleColors.BOLD + ConsoleColors.FAIL,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, ConsoleColors.ENDC)
        # Apply color to the level name and the message
        record.levelname = f"{color}{record.levelname}{ConsoleColors.ENDC}"
        record.msg = f"{color}{record.msg}{ConsoleColors.ENDC}"
        formatter = logging.Formatter(self.FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

# --- LOGGER SETUP ---
def setup_logger():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

def get_logger(name: str):
    return logging.getLogger(name)

# Initialize once
setup_logger()
logger = get_logger(__name__)

# --- YOUR EXISTING FUNCTIONS ---
def log_error(repo, message: str):
    frame = inspect.currentframe().f_back
    file_name = inspect.getfile(frame)
    function_name = frame.f_code.co_name

    # Console log with color (automatic via formatter)
    logger.error(f"Error in {function_name}: {message}")

    repo.save_log_error(
        file_name=file_name,
        function_name=function_name,
        message=message
    )