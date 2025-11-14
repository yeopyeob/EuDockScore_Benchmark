import os
import json
import atom3d.datasets.datasets as da  # type: ignore

from pathlib import Path
import pandas as pd  # type: ignore
from joblib import Parallel, delayed  # type: ignore

cwd = Path.cwd()
zd_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def per_comp(comp: str, bu: str):
    if not (cwd / "bak" / bu / comp).exists():
        (cwd / "bak" / bu / comp).mkdir(parents=True, exist_ok=True)
    os.system(f"mv {cwd / bu / comp}/model* {cwd / 'bak' / bu / comp}/")

    with open(cwd / bu / comp / "eudockscore_input.csv", "w") as f:
        f.write("File,Label\n")
        for idx in range(1, 51):
            if not (cwd / bu / comp / f"{comp}_{idx}.pdb").exists():
                continue
            f.write(f"{comp}_{idx}.pdb,2\n")

    def add_label(item):
        label_file = f"{cwd / bu / comp}/eudockscore_input.csv"
        item["label"] = pd.read_csv(label_file)["Label"]
        return item

    dataset = da.load_dataset(f"{cwd / bu / comp}/", "pdb", transform=add_label)
    da.make_lmdb_dataset(dataset, f"{cwd / bu / comp}/")


def main():
    test_set = get_comps()
    for bu in ["bound", "unbound"]:
        Parallel(n_jobs=48)(delayed(per_comp)(comp, bu) for comp in test_set)


if __name__ == "__main__":
    main()
