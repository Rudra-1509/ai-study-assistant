from dotenv import load_dotenv
load_dotenv()
import tempfile
import os
import traceback
from typing import Optional
from contextlib import asynccontextmanager
from llm.factory import get_llm_client

from fastapi import FastAPI,Form,File,UploadFile,HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware


from ingestion.pdf_loader import load_pdf
from ingestion.text_loader import load_text
from ingestion.img_loader import load_img
from generation import explainer
from controller import run as run_controller



@asynccontextmanager
async def lifespan(app: FastAPI):

    # 🔥 startup
    explainer.init_semaphore(3)
    app.state.llm_client = None  # ❌ don’t load yet

    yield  # app runs here

    # 🛑 shutdown
    if app.state.llm_client is not None:
        await app.state.llm_client.close()
        print("LLM client closed")
    
app=FastAPI(title="AI Study Assistant",
            description="Analyze text, PDFs, or images and generate study-friendly explanations.",
            version="1.0.0",
            lifespan=lifespan)


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
async def analyze(
    request: Request,
    input_type: str = Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    try:
        if input_type == "text":
            if not content:
                raise HTTPException(status_code=400, detail="Text content is missing")
            text = load_text(content)

        elif input_type in {"pdf", "image"}:
            if not file:
                raise HTTPException(status_code=400, detail="File is missing")

            suffix = os.path.splitext(file.filename)[1] or ".tmp"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(await file.read())
                tmp_path = tmp.name

            try:
                if input_type == "pdf":
                    text = load_pdf(tmp_path)
                else:
                    text = load_img(tmp_path)
            finally:
                os.remove(tmp_path)

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid input_type. Must be one of: text, pdf, image"
            )
        if request.app.state.llm_client is None:
            request.app.state.llm_client = get_llm_client()
        llm_client = request.app.state.llm_client
        result = await run_controller(text, llm_client)
        return result

    except HTTPException:
        raise  

    except Exception as e:

        print("🔥 ANALYZE CRASH:", repr(e))
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )
