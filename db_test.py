import psycopg2
from dotenv import load_dotenv
import os
#from src.utils.settings import settings

load_dotenv()  # loads variables from .env file
DB_CONNECTION = os.getenv("DB_CONNECTION")
#Connect = settings.DB_CONNECTION

try:
    conn = psycopg2.connect(
        DB_CONNECTION
    )
    print("✅ Connected successfully!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:")
    print(e)