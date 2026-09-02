
# from dataclasses import dataclass
# import os
# import dotenv

# dotenv.load_dotenv()

# PROJECT_ARN =  os.getenv("PROJECT_ARN")
# PROFILE_ARN = os.getenv("PROFILE_ARN")
# INPUT_S3_URI = os.getenv("INPUT_S3_URI") 
# OUTPUT_S3_URI = os.getenv("OUTPUT_S3_URI")
# BLUEPRINT_NAME =  os.getenv("BLUEPRINT_NAME")
# REGION = os.getenv("REGION")

# # create database database_name --> alternative ORM query 
# @dataclass
# class Config:
#     db_port: str
#     db_host: str
#     db_name: str
#     db_username: str
#     db_password: str
#     port: int
#     host: str
#     log_level: str

# def get_config():
#     """
#     Load application configuration from environment variables.

#     Returns
#     -------
#     Config
#         Configuration object populated from environment variables.

#     Raises
#     ------
#     ValueError
#         If required environment variables are missing or invalid.
#     """
#     return Config(
#         db_port=os.getenv('DB_PORT'),
#         db_host=os.getenv('DB_HOST'),
#         db_name=os.getenv('DB_NAME'),
#         db_username=os.getenv('DB_USERNAME'),
#         db_password=os.getenv('DB_PASSWORD'),
#         port=int(os.getenv('PORT', '8080')),
#         host=os.getenv('HOST', '127.0.0.1'),
#         log_level=os.getenv('LOG_LEVEL', 'INFO')
#     )

# config = get_config()



from dataclasses import dataclass
import os
import dotenv

dotenv.load_dotenv()


@dataclass
class Config:

    # AWS BDA
    project_arn: str
    profile_arn: str
    input_s3_uri: str
    output_s3_uri: str
    blueprint_name: str
    region: str

    # DB
    db_port: str
    db_host: str
    db_name: str
    db_username: str
    db_password: str

    # App
    port: int
    host: str
    log_level: str


def get_config():

    return Config(

        project_arn=os.getenv("PROJECT_ARN"),
        profile_arn=os.getenv("PROFILE_ARN"),
        input_s3_uri=os.getenv("INPUT_S3_URI"),
        output_s3_uri=os.getenv("`OUTPUT_S3_URI1`"),
        blueprint_name=os.getenv("`BLUEPRINT_NAME`"),
        region=os.getenv("REGION", "us-east-1"),

        db_port=os.getenv("DB_PORT"),
        db_host=os.getenv("DB_HOST"),
        db_name=os.getenv("DB_NAME"),
        db_username=os.getenv("DB_USERNAME"),
        db_password=os.getenv("DB_PASSWORD"),

        port=int(os.getenv("PORT", "8080")),
        host=os.getenv("HOST", "127.0.0.1"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


config = get_config()

