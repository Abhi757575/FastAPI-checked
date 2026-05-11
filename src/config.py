from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

class Settings(BaseSettings):
    DB_CONNECTION: str

    model_config = SettingsConfigDict(env_file=".env",
                                      extra="ignore")
    
Config = Settings()