from dotenv import load_dotenv
load_dotenv()
import tempfile
import os
import time
import traceback
from typing import Optional
from contextlib import asynccontextmanager
from llm.factory import get_llm_client

from fastapi import FastAPI,Form,File,UploadFile,HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from evaluation.benchmark import PipelineTimer

from ingestion.pdf_loader import load_pdf
from ingestion.text_loader import load_text
from ingestion.img_loader import load_img
from generation import explainer



@asynccontextmanager
async def lifespan(app: FastAPI):
    explainer.init_semaphore(3)
    app.state.llm_client = None 

    yield 
    
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
        "https://ai-study-assistant-delta-lake.vercel.app",
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
        timer=PipelineTimer()
        start_time=time.perf_counter()
        with timer.measure("ingestion"):
            print(f">> /analyze received: input_type={input_type}")
            # ensure stdout is flushed quickly in container
            # (PYTHONUNBUFFERED=1 is set in the Dockerfile)
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
            try:
                print(">> initializing LLM client")
                request.app.state.llm_client = get_llm_client()
                print(">> LLM client initialized")
            except Exception as e:
                print("🔥 LLM INIT ERROR:", repr(e))
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"LLM init error: {str(e)}")

        benchmark_mode = request.headers.get("x-benchmark", "false").lower() in {"1", "true", "yes"}
        llm_client = request.app.state.llm_client
        from controller import run as run_controller
        result = await run_controller(
            text,
            llm_client,
            timer=timer,
            start_time=start_time,
            include_metrics=benchmark_mode,
        )
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
