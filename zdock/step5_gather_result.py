import json

from pathlib import Path

cwd = Path.cwd()
zd_dir = Path.home()  # masked
zd_eval_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def eval_fnat(fnat):
    if fnat >= 0.5:
        return "high"
    elif fnat >= 0.3:
        return "medium"
    elif fnat >= 0.1:
        return "acceptable"
    elif fnat < 0.1:
        return "incorrect"


def eval_lrmsd(lrmsd):
    if lrmsd <= 1.0:
        return "high"
    elif lrmsd <= 5.0:
        return "medium"
    elif lrmsd <= 10.0:
        return "acceptable"
    elif lrmsd > 10.0:
        return "incorrect"


def eval_irmsd(irmsd):
    if irmsd <= 1.0:
        return "high"
    elif irmsd <= 2.0:
        return "medium"
    elif irmsd <= 4.0:
        return "acceptable"
    elif irmsd > 4.0:
        return "incorrect"


def get_capri_dockq(lrmsd, irmsd, fnat):
    lrmsd = 1 / (1 + (lrmsd / 8.5) ** 2)
    irmsd = 1 / (1 + (irmsd / 1.5) ** 2)
    dockq = (fnat + lrmsd + irmsd) / 3
    return dockq


def get_capri_capri(lrmsd, irmsd, fnat):
    capri2int = {
        "high": 3,
        "medium": 2,
        "acceptable": 1,
        "incorrect": 0,
    }
    lrmsd_num = capri2int[eval_lrmsd(lrmsd)]
    irmsd_num = capri2int[eval_irmsd(irmsd)]
    fnat_num = capri2int[eval_fnat(fnat)]
    return min(lrmsd_num, irmsd_num, fnat_num)


def read_eval(comp: str, bu: str):
    dockqs = list()
    capris = list()
    with open(zd_eval_dir / bu / comp / comp / f"{comp}.eval.dat") as f:
        for line in f:
            lrmsd, irmsd, fnat = map(float, line.split()[0:3])
            dockqs.append(get_capri_dockq(lrmsd, irmsd, fnat))
            capris.append(get_capri_capri(lrmsd, irmsd, fnat))

    return capris, dockqs


def gather_eu_score(comp: str, bu: str):
    output_fn = cwd / bu / comp / f"{comp}_eudockscore_out"
    scores = dict()
    with open(output_fn) as f:
        for line in f:
            if "File" in line:
                continue
            pdb, score = line.strip().split(",")
            m_num = pdb.split("_")[-1].replace(".pdb", "")
            scores[m_num] = float(score)
    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    return sorted_scores


def get_rescored(eu_scores, evals):
    rescored = list()
    for m_num in eu_scores.keys():
        rescored.append(evals[int(m_num) - 1])
    return rescored


def fresh_success_log():
    return {
        "suc": [0, 0, 0, 0, 0],
        "acc": [0, 0, 0, 0, 0],
        "med": [0, 0, 0, 0, 0],
        "high": [0, 0, 0, 0, 0],
    }


def main():
    test_set = get_comps()

    out = {
        "bound": {"dockq": fresh_success_log(), "capri": fresh_success_log()},
        "unbound": {"dockq": fresh_success_log(), "capri": fresh_success_log()},
    }
    wrts = list()
    num_comps = {
        "bound": 0,
        "unbound": 0,
    }
    for comp in test_set.keys():
        for bu in out.keys():
            if not (cwd / bu / comp / f"{comp}_eudockscore_out").exists():
                num_comps[bu] += 1
                wrts.append(f"{comp} {bu} not runned yet.\n")
                continue

            capris, dockqs = read_eval(comp, bu)
            eu_score_out = gather_eu_score(comp, bu)
            if len(eu_score_out) == 0:
                num_comps[bu] += 1
                wrts.append(f"{comp} {bu} did not run successfully.\n")
                continue

            num_comps[bu] += 1
            rescored_capris = get_rescored(eu_score_out, capris)
            rescored_dockqs = get_rescored(eu_score_out, dockqs)

            for i, v in enumerate([1, 5, 10, 30, 50]):
                max_capri = max(rescored_capris[:v])
                max_dockq = max(rescored_dockqs[:v])

                if max_capri == 3:
                    out[bu]["capri"]["suc"][i] += 1
                    out[bu]["capri"]["high"][i] += 1
                elif max_capri == 2:
                    out[bu]["capri"]["suc"][i] += 1
                    out[bu]["capri"]["med"][i] += 1
                elif max_capri == 1:
                    out[bu]["capri"]["suc"][i] += 1
                    out[bu]["capri"]["acc"][i] += 1

                if max_dockq >= 0.8:
                    out[bu]["dockq"]["suc"][i] += 1
                    out[bu]["dockq"]["high"][i] += 1
                elif max_dockq >= 0.49:
                    out[bu]["dockq"]["suc"][i] += 1
                    out[bu]["dockq"]["med"][i] += 1
                elif max_dockq >= 0.23:
                    out[bu]["dockq"]["suc"][i] += 1
                    out[bu]["dockq"]["acc"][i] += 1

    for bu in out.keys():
        wrts.append(f"==== {bu} ====\n")
        for score_type in out[bu].keys():
            wrts.append(f"---- {score_type} ----\n")
            for i, v in enumerate([1, 5, 10, 30, 50]):
                wrts.append(f"Top {v}:\n")
                wrts.append(
                    f"Success Rate : {out[bu][score_type]['suc'][i] / num_comps[bu]}\n"
                )
                wrts.append(
                    f"High : {out[bu][score_type]['high'][i] / num_comps[bu]}\n"
                )
                wrts.append(
                    f"Medium : {out[bu][score_type]['med'][i] / num_comps[bu]}\n"
                )
                wrts.append(
                    f"Acceptable : {out[bu][score_type]['acc'][i] / num_comps[bu]}\n"
                )

    with open("step5_result", "w") as f:
        f.writelines(wrts)


if __name__ == "__main__":
    main()
