from llm.base import LLMClient
import os
import requests

class CloudflareLLMClient(LLMClient):
    """
    Clouflare Workers as LLM client
    """

    def __init__(self):
        self.api_token=os.getenv("CLOUDFLARE_API_TOKEN")
        self.account_id=os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.model=os.getenv("CLOUDFLARE_MODEL","@cf/meta/llama-3-8b-instruct")

        if not self.api_token or not self.account_id:
            raise ValueError("Cloudflare credentials are not set in environment variables")
        
        self.url=(f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}")

        self.headers={
            "Authorization":f"Bearer {self.api_token}",
            "Content-type":"application/json"
        }
    
    def generate(self,prompt:str)->str:
        json={
            "messages":[
                {"role":"user","content":prompt}
            ],
            "parameters": {
                "temperature": 0.5,
                "top_p": 0.9,
                "max_tokens": 400,
                "repetation_penalty":1.1
            }
        }

        response=requests.post(url=self.url,headers=self.headers,json=json,timeout=60)

        response.raise_for_status()
        data=response.json()

        return data["result"]["response"].strip()