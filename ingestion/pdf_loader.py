import fitz
import pytesseract
from PIL import Image
import io
from pathlib import Path

def load_pdf(source:str)->str:
    if not isinstance(source,str):
        raise ValueError("Input must be a string.")
    source=source.strip()
    if not source:
        raise ValueError("Source can not be empty.")
    path=Path(source)
    if path.exists():
        if path.suffix.lower()!='.pdf':
            raise ValueError("Ony txt, pdf and jpg files are allowed")
    output_text=[]
    try:
        with fitz.open(path) as doc:
            for page in doc:
                text=page.get_text("text").strip()
                if len(text)<30:
                    pix=page.get_pixmap(dpi=300)
                    img=Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")

                    custom_config=r'--oem 3 --psm 6'
                    text=pytesseract.image_to_string(img,lang="eng",config=custom_config)
                    output_text.append(text)
                else:
                    output_text.append(text)
        output_text="\n".join(output_text)
    except Exception as e:
        raise ValueError(f"Failed to read pdf file:{e}")
    return output_text
            
