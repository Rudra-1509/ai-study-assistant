def chunk_text(source:str, chunk_lim:int =800)->list[str]:
    if not isinstance(source,str):
        raise ValueError("Input string must be a string")
    source=source.strip()
    if not source:
        raise ValueError("Input text is empty after stripping")
    paragraphs=[p for p in source.split('\n') if p.strip()]
    chunks=[]
    cur_chunk=""
    for p in paragraphs:
        if len(p)>chunk_lim:
            if cur_chunk:
                chunks.append(cur_chunk.strip())
                cur_chunk=""
            chunks.append(p)
        elif len(p)+len(cur_chunk) > chunk_lim:
            chunks.append(cur_chunk)
            cur_chunk=p
        else:
            cur_chunk+=' '+p
    if cur_chunk:
        chunks.append(cur_chunk.strip())
    return chunks
