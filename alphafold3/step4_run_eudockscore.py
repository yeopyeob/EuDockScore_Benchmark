import json
import subprocess

from pathlib import Path

cwd = Path.cwd()
af_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def get_command(comp: str):
    comp_dir = cwd / comp
    root_dir = comp_dir
    csv_name = comp_dir / "eudockscore_input.csv"
    file_name = comp_dir / f"{comp}_eudockscore_out"
    cmd = "python ../eudockscore/scripts/run_eudockscore_data_afscores.py"
    cmd += f" --root_dir {root_dir}"
    cmd += f" --csv_name {csv_name}"
    cmd += f" --file_name {file_name}"
    return cmd


def run_sh(comp: str):
    w_file = open(cwd / comp / f"{comp}_eudockscore.sh", "w")

    w_file.write("#!/bin/sh\n")
    w_file.write(f"#SBATCH -J {comp}\n")
    # masked
    w_file.write(f"#SBATCH -o {cwd / comp / comp}_eudockscore.log.q\n")

    cmd = get_command(comp)
    w_file.write(cmd + "\n")
    w_file.close()

    subprocess.call(f"sbatch {cwd / comp / f'{comp}_eudockscore.sh'}", shell=True)


def main():
    test_set = get_comps()
    for comp in test_set:
        run_sh(comp)


if __name__ == "__main__":
    main()
