from abc import ABC, abstractmethod
from typing import List


class BaseLLM(ABC):
    @abstractmethod
    def get_name(self):
        raise NotImplementedError("get_name() must be implemented in a subclass")

    @abstractmethod
    def generate(self, query: str):
        raise NotImplementedError("generate() must be implemented in a subclass")

    @abstractmethod
    def batch_generate(self, queries: List[str]):
        raise NotImplementedError("batch_generate() must be implemented in a subclass")
    
