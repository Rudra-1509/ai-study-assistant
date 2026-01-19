import pytesseract
from PIL import Image
from pathlib import Path

def load_img(source: str)->str:
    if not isinstance(source,str):
            raise ValueError("Input must be a string.")
    source=source.strip()
    if not source:
            raise ValueError("Source can not be empty.")
    path=Path(source)
    if path.exists():
        ext=path.suffix.lower()
        if ext not in ('.png', '.jpg', '.jpeg'):
            raise ValueError("Ony txt, pdf and jpg files are allowed")
    text=""
    try:
        img=Image.open(path).convert("L")
        custom_config=r'--oem 3 --psm 6'
        text=pytesseract.image_to_string(img,lang="eng",config=custom_config)
    except Exception as e:
        raise ValueError(f"Failed to read pdf file:{e}")
    return text
    