import argparse

from pathlib import Path
from datasets import load_dataset
from redeval.configs.refuse import RefuseRunner
from redeval.switcher import LLMSwitcher
from redeval.refuse.simple import SimpleRefuser
from redeval.utils import load_queries



def parse_arguments():
    """
    Parse command-line arguments for adversarial prompt generation.

    Returns:
        Parsed arguments with configuration for the script
    """
    parser = argparse.ArgumentParser(description="Run Refuse")
    parser.add_argument("--config_path", type=str, default="./recipes/refuse/base-open.yml", help="Path to the configuration file")
    parser.add_argument("--model_name", type=str, default=None, help="Name of the model to use")
    parser.add_argument("--num_samples", type=int, default=10, help="Number of samples to generate")
    parser.add_argument("--shuffle", type=bool, default=False, help="Whether to shuffle the data")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for shuffling")
    parser.add_argument("--split", type=str, default="train", help="Dataset split to use")
    parser.add_argument("--field", type=str, default="prompt", help="Field to extract from the dataset")
    return parser.parse_args()

def run(config, num_samples, shuffle, seed, split, field):
    llm = LLMSwitcher(config.target_llm).create_llm()
    refuser = SimpleRefuser(llm)

    for subdataset in config.subdatasets:
        for method in config.methods:
            dir_path = Path(config.log_dir) / subdataset / method
            dir_path.mkdir(parents=True, exist_ok=True)

            queries = load_queries(
                config.dataset_id, 
                subdataset, 
                num_samples=num_samples, 
                shuffle=shuffle, 
                seed=seed, 
                split=split,
                field=field
            )
            refuser.batch_generate(queries, config.target_llm.sampling_params)

            # Log dir with subdataset name (use basename to avoid nested dirs from slash in model name)
            model_basename = config.target_llm.model_kwargs["model"].split("/")[-1]
            log_dir = dir_path / model_basename
            refuser.save(log_dir)


if __name__ == "__main__":
    args = parse_arguments()

    # Load config
    config = RefuseRunner.load(args.config_path)

    # Update model name if provided
    if args.model_name is not None:
        config.target_llm.model_kwargs["model"] = args.model_name
    
    run(config, args.num_samples, args.shuffle, args.seed, args.split, args.field)
    
    


