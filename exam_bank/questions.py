import json
from pathlib import Path
from typing import List, Dict

QUESTIONS_FILE = Path("exam_bank/questions.json")

# Ensure the file exists
if not QUESTIONS_FILE.exists():
    QUESTIONS_FILE.write_text("[]")

def save_questions(questions: List[Dict]):
    """Save questions to a JSON file."""
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=4)

def load_questions() -> List[Dict]:
    """Load questions from the JSON file."""
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def add_question(question: Dict):
    """Add a new question to the storage."""
    questions = load_questions()
    questions.append(question)
    save_questions(questions)

# Used for JSON, not needed if I decide to switch to sql