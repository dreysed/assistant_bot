from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine("sqlite:///bot_database.db", echo=True)
Base = declarative_base()

class Workout(Base):
    __tablename__ = 'trainings'

    id = Column(Integer, primary_key=True)
    details = Column(String, unique=False, nullable=False)
    hour = Column(Integer, unique=False, nullable=False)
    minute = Column(Integer, unique=False, nullable=False)
    id_of_chat = Column(Integer, unique=False, nullable=False)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)

