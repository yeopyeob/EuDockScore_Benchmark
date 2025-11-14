import os
import json
import atom3d.datasets.datasets as da  # type: ignore

from pathlib import Path
import pandas as pd  # type: ignore
from joblib import Parallel, delayed  # type: ignore

cwd = Path.cwd()
af_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def per_comp(comp: str):
    if not (cwd / "bak" / comp).exists():
        (cwd / "bak" / comp).mkdir(parents=True, exist_ok=True)
    os.system(f"mv {cwd / comp}/*.pdb.bak {cwd / 'bak' / comp}/")
    os.system(f"mv {cwd / comp}/*.json {cwd / 'bak' / comp}/")

    with open(cwd / comp / "eudockscore_input.csv", "w") as f:
        f.write("File,Label\n")
        for idx in range(1, 101):
            f.write(f"{comp}_{idx}.pdb,2\n")

    def add_label(item):
        label_file = f"{cwd / comp}/eudockscore_input.csv"
        item["label"] = pd.read_csv(label_file)["Label"]
        return item

    dataset = da.load_dataset(f"{cwd / comp}/", "pdb", transform=add_label)
    da.make_lmdb_dataset(dataset, f"{cwd / comp}/")


def main():
    test_set = get_comps()
    Parallel(n_jobs=48)(delayed(per_comp)(comp) for comp in test_set)


if __name__ == "__main__":
    main()
