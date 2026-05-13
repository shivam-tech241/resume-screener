from fastapi import FastAPI
from fastapi import UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pypdf
import io
import uuid
import chromadb
from chromadb.utils import embedding_functions
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

print("KEY:", os.getenv("GEMINI_API_KEY"))

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

app = FastAPI(title = "Resume Screener API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

chroma_client = chromadb.PersistentClient(path="./resume_db")
collection = chroma_client.get_or_create_collection(name="resumes")

class ResumeInput(BaseModel):
    resume_text: str
    job_description: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze-resume")
def analyze_resume(data: ResumeInput):
    if data.job_description:
        jd_section = f"\nJob Description:\n{data.job_description}"
        match_instruction = '\n- match_score: integer from 0 to 100 showing how well the candidate fits the job description'
    else:
        jd_section = ""
        match_instruction = ""
    prompt = f"""
You are a resume screening assistant.

Resume:
{data.resume_text}

Job description:
{jd_section if jd_section else "Not provided"}

Return only this JSON:
{{
    "score": <0 to 100 overall candidate score>,
    "skills": [<list of skills from resume>],
    "decision": <"Strong Hire", "Shortlist", "Maybe", or "Reject">,
    "match_score": <0 to 100 how well resume matches the job description or null if no JD>
}}

No explanation. No markdown. Just the JSON.
"""
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b:free",
        messages=[{"role": "user", "content": prompt}]
    )
    result = response.choices[0].message.content.strip()
    return json.loads(result)
    
@app.post("/analyze-resume/upload")
async def analyze_resume_upload(
    file: UploadFile = File(...),
    job_description: str = None
):
    contents = await file.read()
    pdf_reader = pypdf.PdfReader(io.BytesIO(contents))

    resume_text = ""
    for page in pdf_reader.pages:
        resume_text += page.extract_text()

    if not resume_text.strip():
        return {"error": "Could not extract text from PDF"}
    
    return analyze_resume(ResumeInput(resume_text=resume_text, job_description=job_description))

@app.post("/resumes/store")
async def store_resume(file: UploadFile = File(...), candidate_name: str = None):
    contents = await file.read()
    pdf_reader = pypdf.PdfReader(io.BytesIO(contents))

    resume_text = ""
    for page in pdf_reader.pages:
        resume_text += page.extract_text()

    if not resume_text.strip():
        return {"error": "Could not extract text from PDF"}

    resume_id = str(uuid.uuid4())
    
    collection.add(
        documents=[resume_text],
        metadatas=[{"name": candidate_name or file.filename, "filename": file.filename}],
        ids=[resume_id]
    )
    return {"message": "Resume stored successfully", "id": resume_id, "candidate": candidate_name or file.filename}

@app.post("/resumes/search")
def search_resumes(job_description: str, top_k: int = 5):
    results = collection.query(
        query_texts=[job_description],
        n_results=min(top_k, collection.count())
    )
    if not results["documents"][0]:
        return {"message": "No resumes found in database", "candidates": []}
    
    candidates = []
    for i, doc in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        match_score = round((1 - distance) * 100, 1)
        candidates.append({
            "rank": i + 1,
            "candidate": metadata.get("name"),
            "match_score": match_score,
            "resume_preview": doc[:200] + "..."
        })
    
    return {"job_description": job_description, "total_found": len(candidates), "candidates": candidates}
