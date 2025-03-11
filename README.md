# 📘 Exam Bank System – Backend (FastAPI)

This is the backend of the **Exam Bank System**, built using FastAPI. It handles question storage, exam creation, marking scheme generation, and PDF export.

## 🚀 Features
✅ **Store & Retrieve Questions**  
✅ **Create & Manage Exams**  
✅ **Generate Marking Schemes**  
✅ **Export Exams & Marking Schemes as PDFs**  
✅ **FastAPI for High-Performance API Handling**  
✅ **SQLite Database Support**  
✅ **CORS Enabled for Frontend Communication**  

## 📂 Project Structure


## 🛠️ Installation & Setup
```txt
backend/ │── database.py # Database models & setup │── main.py # FastAPI main app │── requirements.txt # Required dependencies │── generated_files/ # Stores exported PDFs │── .env.example # Example environment variables └── README.md # This file
```

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/lewis-2000/SnapSeedBackend.git
cd exam-bank-backend
```

### 2️⃣ Activate and use Venv
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows

```
### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```
### 4️⃣ Run the Server
```sh
uvicorn app:app --reload
```

### 🎯 Future Improvements
```txt
✅ Authentication & User Management
✅ Cloud Storage for PDFs
✅ Enhanced Exam Editing
```
