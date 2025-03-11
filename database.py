from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# SQLite database
DATABASE_URL = "sqlite:///./questions.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Question model
class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    options = Column(JSON, nullable=False)  # Stores multiple-choice options
    answer = Column(String, nullable=False)  # Correct answer

# Define the Exam model
class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    question_ids = Column(JSON, nullable=False)  # Stores list of question IDs


# Marking Scheme model
class MarkingScheme(Base):
    __tablename__ = "marking_schemes"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    answers = Column(JSON, nullable=False)  # Question ID -> Correct Answer Mapping
    exam = relationship("Exam")

# Create tables
Base.metadata.create_all(bind=engine)
