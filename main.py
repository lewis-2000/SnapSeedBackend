from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from typing import List
import json

from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./questions.db" 
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Import models
from database import Question, Exam

# FastAPI app setup
app = FastAPI()

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Pydantic models for request validation
class QuestionCreate(BaseModel):
    text: str
    options: List[str]
    answer: str

class ExamCreate(BaseModel):
    title: str
    question_ids: List[int]  # Store selected question IDs

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to create a new question
@app.post("/questions/")
async def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    db_question = Question(text=question.text, options=question.options, answer=question.answer)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

# Route to get all questions
@app.get("/questions/")
async def get_questions(db: Session = Depends(get_db)):
    result = db.execute(select(Question)).scalars().all()
    return result

# Route to create an exam
@app.post("/exams/")
async def create_exam(exam: ExamCreate, db: Session = Depends(get_db)):
    # Ensure all questions exist
    questions = db.query(Question).filter(Question.id.in_(exam.question_ids)).all()
    if len(questions) != len(exam.question_ids):
        raise HTTPException(status_code=400, detail="Some questions not found")

    db_exam = Exam(title=exam.title, question_ids=json.dumps(exam.question_ids))
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

# Route to get an exam with its questions
@app.get("/exams/{exam_id}")
async def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    question_ids = json.loads(exam.question_ids)
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    
    return {"id": exam.id, "title": exam.title, "questions": questions}

# Route to generate a marking scheme
@app.get("/exams/{exam_id}/marking_scheme")
async def generate_marking_scheme(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    question_ids = json.loads(exam.question_ids)
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()

    marking_scheme = {q.text: q.answer for q in questions}
    return {"exam_id": exam.id, "title": exam.title, "marking_scheme": marking_scheme}


# Directory to store generated files
OUTPUT_DIR = "generated_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_pdf(content: str, filename: str) -> str:
    """Generate a PDF with given content and return the file path."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    y_position = height - 40  # Start below the top margin
    
    for line in content.split("\n"):
        c.drawString(40, y_position, line)
        y_position -= 20  # Move to the next line
    
    c.save()
    return file_path

@app.get("/exams/{exam_id}/export/")
async def export_exam(exam_id: int, db: Session = Depends(get_db)):
    """Generate a PDF for an exam."""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    question_ids = json.loads(exam.question_ids)
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()

    content = f"Exam: {exam.title}\n\n"
    for idx, question in enumerate(questions, start=1):
        content += f"{idx}. {question.text}\n"
        for opt_idx, option in enumerate(question.options, start=1):
            content += f"   {chr(65 + opt_idx - 1)}. {option}\n"
        content += "\n"
    
    file_path = generate_pdf(content, f"exam_{exam_id}.pdf")
    return FileResponse(file_path, media_type="application/pdf", filename=f"exam_{exam_id}.pdf")

@app.get("/exams/{exam_id}/export/marking_scheme")
async def export_marking_scheme(exam_id: int, db: Session = Depends(get_db)):
    """Generate a PDF for the marking scheme."""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    question_ids = json.loads(exam.question_ids)
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()

    content = f"Marking Scheme: {exam.title}\n\n"
    for idx, question in enumerate(questions, start=1):
        content += f"{idx}. {question.text}\n   Answer: {question.answer}\n\n"
    
    file_path = generate_pdf(content, f"marking_scheme_{exam_id}.pdf")
    return FileResponse(file_path, media_type="application/pdf", filename=f"marking_scheme_{exam_id}.pdf")


@app.get("/stats/")
async def get_stats(db: Session = Depends(get_db)):
    question_count = db.query(Question).count()
    exam_count = db.query(Exam).count()
    marking_scheme_count = exam_count  # Since each exam has a marking scheme
    answer_count = db.query(Question).count()  # If each question has one answer

    return {
        "questionCount": question_count,
        "answerCount": answer_count,
        "examCount": exam_count,
        "markingSchemeCount": marking_scheme_count,
    }


# Running the application directly using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
