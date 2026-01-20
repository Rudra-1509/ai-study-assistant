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
    provider=os.getenv("LLM_PROVIDER","local").lower()
    if provider=="cloudflare":
        return CloudflareLLMClient()
    return LocalLLMClient()
