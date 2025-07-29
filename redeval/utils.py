from datasets import load_dataset
from typing import List




def load_queries(
    dataset_id: str,
    subdataset: str,
    field: str = "prompt",
    num_samples: int = -1,
    shuffle: bool = False,
    seed: int = 0,
    split: str = "train",
) -> List[str]:
    """
    Load JSON dataset with optional sampling and shuffling.

    Args:
        file_path (str): Path to the JSON file
        field (str): Field to extract from the dataset
        num_samples (int, optional): Number of samples to return. Defaults to -1 (all).
        shuffle (bool, optional): Whether to shuffle the data. Defaults to False.
        seed (int, optional): Random seed for shuffling. Defaults to 0.

    Returns:
        List[str]: Extracted and potentially sampled/shuffled data
    """
    data = load_dataset(dataset_id, subdataset, split=split)

    if shuffle:
        data = data.shuffle(seed=seed)

    # Determine number of samples
    sample_count = len(data) if num_samples == -1 else min(num_samples, len(data))

    return data[field][:sample_count]