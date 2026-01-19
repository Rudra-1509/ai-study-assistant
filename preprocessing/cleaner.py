import re
def clean_text(source: str)->str:
    if not isinstance(source,str):
        raise ValueError("Source must be a string")
    #Step1: remove leading and trailing spaces
    source=source.strip()
    if not source:
        raise ValueError("Input string is empty after stripping")
    
    #step2: remove OCR extra line breaks
    source=re.sub(r"/n+","\n",source)

    #step3: remove extra spaces in between
    source=re.sub(r"/s+"," ",source)

    #step4: remove hidden characters
    source = source.replace("\u00a0"," ")

    #step5: lower the whole text
    source=source.lower()
    
    return source