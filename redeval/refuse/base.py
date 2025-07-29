import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from redeval.llms.base import BaseLLM

class BaseRefuser:
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
