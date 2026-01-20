from dotenv import load_dotenv
load_dotenv()

from controller import run as run_controller
from fastapi import FastAPI,Form,File,UploadFile,HTTPException
import tempfile
import os

from ingestion.text_loader import load_text
from ingestion.pdf_loader import load_pdf
from ingestion.img_loader import load_img

app=FastAPI(title="AI Study Assistant",
            description="Analyze text, PDFs, or images and generate study-friendly explanations.",
            version="1.0.0")

@app.get("/health")
def health_check():
    return {"status":"ok"}

@app.post("/analyze")
def analyze(
    input_type: str=Form(...),
    content: str|None=Form(None),
    file: UploadFile|None=Form(None)
):
    if input_type == "text":
        if not content:
            raise HTTPException(status_code=400,detail="Text content is missing")
        text=load_text(content)
    elif input_type in {"pdf"|"image"}:
        if not file:
            raise HTTPException(status_code=400,detail="File is missing")
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.file.read())
            tmp_path=tmp.name

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