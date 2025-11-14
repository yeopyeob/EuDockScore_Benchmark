import json
import numpy as np

from pathlib import Path
from ..read_pdb import CustomPDB, Structure, CA_IDX  # masked

cwd = Path.cwd()
af_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def get_info(comp: str, m_num: int, ab_chs: str, ag_chs: str):
    pdb = CustomPDB(cwd / comp / f"{comp}_{m_num}.pdb")
    struc: Structure = pdb.pdb_infos[0]

    coords = {"ab": list(), "ag": list()}
    chains = {"ab": list(), "ag": list()}
    for ch in ab_chs:
        coords["ab"].append(struc.coord[ch])
        chains["ab"] += [ch] * len(struc.coord[ch])
    for ch in ag_chs:
        coords["ag"].append(struc.coord[ch])
        chains["ag"] += [ch] * len(struc.coord[ch])

    for abag in coords:
        coords[abag] = np.concatenate(coords[abag])
        coords[abag] = coords[abag][coords[abag][:, :, 3] == CA_IDX][:, :3]

    return coords, chains


def get_iface(coords, chains):
    dist = np.sqrt(
        np.sum((coords["ab"][:, None, :] - coords["ag"][None, :, :]) ** 2, axis=-1)
    )

    iface_r = np.min(dist, axis=1) < 10
    iface_l = np.min(dist, axis=0) < 10

    iface_ab = [chains["ab"][i] for i in np.where(iface_r)[0]]
    iface_ag = [chains["ag"][i] for i in np.where(iface_l)[0]]
    max_num, max_ch = 0, ""
    for ch in set(iface_ag):
        count = iface_ag.count(ch)
        if count > max_num:
            max_num = count
            max_ch = ch

    return set(iface_ab + [max_ch])


def main():
    test_set = get_comps()
    out: dict[str, dict] = dict()  # type: ignore
    for comp in test_set:
        out[comp]: dict[str, dict] = dict()  # type: ignore
        for m_num in range(1, 101):
            out[comp][m_num] = {
                "Ab": list(),
                "Ag": list(),
            }
            ag_chs = test_set[comp]["Ag"]
            ab_chs = ""
            ab_chs += (
                test_set[comp]["H"] if test_set[comp]["H"] not in ["@", "#"] else ""
            )
            ab_chs += (
                test_set[comp]["L"] if test_set[comp]["L"] not in ["@", "#"] else ""
            )
            coords, chains = get_info(comp, m_num, ab_chs, ag_chs)
            iface = get_iface(coords, chains)
            for ch in iface:
                if ch in ab_chs and ch in test_set[comp]["H"]:
                    out[comp][m_num]["Ab"].append(ch)
                elif ch in ag_chs:
                    out[comp][m_num]["Ag"].append(ch)
    with open(cwd / "step2_valid_chains.json", "w") as f:
        json.dump(out, f, indent=4)


if __name__ == "__main__":
    main()
