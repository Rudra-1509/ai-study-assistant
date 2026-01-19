from pathlib import Path

def load_text(source:str) -> str:
    if not isinstance(source,str):
        raise ValueError("Input must be a string.")
    source=source.strip()
    if not source:
        raise ValueError("Source can not be empty.")
    path=Path(source)
    if path.exists():
        if path.suffix.lower()!='.txt':
            raise ValueError("Ony txt, pdf and jpg files are allowed")
        try:
            with open(path,"r",encoding="utf-8") as file:
                text=file.read().strip()
                if not text:
                    raise ValueError("File is empty")
                return text
        except Exception as e:
            raise ValueError(f"Failed to read text file:{e}")
    else:
        return source
