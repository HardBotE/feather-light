from src.app.db.base import Base
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())


DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST', 'db')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

if os.getenv("TESTING") == "1":
    DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(DATABASE_URL)


def start_db():
    Base.metadata.create_all(engine)
