import os

_llm_client = None


def get_llm_client():
    global _llm_client

    if _llm_client is not None:
        return _llm_client

    provider = os.getenv("LLM_PROVIDER", "cloudflare").lower()

    if provider == "cloudflare":
        from llm.cloudfare import CloudflareLLMClient
        _llm_client = CloudflareLLMClient()

    elif provider == "local":
        from llm.local import LocalLLMClient
        _llm_client = LocalLLMClient()

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    return _llm_client