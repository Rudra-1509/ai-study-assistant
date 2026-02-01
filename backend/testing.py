from dotenv import load_dotenv
load_dotenv()

from llm.cloudfare import CloudflareLLMClient

llm = CloudflareLLMClient()
print(llm.generate("Explain BFS in one paragraph."))
