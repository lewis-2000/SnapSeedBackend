from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.database import get_db, Question, Exam

router = APIRouter()

# Pydantic models
class QuestionCreate(BaseModel):
    text: str
    options: List[str]
    answer: str

class ExamCreate(BaseModel):
    title: str
    question_ids: List[int]  # Store selected question IDs

# Directory to store generated PDFs
OUTPUT_DIR = "generated_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Utility to generate a PDF
def generate_pdf(content: str, filename: str) -> str:
    """Generate a PDF with given content and return the file path."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    y_position = height - 40  

    for line in content.split("\n"):
        c.drawString(40, y_position, line)
        y_position -= 20  
    
    c.save()
    return file_path

# Routes
@router.get("/")
async def home():
    return {"message": "Welcome to the Exam Bank API"}

@router.post("/questions/")
async def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    db_question = Question(text=question.text, options=question.options, answer=question.answer)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

@router.get("/questions/")
async def get_questions(db: Session = Depends(get_db)):
    return db.query(Question).all()

@router.post("/exams/")
async def create_exam(exam: ExamCreate, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.id.in_(exam.question_ids)).all()
    if len(questions) != len(exam.question_ids):
        raise HTTPException(status_code=400, detail="Some questions not found")

    db_exam = Exam(title=exam.title, question_ids=json.dumps(exam.question_ids))
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

@router.get("/exams/{exam_id}")
async def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    question_ids = json.loads(exam.question_ids)
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()

    return {"id": exam.id, "title": exam.title, "questions": questions}

@router.get("/exams/{exam_id}/marking_scheme")
async def generate_marking_scheme(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    question_ids = json.loads(exam.question_ids)
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()

    marking_scheme = {q.text: q.answer for q in questions}
    return {"exam_id": exam.id, "title": exam.title, "marking_scheme": marking_scheme}

@router.get("/exams/{exam_id}/export/")
async def export_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
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

@router.get("/stats/")
async def get_stats(db: Session = Depends(get_db)):
    question_count = db.query(Question).count()
    exam_count = db.query(Exam).count()

    return {
        "questionCount": question_count,
        "examCount": exam_count,
    }
