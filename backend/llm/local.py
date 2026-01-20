from ctransformers import AutoModelForCausalLM
from backend.llm.base import LLMClient

DEFAULT_MODEL_DIR = "models/mistral"
DEFAULT_MODEL_FILE = "Mistral-7B-Instruct-v0.3.Q4_K_M.gguf"

class LocalLLMClient(LLMClient):
    """
    Local GGUF-based LLM implementation using ctransformers.
    """
    def __init__(self,model_dir: str=DEFAULT_MODEL_DIR,model_file: str=DEFAULT_MODEL_FILE,model_type: str = "mistral",context_length: int = 2048,threads: int = 8):

        self.model_dir = model_dir
        self.model_file = model_file

        self.llm = AutoModelForCausalLM.from_pretrained(model_dir,model_file=model_file,model_type=model_type,context_length=context_length,threads=threads)
    def generate(self, prompt: str) -> str:
        """
        Generate text from a prompt using the local model.
        """

        text = self.llm(prompt,max_new_tokens=300,temperature=0.5,top_p=0.9,stop=["### END"],repetition_penalty=1.15)

        # Some GGUF models echo the prompt
        if isinstance(text, str) and text.startswith(prompt):
            text = text[len(prompt):]

        return text.strip()