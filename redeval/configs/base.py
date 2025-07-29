from dataclasses import dataclass, field
from typing import Dict, Any
from pydantic import BaseModel

@dataclass
class LLMConfig:
    """Configuration for a Language Model."""

    provider: str
    api_key: str = None
    base_url: str = None
    model_kwargs: Dict[str, Any] = field(default_factory=dict)
    sampling_params: Dict[str, Any] = field(default_factory=dict)
    response_format: BaseModel = None


