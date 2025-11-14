import os
import json

from pathlib import Path
from ..read_pdb import CustomPDB  # masked

cwd = Path.cwd()
af_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def split_models(comp: str):
    if not os.path.exists(cwd / comp):
        os.makedirs(cwd / comp)

    wrts = dict()  # type: ignore
    with open(af_dir / comp / f"{comp}.pdb") as f:
        for line in f:
            if line.startswith("MODEL"):
                model_id = line.split()[1]
                wrts[model_id] = list()
            elif line.startswith("ENDMDL"):
                continue
            else:
                wrts[model_id].append(line)

    for m_num in wrts.keys():
        with open(cwd / comp / f"{comp}_{m_num}.pdb", "w") as f:
            f.writelines(wrts[m_num])
        pdb = CustomPDB(cwd / comp / f"{comp}_{m_num}.pdb")
        pdb.write_renum_pdb()
        os.system(
            f"mv {cwd / comp / f'{comp}_{m_num}_renum.pdb'} {cwd / comp / f'{comp}_{m_num}.pdb'}"
        )


def main():
    test_set = get_comps()
    for comp in test_set:
        print(f"Processing {comp}...")
        split_models(comp)


if __name__ == "__main__":
    main()
