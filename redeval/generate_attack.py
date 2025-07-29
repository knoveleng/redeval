import yaml
import argparse

from typing import List, Dict, Any
from pathlib import Path
from redeval.switcher import MethodSwitcher
from redeval.utils import load_queries
from redeval.configs.attack import AttackRunner

def parse_arguments():
    """
    Parse command-line arguments for adversarial prompt generation.

    Returns:
        Parsed arguments with configuration for the script
    """
    parser = argparse.ArgumentParser(description="Generate Adversarial Prompts")
    parser.add_argument("--config_path", type=str, default="./recipes/attack/base-open.yml", help="Path to the configuration file")
    parser.add_argument("--num_samples", type=int, default=10, help="Number of samples to generate")
    parser.add_argument("--shuffle", type=bool, default=False, help="Whether to shuffle the data")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for shuffling")
    parser.add_argument("--split", type=str, default="train", help="Dataset split to use")
    parser.add_argument("--field", type=str, default="prompt", help="Field to extract from the dataset")
    return parser.parse_args()

def run(config, num_samples, shuffle, seed, split, field):
    # Log dir
    subdatasets = config.subdatasets
    log_dir = config.log_dir

    for subdataset in subdatasets:
        queries = load_queries(
            config.dataset_id,
            subdataset, 
            num_samples=num_samples, 
            shuffle=shuffle, 
            seed=seed, 
            split=split,
            field=field
        )

        for method, path in zip(config.methods, config.paths):
            if path:
                method_config = yaml.safe_load(open(path))
            else:
                method_config = {}
            
            dir_path = Path(log_dir) / subdataset / method
            method = MethodSwitcher(method, method_config).create_method()
            method.batch_generate_jailbreak_prompts(queries)
            method.save(dir_path)
            print(f"Generated jailbreak prompts for {method.get_name()} on {subdataset}")


if __name__ == "__main__":
    args = parse_arguments()

    # Load config
    config = AttackRunner.load(args.config_path)
    
    run(config, args.num_samples, args.shuffle, args.seed, args.split, args.field)
