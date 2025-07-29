import argparse

from pathlib import Path
from datasets import load_dataset
from redeval.configs.eval import EvalRunner
from redeval.switcher import LLMSwitcher
from redeval.evaluator import Evaluator


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run Refuse Evaluation")
    parser.add_argument("--config_path", type=str, default="./recipes/refuse/eval.yml", help="Path to the configuration file")
    parser.add_argument("--log_dir", type=str, help="Log directory")
    return parser.parse_args()
    
def run(args):
    config = EvalRunner.load(args.config_path)
    print(config)
    
    judge_llm = LLMSwitcher(config.judge_llm).create_llm()
    evaluator = Evaluator(judge_llm, sampling_params=config.judge_llm.sampling_params, type="refuse")
    
    log_dir = Path(args.log_dir)
    evaluator.evaluate(log_dir, config.keywords)

if __name__ == "__main__":
    args = parse_arguments()
    run(args)
    
    
