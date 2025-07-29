import sys
import logging  

from typing import List
from pydantic import BaseModel
from vllm import LLM, SamplingParams
from vllm.sampling_params import GuidedDecodingParams

from redeval.llms.base import BaseLLM


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

class vLLM(BaseLLM):
    def __init__(self, model_kwargs: dict):
        self.model_kwargs = model_kwargs
        self.llm = LLM(**model_kwargs)

    def get_name(self):
        return self.model_kwargs["model"].split("/")[-1]

    def generate(self, query: str, sampling_params: dict):
        try:
            outputs = self.llm.generate([query], SamplingParams(**sampling_params))
            response = outputs[0].outputs[0].text
            return response
        except Exception as e:
            logger.error(f"Error in generate: {e}")
            return ""

    def batch_generate(self, queries: List[str], sampling_params: dict):
        outputs = self.llm.generate(queries, SamplingParams(**sampling_params))
        return [output.outputs[0].text for output in outputs]

    def generate_format(
        self, query: str, 
        sampling_params: dict, 
        response_format: BaseModel
    ):
        try:
            schema = response_format.model_json_schema()
            guided_decoding_params = GuidedDecodingParams(json=schema)
            outputs = self.llm.generate([query], SamplingParams(**sampling_params, guided_decoding_params=guided_decoding_params))
            response = outputs[0].outputs[0].text
            return response
        except Exception as e:
            logger.error(f"Error in generate_format: {e}")
            return ""

    def batch_generate_format(
        self, queries: List[str], sampling_params: dict, response_format: BaseModel
    ):
        schema = response_format.model_json_schema()
        guided_decoding_params = GuidedDecodingParams(json=schema)
        outputs = self.llm.generate(queries, SamplingParams(**sampling_params, guided_decoding_params=guided_decoding_params))
        return [output.outputs[0].text for output in outputs]
        
        
