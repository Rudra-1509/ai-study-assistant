from pathlib import Path

def load_text(source:str) -> str:
    if not isinstance(source,str):
        raise ValueError("Input must be a string.")
    source=source.strip()
    if not source:
        raise ValueError("Input can not be empty.")
    return source
