from llm.base import LLMClient
import os
import httpx

class CloudflareLLMClient(LLMClient):
    """
    Clouflare Workers as LLM client
    """

    def __init__(self):
        self.api_token=os.getenv("CLOUDFLARE_API_TOKEN")
        self.account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.model=os.getenv("CLOUDFLARE_MODEL","@cf/meta/llama-3.1-8b-instruct-fp8")

        self.client = httpx.AsyncClient(timeout=60)
        if not self.api_token or not self.account_id:
            raise ValueError("Cloudflare credentials are not set in environment variables")
        
        self.url=(f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}")

        self.headers={
            "Authorization":f"Bearer {self.api_token}",
            "Content-type":"application/json"
        }
    
    async def close(self):
        await self.client.aclose()
    
    async def generate(self,prompt:str,max_tokens:int)->str:
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "parameters": {
                "temperature": 0.6,
                "top_p": 0.9,
                "max_tokens": max_tokens,
                "repetition_penalty": 1.2,
                "stop":["</s>","[INST]","[/INST]","### END"]
            }
        }

        response = await self.client.post(
                url=self.url,
                headers=self.headers,
                json=payload
            )

        response.raise_for_status()
        data=response.json()
        return {
        "text": data["result"]["response"].strip(),
        "usage": data["result"]["usage"]
        }