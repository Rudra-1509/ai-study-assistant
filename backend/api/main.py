from dotenv import load_dotenv
load_dotenv()
import tempfile
import os
from typing import Optional

from fastapi import FastAPI,Form,File,UploadFile,HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.ingestion.text_loader import load_text
from backend.ingestion.pdf_loader import load_pdf
from backend.ingestion.img_loader import load_img

from backend.controller import run as run_controller

app=FastAPI(title="AI Study Assistant",
            description="Analyze text, PDFs, or images and generate study-friendly explanations.",
            version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status":"ok"}

@app.post("/analyze")
def analyze(
    input_type: str=Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    if input_type == "text":
        if not content:
            raise HTTPException(status_code=400,detail="Text content is missing")
        text=load_text(content)
    elif input_type in {"pdf","image"}:
        if not file:
            raise HTTPException(status_code=400,detail="File is missing")
        
        suffix=os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False,suffix=suffix) as tmp:
            tmp.write(file.file.read())
            tmp_path=tmp.name

        file.file.close()

        try:
            if input_type=="pdf":
                text=load_pdf(tmp_path)
            else:
                text=load_img(tmp_path)
        finally:
            os.remove(tmp_path)
    else:
        raise HTTPException(status_code=400,detail="Invalid input_type.Must be one of: text,pdf,image")
    
    result=run_controller(text)
    return result