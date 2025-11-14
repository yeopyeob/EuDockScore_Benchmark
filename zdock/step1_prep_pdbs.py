import os
import json

from pathlib import Path

cwd = Path.cwd()
zd_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def split_models(comp: str, bu: str):
    if not os.path.exists(cwd / bu / comp):
        os.makedirs(cwd / bu / comp)

    wrts = dict()  # type: ignore
    with open(zd_dir / bu / comp / comp / "model_matched.pdb") as f:
        for line in f:
            if line.startswith("MODEL"):
                model_id = line.split()[1]
                wrts[model_id] = list()
            elif line.startswith("ENDMDL"):
                continue
            elif "UNK" in line:
                continue
            else:
                wrts[model_id].append(line)

    for m_num in wrts.keys():
        with open(cwd / bu / comp / f"model_{m_num}.pdb", "w") as f:
            f.writelines(wrts[m_num])


def main():
    test_set = get_comps()
    for comp in test_set:
        print(f"Processing {comp}...")
        split_models(comp, "bound")
        split_models(comp, "unbound")


if __name__ == "__main__":
    main()
