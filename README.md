# 🤖 AI Resume Screener

An AI-powered resume screening API and web app that analyzes resumes, extracts skills, scores candidates, and gives hiring decisions — built with FastAPI and OpenRouter.

---

## Features

- Upload resume as PDF or paste as text
- AI extracts skills automatically
- Scores candidate from 0 to 100
- Returns hiring decision (Strong Hire / Shortlist / Maybe / Reject)
- Job description matching with match score
- Store multiple resumes and search by job description (RAG)
- Clean purple/pink gradient frontend

---

## Tech Stack

- **Backend:** Python, FastAPI
- **AI:** OpenRouter API (Nvidia Nemotron model)
- **Vector Database:** ChromaDB
- **Frontend:** HTML, CSS, JavaScript
- **PDF Parsing:** pypdf

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/resume-screener.git
cd resume-screener
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
Create a `.env` file:

### 4. Run the server
```bash
uvicorn main:app --reload
```

### 5. Open the frontend
Open `index.html` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze-resume` | Analyze resume from text |
| POST | `/analyze-resume/upload` | Analyze resume from PDF |
| POST | `/resumes/store` | Store resume in database |
| POST | `/resumes/search` | Search resumes by job description |
| GET | `/health` | Health check |

---

## Example Response

```json
{
  "score": 88,
  "skills": ["Python", "TensorFlow", "Keras", "NumPy"],
  "decision": "Strong Hire",
  "match_score": 95
}
```

---

## Getting an API Key

Sign up at [openrouter.ai](https://openrouter.ai) and create a free API key.
