import os
from dotenv import load_dotenv

from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool


class DBConnector:
    db_drivername: str
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    def __init__(self):
        load_dotenv()

        self.db_drivername = 'postgresql+pg8000'
        self.db_username = os.getenv("DB_USERNAME")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_host = os.getenv("DB_HOST")
        self.db_port = int(os.getenv("DB_PORT"))
        self.db_name = os.getenv("DB_NAME")

    def create_sql_engine(self) -> Engine:
        url_object = URL.create(
            drivername=self.db_drivername, username=self.db_username,
            password=self.db_password, host=self.db_host,
            port=self.db_port, database=self.db_name
        )

        return create_engine(url_object, poolclass=NullPool)

    def create_session(self) -> Session:
        my_session = sessionmaker(bind=self.create_sql_engine())
        session = my_session()

        return session
