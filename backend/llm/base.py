from abc import ABC,abstractmethod

class LLMClient(ABC):
    """
    Abstract base class for all LLM backends.

    Any LLM implementation used in this project
    MUST implement the generate() method.
    """

    @abstractmethod
    def generate(self,prompt:str)->str:
        """
        Generate text from a prompt.

        Args:
            prompt (str): Input prompt

        Returns:
            str: Generated text
        """
        pass