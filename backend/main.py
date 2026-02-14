from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
from ai_icd_suggester import process_medical_file_with_ai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/match-icd-codes")
async def match_icd_codes(file: UploadFile = File(...)):
    """
    Upload CSV or XLSX file for AI-powered ICD code suggestion.
    """
    
    if not (file.filename.endswith('.csv') or 
            file.filename.endswith('.xlsx') or 
            file.filename.endswith('.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    try:
        file_content = await file.read()
        result = process_medical_file_with_ai(file_content, file.filename)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AI Medical Coding Assistant - Powered by Gemini"}