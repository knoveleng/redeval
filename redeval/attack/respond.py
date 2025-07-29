from typing import List, Dict, Any
from redeval.llms.base import BaseLLM
from redeval.attack.base import BaseResponder

class SimpleResponder(BaseResponder):
    def __init__(self, target_llm: BaseLLM):
        self.target_llm = target_llm
        self.points = []
    
    def generate(self, query: str, sampling_params: Dict[str, Any] = None):
        response = self.target_llm.generate(query, sampling_params)
        self.points.append({"query": query, "prompts": [query], "responses": [response]})
        return response

    def batch_generate(self, queries: List[str], sampling_params: Dict[str, Any] = None):
        responses = self.target_llm.batch_generate(queries, sampling_params)
        self.points.extend([{"query": query, "prompts": [query], "responses": [response]} for query, response in zip(queries, responses)])
        return responses