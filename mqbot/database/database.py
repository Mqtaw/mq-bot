from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Config


SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI
    # f'postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}'

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_web_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        while True:
            yield db
    finally:
        db.close()
