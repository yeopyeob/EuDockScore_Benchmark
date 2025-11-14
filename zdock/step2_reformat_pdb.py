import os
import json

from pathlib import Path
from ..read_pdb import CustomPDB

cwd = Path.cwd()


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def reformat(comp: str, bu: str, m_num: int, ab_chs: str, ag_chs: str):
    if os.path.exists(cwd / bu / comp / f"model_{m_num}.pdb.bak"):
        os.system(
            f"mv {cwd / bu / comp / f'model_{m_num}.pdb.bak'} {cwd / bu / comp / f'model_{m_num}.pdb'}"
        )

    pdb = CustomPDB(cwd / bu / comp / f"model_{m_num}.pdb")
    pdb.write_renum_pdb()
    os.system(
        f"mv {cwd / bu / comp / f'model_{m_num}.pdb'} {cwd / bu / comp / f'model_{m_num}.pdb.bak'}"
    )

    wrts = dict()  # type: ignore
    with open(cwd / bu / comp / f"model_{m_num}_renum.pdb") as f:
        for line in f:
            if not line.startswith("ATOM"):
                continue
            ch = line[21]
            if ch not in wrts:
                wrts[ch] = list()
            wrts[ch].append(line)

    new_wrts = {
        "A": list(),
        "G": list(),
    }  # type: ignore
    max_res_nums = {
        "A": 0,
        "G": 0,
    }
    for ch in ab_chs:
        for i, line in enumerate(wrts[ch]):
            new_res_num = int(line[22:26]) + max_res_nums["A"]
            new_line = line[:21] + "A" + f"{new_res_num:>4d}" + line[26:]
            new_wrts["A"].append(new_line)
            if i == len(wrts[ch]) - 1:
                max_res_nums["A"] = new_res_num
    for ch in ag_chs:
        for i, line in enumerate(wrts[ch]):
            new_res_num = int(line[22:26]) + max_res_nums["G"]
            new_line = line[:21] + "G" + f"{new_res_num:>4d}" + line[26:]
            new_wrts["G"].append(new_line)
            if i == len(wrts[ch]) - 1:
                max_res_nums["G"] = new_res_num

    with open(cwd / bu / comp / f"{comp}_{m_num}.pdb", "w") as fw:
        fw.writelines(new_wrts["A"])
        fw.write("TER\n")
        fw.writelines(new_wrts["G"])


def main():
    test_set = get_comps()
    for bu in ["bound", "unbound"]:
        for c in test_set:
            print(c, bu)
            ag_chs = test_set[c][bu]["Ag"]
            ab_chs = ""
            ab_chs += (
                test_set[c][bu]["H"] if test_set[c][bu]["H"] not in ["#", "@"] else ""
            )
            ab_chs += (
                test_set[c][bu]["L"] if test_set[c][bu]["L"] not in ["#", "@"] else ""
            )
            for idx in range(1, 51):
                reformat(c, bu, idx, ab_chs, ag_chs)


if __name__ == "__main__":
    main()
