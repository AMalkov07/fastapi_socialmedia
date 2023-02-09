# this is the file we use to specify which environment variables are necessary for running this program
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        # env_file should contain the path to the file that contains the information for your environment variables
        env_file = "../.env"

settings = Settings()
