import sys 
import os
import json
import yaml
import logging

from redeval.configs.base import LLMConfig
from typing import List
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


@dataclass
class EvalConfig:
    subdatasets: List[str]
    log_dir: str
    judge_llm: LLMConfig
    keywords: List[str]


class EvalRunner:
    @staticmethod
    def load(config_path: str) -> EvalConfig:
        try:
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return EvalConfig(
                subdatasets=config["subdatasets"],
                log_dir=config["log_dir"],
                judge_llm=LLMConfig(**config["judge_llm"]),
                keywords=config["keywords"],
            )
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise


if __name__ == "__main__":
    config_path = "./recipes/attack/eval.yml"
    config = EvalRefuseRunner.load(config_path)
    print(config)
        