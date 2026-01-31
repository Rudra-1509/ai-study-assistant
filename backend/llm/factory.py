import os
from llm.local import LocalLLMClient
from llm.cloudfare import CloudflareLLMClient

def get_llm_client():
    """
    Returns an LLM client based on environment configuration.

    Supported providers:
    - local (default)
    - cloudflare
    """
    global _llm_client
    if _llm_client is not None:
        return _llm_client 
    provider=os.getenv("LLM_PROVIDER","local").lower()
    if provider == "cloudflare":
        _llm_client = CloudflareLLMClient()
    else:
        _llm_client = LocalLLMClient()

    return _llm_client
