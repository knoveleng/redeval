import json
from datetime import datetime
from pathlib import Path

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from redeval.llms import BaseLLM


class BaseRedTeaming(ABC):
    @abstractmethod
    def get_name(self):
        raise NotImplementedError("get_name() must be implemented in a subclass")

    @abstractmethod
    def generate_jailbreak_prompts(self, query: str):
        raise NotImplementedError("generate_jailbreak_prompts() must be implemented in a subclass")
        
    @abstractmethod
    def batch_generate_jailbreak_prompts(self, queries: List[str]):
        raise NotImplementedError("batch_generate_jailbreak_prompts() must be implemented in a subclass")
        
    def save(self, path: str):
        # Create directory if it doesn't exist
        Path(path).mkdir(parents=True, exist_ok=True)
        
        # Get timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.get_name()}_{timestamp}.json"
        
        # Save points
        with open(Path(path) / filename, "w") as f:
            json.dump(self.points, f, indent=4)


class BaseResponder(ABC):
    def __init__(self, target_llm: BaseLLM):
        self.target_llm = target_llm
        self.points = []
    
    def generate(self, query: str, sampling_params: Dict[str, Any] = None):
        raise NotImplementedError("generate() must be implemented in a subclass")
    
    def batch_generate(self, queries: List[str], sampling_params: Dict[str, Any] = None):
        raise NotImplementedError("batch_generate() must be implemented in a subclass")
    
    def save(self, path: str):
        # Create directory if it doesn't exist
        Path(path).mkdir(parents=True, exist_ok=True)
        
        # Get timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.target_llm.get_name()}_{timestamp}.json"
        
        # Save points
        with open(Path(path) / filename, "w") as f:
            json.dump(self.points, f, indent=4)


