import json
import subprocess

from pathlib import Path

cwd = Path.cwd()
zd_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def get_command(comp: str, bu: str):
    comp_dir = cwd / bu / comp
    root_dir = comp_dir
    csv_name = comp_dir / "eudockscore_input.csv"
    file_name = comp_dir / f"{comp}_eudockscore_out"
    cmd = "python ../eudockscore/scripts/run_eudockscore_data_ab.py"
    cmd += f" --root_dir {root_dir}"
    cmd += f" --csv_name {csv_name}"
    cmd += f" --file_name {file_name}"
    return cmd


def run_sh(comp: str, bu: str):
    w_file = open(cwd / bu / comp / f"{comp}_eudockscore.sh", "w")

    w_file.write("#!/bin/sh\n")
    w_file.write(f"#SBATCH -J {comp}\n")
    # masked
    w_file.write(f"#SBATCH -o {cwd / bu / comp / f'{comp}_eudockscore.log.q'}\n")

    cmd = get_command(comp, bu)
    w_file.write(cmd + "\n")
    w_file.close()

    subprocess.call(f"sbatch {cwd / bu / comp / f'{comp}_eudockscore.sh'}", shell=True)


def main():
    test_set = get_comps()
    for comp in test_set:
        for bu in ["bound", "unbound"]:
            run_sh(comp, bu)


if __name__ == "__main__":
    main()
