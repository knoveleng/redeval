import numpy as np

from typing import List
from redeval.attack.human_jailbreaks.jailbreaks import JAILBREAKS
from redeval.attack.base import BaseRedTeaming

class HumanJailbreaks(BaseRedTeaming):
    def __init__(self, num_subsets: int = 1, random_state: int = 42):
        self.points = []
        self.num_subsets = num_subsets
        self.random_state = random_state
        self.jailbreaks = self.get_jailbreaks()
        
    def get_name(self):
        return "HumanJailbreaks"

    def get_jailbreaks(self):
        if self.num_subsets == -1:
            return JAILBREAKS
        else:
            # Shuffle jailbreaks
            np.random.seed(self.random_state)
            jailbreaks = np.random.permutation(JAILBREAKS)
            return jailbreaks[:self.num_subsets]

    def generate_jailbreak_prompts(self, query: str):

        jailbreak_prompts = [f"{jb}\n\n Query: {query}" for jb in self.jailbreaks]
        
        # Save
        self.points.append({"query": query, "prompts": jailbreak_prompts})
        return jailbreak_prompts
        
    def batch_generate_jailbreak_prompts(self, queries: List[str]):
        batch_jailbreak_prompts = [self.generate_jailbreak_prompts(query) for query in queries]
        
        # Save
        self.points.extend([{"query": query, "prompts": jailbreak_prompts} for query, jailbreak_prompts in zip(queries, batch_jailbreak_prompts)])
        return batch_jailbreak_prompts
        