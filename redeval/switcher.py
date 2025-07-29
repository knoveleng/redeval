from typing import Any, Dict, List
from redeval.llms import vLLM, LLMviaOpenAI
from redeval.attack import (
    Direct,
    ZeroShot,
    HumanJailbreaks
)


class LLMSwitcher:
    """Factory class for creating and managing different LLM implementations"""

    def __init__(self, config: Any):
        """
        Initialize LLM switcher with configuration

        Args:
            config: Configuration for the Language Model
        """
        self.provider = config.provider
        self.config = config
        self.model_kwargs = config.model_kwargs

    def create_llm(self):
        """
        Create the appropriate LLM based on configuration

        Returns:
            Instantiated Language Model

        Raises:
            ValueError: If an unsupported LLM type is specified
        """
        if self.provider == "vllm":
            return vLLM(self.model_kwargs)
        elif self.provider == "openai":
            return LLMviaOpenAI(self.config)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    # def generate(self, query: str, sampling_params: Dict[str, Any] = None) -> str:
    #     """
    #     Generate a response using the selected LLM

    #     Args:
    #         query: Input query to generate response for
    #         sampling_params: Optional sampling parameters

    #     Returns:
    #         Generated response
    #     """
    #     if sampling_params is None:
    #         sampling_params = {}
    #     return self._llm.generate(query, sampling_params)

    # def batch_generate(
    #     self, queries: List[str], sampling_params: Dict[str, Any] = None
    # ) -> List[str]:
    #     """
    #     Generate responses for a batch of queries using the selected LLM

    #     Args:
    #         queries: List of input queries
    #         sampling_params: Optional sampling parameters

    #     Returns:
    #         List of generated responses
    #     """
    #     if sampling_params is None:
    #         sampling_params = {}
    #     return self._llm.batch_generate(queries, sampling_params)

    # def generate_format(
    #     self,
    #     query: str,
    #     sampling_params: Dict[str, Any] = None,
    #     response_format: Any = None,
    # ):
    #     return self._llm.generate_format(query, sampling_params, response_format)

    # def batch_generate_format(
    #     self,
    #     queries: List[str],
    #     sampling_params: Dict[str, Any] = None,
    #     response_format: Any = None,
    # ):
    #     return self._llm.batch_generate_format(queries, sampling_params, response_format)

    # def __repr__(self) -> str:
    #     return f"LLMSwitcher(provider={self.provider}, model_kwargs={self.model_kwargs})"


class MethodSwitcher:
    def __init__(self, method: str, config: Any):
        self.method = method
        self.config = config
        
    def create_method(self):
        if self.method == "direct":
            return Direct(**self.config)
        elif self.method == "human_jailbreak":
            return HumanJailbreaks(**self.config)
        elif self.method == "zeroshot":
            return ZeroShot(**self.config)
        else:
            raise ValueError(f"Unsupported method: {self.method}")
            
    def __repr__(self) -> str:
        return f"MethodSwitcher(method={self.method}, config={self.config})"