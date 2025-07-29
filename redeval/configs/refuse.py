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
class RefuseConfig:
    dataset_id: str
    subdatasets: List[str]
    log_dir: str
    methods: List[str]
    paths: List[str]
    target_llm: LLMConfig


class RefuseRunner:
    @staticmethod
    def load(config_path: str) -> RefuseConfig:
        try:
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            
            return RefuseConfig(
                dataset_id=config["dataset_id"],
                subdatasets=config["subdatasets"],
                log_dir=config["log_dir"],
                methods=config["methods"],
                paths=config["paths"],
                target_llm=LLMConfig(**config["target_llm"]),
            )
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise


if __name__ == "__main__":
    config_path = "./recipes/refuse/base-open.yml"
    config = RefuseRunner.load(config_path)
    print(config)

        