from typing import List
from redeval.attack.base import BaseRedTeaming

class Direct(BaseRedTeaming):
    def __init__(self, **kwargs):
        self.points = []
        self.kwargs = kwargs
        
    def get_name(self):
        return "Direct"
    
    def generate_jailbreak_prompts(self, query: str):
        jailbreak_prompt = query
        
        # Save
        self.points.append({"query": query, "prompts": [jailbreak_prompt]})
        return jailbreak_prompt
        
    def batch_generate_jailbreak_prompts(self, queries: List[str]):
        jailbreak_prompts = queries

        # Save
        self.points.extend([{"query": query, "prompts": [jailbreak_prompt]} for query, jailbreak_prompt in zip(queries, jailbreak_prompts)])
        return jailbreak_prompts
            
