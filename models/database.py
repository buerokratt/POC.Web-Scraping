from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON, Interval, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

Base = declarative_base()

class LinkMetadata(Base):
    """SQLAlchemy model for storing metadata of scraped links."""
    __tablename__ = "link_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)
    language = Column(String, nullable=True)
    last_modified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    scraped_at = Column(DateTime, default=datetime.now)
    status_code = Column(Integer, nullable=True)
    parsed_at = Column(DateTime, nullable=True)
    parsed_data = Column(JSON, nullable=True)

class ScrapingSchedule(Base):
    """SQLAlchemy model for storing scraping schedules."""
    __tablename__ = "scraping_schedule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    scraped_at = Column(DateTime, default=datetime.now)
    scraping_interval = Column(Interval, nullable=False)
    is_active = Column(Boolean, default=True)

def get_db_session():
    db_user = os.environ.get("POSTGRES_USER", "postgres")
    db_password = os.environ.get("POSTGRES_PASSWORD", "password")
    db_host = os.environ.get("POSTGRES_HOST", "localhost")
    db_port = os.environ.get("POSTGRES_PORT", "5432")
    db_name = os.environ.get("POSTGRES_DB", "scrapy_metadata")

    engine_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(engine_url, echo=False)

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()

