import argparse
import json
import os

from pathlib import Path
from datasets import load_dataset
from redeval.configs.attack import AttackRunner
from redeval.switcher import LLMSwitcher
from redeval.attack.respond import SimpleResponder
from redeval.utils import load_queries



def parse_arguments():
    """
    Parse command-line arguments for adversarial prompt generation.

    Returns:
        Parsed arguments with configuration for the script
    """
    parser = argparse.ArgumentParser(description="Run Attack")
    parser.add_argument("--config_path", type=str, default="./recipes/attack/base-open.yml", help="Path to the configuration file")
    parser.add_argument("--model_name", type=str, default=None, help="Name of the model to use")
    return parser.parse_args()

def run(config):
    print(f"Running attack with target {config.target_llm.model_kwargs['model']}")
    llm = LLMSwitcher(config.target_llm).create_llm()
    attacker = SimpleResponder(llm)

    model_name = config.target_llm.model_kwargs['model']

    # Load logs
    subdatasets = config.subdatasets
    log_dir = config.log_dir
    methods = config.methods
    
    # # Loop through subdatasets
    # for subdataset in subdatasets:
    #     for method in methods:
    #         dir_path = Path(log_dir) / subdataset / method

    #         # Get latest log file
    #         log_files = [f for f in os.listdir(dir_path) if f.endswith(".json")]
    #         latest_log_file = sorted(log_files)[0]
            
    #         # Load logs
    #         points = json.load(open(dir_path / latest_log_file))

    #         print(f"Processing {subdataset} for {method} target {config.target_llm.model_kwargs['model']}")
    #         for i, point in enumerate(points):
    #             responses = attacker.batch_generate(point["prompts"], config.target_llm.sampling_params)
    #             points[i]["responses"] = responses

    #         # Create model directory if it doesn't exist
    #         saving_dir = dir_path / model_name
    #         saving_dir.mkdir(parents=True, exist_ok=True)
            
    #         # Overwrite log file
    #         print(f"Saving responses to {saving_dir / latest_log_file}")
    #         json.dump(points, open(saving_dir / latest_log_file, "w"), indent=4) 

    # Loop through subdatasets
    main_name = model_name.split("/")[-1].lower()
    for subdataset in subdatasets:
        for method in methods:
            dir_path = Path(log_dir) / subdataset / method

            # Get the most recent log file (sorted by timestamp in filename)
            log_files = [f for f in os.listdir(dir_path) if f.endswith(".json") and not os.path.isdir(dir_path / f)]
            if not log_files:
                print(f"No log files found in {dir_path}, skipping...")
                continue
            latest_log_file = sorted(log_files)[-1]  # Most recent by timestamp in filename
            
            # Load logs
            points = json.load(open(dir_path / latest_log_file))

            print(f"Processing {subdataset} for {method} target {config.target_llm.model_kwargs['model']}")
            for i, point in enumerate(points):
                responses = attacker.batch_generate(point["prompts"], config.target_llm.sampling_params)
                points[i]["responses"] = responses

            # Create model directory if it doesn't exist
            saving_dir = dir_path / model_name
            saving_dir.mkdir(parents=True, exist_ok=True)
            
            # Overwrite log file
            print(f"Saving responses to {saving_dir / latest_log_file}")
            json.dump(points, open(saving_dir / latest_log_file, "w"), indent=4)     


if __name__ == "__main__":
    args = parse_arguments()

    # Load config
    config = AttackRunner.load(args.config_path)

    # Update model name if provided
    if args.model_name is not None:
        config.target_llm.model_kwargs["model"] = args.model_name
    
    run(config)
    
    


