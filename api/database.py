from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


db_url = "mysql+pymysql://root@db:3306/demo?charset=utf8"

engine = create_engine(db_url, echo=True)

# DB 세션 생성하기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class 생성하기
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
