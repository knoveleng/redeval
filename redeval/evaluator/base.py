import os
import sys
import json
import logging
from typing import List, Dict, Any, Union, Optional
from pathlib import Path

from redeval.llms.base import BaseLLM
from redeval.evaluator.prompts import EVALUATE_ATTACK_TEMPLATE, EVALUATE_REFUSE_TEMPLATE

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class Evaluator:
    """
    Evaluator class for assessing model responses to prompts.
    
    This class handles the evaluation of model responses for both attack and refuse scenarios.
    It loads data from log files, processes them through a language model, and saves the evaluation results.
    """
    
    def __init__(
        self, 
        llm: BaseLLM,
        sampling_params: Optional[Dict[str, Any]] = None,
        type: str = "attack",  # Using string literal instead of Union type in default
        template: Optional[str] = None,
    ):
        """
        Initialize the Evaluator.
        
        Args:
            llm: The language model to use for evaluation
            sampling_params: Optional sampling parameters for the language model
            type: The type of evaluation ('attack' or 'refuse')
            template: Custom evaluation template (optional)
        
        Raises:
            ValueError: If an invalid evaluation type is provided
        """
        self.llm = llm
        self.sampling_params = sampling_params
        
        # Validate evaluation type
        if type not in ["attack", "refuse"]:
            raise ValueError(f"Invalid evaluation type: {type}. Must be 'attack' or 'refuse'.")
        self.type = type
        
        # Set template based on evaluation type or use custom template
        if template is None:
            if type == "attack":
                self.template = EVALUATE_ATTACK_TEMPLATE
            else:  # type == "refuse"
                self.template = EVALUATE_REFUSE_TEMPLATE
        else:
            self.template = template

    def evaluate(self, log_dir: str, keywords: List[str], exclude=["eval", "metric"]) -> None:
        """
        Evaluate model responses from log files.
        
        Args:
            log_dir: Directory containing log files to evaluate
            keywords: List of keys to extract from the data points [prompt_key, response_key]
            exclude: List of file names starting with 'eval_' to exclude from evaluation
        
        Raises:
            FileNotFoundError: If log directory doesn't exist
            ValueError: If keywords list doesn't contain exactly 2 elements
        """
        # Validate inputs
        log_path = Path(log_dir)
        if not log_path.exists():
            raise FileNotFoundError(f"Log directory not found: {log_dir}")
        
        if len(keywords) != 2:
            raise ValueError(f"Expected 2 keywords [prompt_key, response_key], got {len(keywords)}")
        
        prompt_key, response_key = keywords
        
        # Get all JSON log files
        files = [f for f in os.listdir(log_dir) if f.endswith(".json") and not any(excluded in f for excluded in exclude)]
        if not files:
            logger.warning(f"No JSON files found in {log_dir}")
            return
        
        # Process each log file
        for filename in files:
            file_path = log_path / filename
            try:
                with open(file_path, 'r') as f:
                    points = json.load(f)
                
                if not points:
                    logger.warning(f"Empty data in {filename}, skipping")
                    continue
                
                # Process each data point
                for idx, point in enumerate(points):
                    # Extract prompts and responses using the provided keywords
                    try:
                        prompts = point.get(prompt_key, [])
                        responses = point.get(response_key, [])

                        
                        if not prompts or not responses or len(prompts) != len(responses):
                            logger.warning(f"Invalid data format in point {idx} of {filename}, skipping")
                            continue
                        
                        # Prepare evaluation queries
                        queries = [
                            self.template.format(prompt=prompt, response=response) 
                            for prompt, response in zip(prompts, responses)
                        ]
                        
                        # Generate evaluation responses
                        evaluation_results = self.llm.batch_generate(queries, self.sampling_params)
                        
                        # Update data point with evaluation results
                        points[idx]["judges"] = evaluation_results

                        
                    except Exception as e:
                        logger.error(f"Error processing point {idx} in {filename}: {e}")
                
                # Save evaluation results
                eval_filename = f"eval_{filename}"
                with open(log_path / eval_filename, "w") as f:
                    json.dump(points, f, indent=4)
                
                logger.info(f"Evaluated {filename} and saved to {eval_filename}")
                
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")