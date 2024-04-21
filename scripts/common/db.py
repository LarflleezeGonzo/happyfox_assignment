
from sqlalchemy import Column, Date, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
from common.config import settings

DB_URI = settings.DBI_URI

# SQLAlchemy setup
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Define the email table
class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String)
    subject = Column(Text)
    date_received = Column(Date)
    sender = Column(String)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()