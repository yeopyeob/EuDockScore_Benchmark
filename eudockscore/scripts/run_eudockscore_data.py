"""Score a directory of PDBs with BERTScore"""

import argparse
from eudockscore.equiformer_v2_resi.model_v2_new import EuBERT
from torch_geometric.loader import DataLoader

from transformers import BertTokenizer
import torch
import torch.nn as nn
import os
import pandas as pd
from atom3d.datasets import LMDBDataset
from eudockscore.equiformer_v2_resi.data_new import EDN_Transform
import subprocess
import traceback
import pickle

# Silence tokenizer warnings
import logging
import warnings

logging.disable(logging.WARNING)
warnings.filterwarnings("ignore", category=DeprecationWarning)

VALID_AA = [
    "A",
    "R",
    "N",
    "D",
    "C",
    "Q",
    "E",
    "G",
    "H",
    "I",
    "L",
    "K",
    "M",
    "F",
    "P",
    "S",
    "T",
    "W",
    "Y",
    "V",
]

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
score_model = EuBERT().to(DEVICE)

# Load weights
score_model.load_state_dict(
    torch.load(
        "/home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/eudockscore/weights/eudockscore/weights.pth",
        map_location=DEVICE,
    )["model_state_dict"]
)
score_model.eval()  # Set in eval mode


def score_dir(root_dir: str, file_name: str, csv_name: str) -> pd.DataFrame:
    # Sigmoid
    softmax = nn.Softmax(dim=-1)

    # Load the data
    if not os.path.isfile(csv_name.replace(".csv", ".pkl")):
        ds = LMDBDataset(
            root_dir,
            transform=EDN_Transform(
                True,
                csv_file=csv_name,
                nlp_model="/home/dnduq97/Benchmark/tdrerank/scoring/eudockscore/eudockscore/weights/pretrained",
            ),
        )
        score_data = []
        model_input_data = {pdb["id"]: pdb for pdb in ds}
        with open(csv_name.replace(".csv", ".pkl"), "wb") as f:
            pickle.dump(model_input_data, f)
    else:
        with open(csv_name.replace(".csv", ".pkl"), "rb") as f:
            model_input_data = pickle.load(f)
            score_data = []

    for index, row in pd.read_csv(csv_name).iterrows():
        try:
            pdb_file_name = row["File"]
            model_input = model_input_data[pdb_file_name]
            data_list = [model_input]
            loader = DataLoader(data_list, batch_size=1)
            batch = next(iter(loader))

            with torch.no_grad():
                model_outputs = score_model(batch.to(DEVICE))
                model_outputs = softmax(model_outputs)
                score = model_outputs.flatten()[-1]  # Get score positive
                score = score.item()
            # Store the score
            score_data.append([pdb_file_name, score])
        except:
            traceback.print_exc()
            continue

    df = pd.DataFrame.from_records(score_data, columns=["File", "Score"])
    df.to_csv(file_name, index=False)

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--root_dir",
        dest="root_dir",
        type=str,
        required=True,
        help="The path to the LMDB file.",
    )
    parser.add_argument(
        "--csv_name",
        dest="csv_name",
        type=str,
        required=True,
        help="The path to the csv of pairs to be scored. Format File, Label. The label can be real labels or dummy values.",
    )
    parser.add_argument(
        "--file_name",
        dest="file_name",
        type=str,
        required=True,
        help="The name to save the results under.",
    )
    args = parser.parse_args()
    root_dir = args.root_dir
    file_name = args.file_name
    csv_name = args.csv_name

    df_results = score_dir(root_dir, file_name, csv_name)
