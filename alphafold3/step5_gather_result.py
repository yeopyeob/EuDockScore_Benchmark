import json
from pathlib import Path

cwd = Path.cwd()
af_eval_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def read_eval(comp: str):
    with open(af_eval_dir / comp / "sorted_data.json") as f:
        datas = json.load(f)
    return datas["capri"], datas["dockq"]


def gather_eu_score(comp: str):
    output_fn = cwd / comp / f"{comp}_eudockscore_out"
    scores = dict()
    with open(output_fn) as f:
        for line in f:
            if "File" in line:
                continue
            pdb, score = line.strip().split(",")
            m_num = pdb.split("_")[-1].strip().replace(".pdb", "")
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
        "suc": [0, 0, 0, 0, 0, 0],
        "acc": [0, 0, 0, 0, 0, 0],
        "med": [0, 0, 0, 0, 0, 0],
        "high": [0, 0, 0, 0, 0, 0],
    }


def main():
    test_set = get_comps()

    out = {"dockq": fresh_success_log(), "capri": fresh_success_log()}

    wrts = list()
    num_comp = 0
    for comp in test_set.keys():
        print(comp)
        if not (cwd / comp / f"{comp}_eudockscore_out").exists():
            wrts.append(f"{comp} not runned yet.\n")
            continue
        capris, dockqs = read_eval(comp)
        eu_score_out = gather_eu_score(comp)
        if len(eu_score_out) == 0:
            wrts.append(f"{comp} did not run successfully.\n")
            continue

        num_comp += 1
        rescored_capris = get_rescored(eu_score_out, capris)
        rescored_dockqs = get_rescored(eu_score_out, dockqs)

        for i, v in enumerate([1, 5, 10, 30, 50, 100]):
            max_capri = max(rescored_capris[:v])
            max_dockq = max(rescored_dockqs[:v])

            if max_capri == 3:
                out["capri"]["suc"][i] += 1
                out["capri"]["high"][i] += 1
            elif max_capri == 2:
                out["capri"]["suc"][i] += 1
                out["capri"]["med"][i] += 1
            elif max_capri == 1:
                out["capri"]["suc"][i] += 1
                out["capri"]["acc"][i] += 1

            if max_dockq >= 0.8:
                out["dockq"]["suc"][i] += 1
                out["dockq"]["high"][i] += 1
            elif max_dockq >= 0.49:
                out["dockq"]["suc"][i] += 1
                out["dockq"]["med"][i] += 1
            elif max_dockq >= 0.23:
                out["dockq"]["suc"][i] += 1
                out["dockq"]["acc"][i] += 1

    for score_type in out.keys():
        wrts.append(f"---- {score_type}: {num_comp} ----\n")
        for i, v in enumerate([1, 5, 10, 30, 50, 100]):
            wrts.append(f"Top {v}:\n")
            wrts.append(f"Success Rate : {out[score_type]['suc'][i] / num_comp}\n")
            wrts.append(f"High : {out[score_type]['high'][i] / num_comp}\n")
            wrts.append(f"Medium : {out[score_type]['med'][i] / num_comp}\n")
            wrts.append(f"Acceptable : {out[score_type]['acc'][i] / num_comp}\n")

    with open("step5_result", "w") as f:
        f.writelines(wrts)


if __name__ == "__main__":
    main()
