from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import os
from sqlalchemy import create_engine

from src.app.db.base import Base
from src.app.models.user_table import Users
from src.app.models.project_table import Projects
from src.app.models.attachment_to_project_table import AttachmentToProject
from src.app.models.user_to_project_table import UserToProjectTable

DATABASE_URL = (f"postgresql+psycopg2://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@"
                f"{os.getenv('DB_HOST','db')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

engine = create_engine(DATABASE_URL)

def start_db():
    Base.metadata.create_all(engine)

