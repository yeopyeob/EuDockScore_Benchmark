import json
import torch
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

cwd = Path.cwd()
zd_dir = Path.home()  # masked
zd_eval_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def get_capri_dockq(lrmsd, irmsd, fnat):
    lrmsd = 1 / (1 + (lrmsd / 8.5) ** 2)
    irmsd = 1 / (1 + (irmsd / 1.5) ** 2)
    dockq = (fnat + lrmsd + irmsd) / 3
    return dockq


def read_eval(comp: str, bu: str):
    dockqs = list()
    with open(zd_eval_dir / bu / comp / comp / f"{comp}.eval.dat") as f:
        for line in f:
            lrmsd, irmsd, fnat = map(float, line.split()[0:3])
            dockqs.append(get_capri_dockq(lrmsd, irmsd, fnat))
    return dockqs


def gather_eu_score(comp: str, bu: str):
    output_fn = cwd / bu / comp / f"{comp}_eudockscore_out"
    scores = list()
    exists = list()
    with open(output_fn) as f:
        for line in f:
            if "File" in line:
                continue
            m_num, score = line.strip().split(",")
            scores.append(float(score))
            exists.append(int(m_num.split("_")[-1][:-4]) - 1)
    return scores, exists


def get_violin_plot(
    dockqs: dict,
    scores: dict,
    fn: str,
    mode: str = "capri",
):
    if mode == "capri":
        energys = {i: list() for i in range(4)}
    elif mode == "dockq_bin":
        energys = {i: list() for i in range(10)}
    elif mode == "near_native":
        energys = {0: list(), 1: list()}

    if mode == "capri":
        crits = [(0, 0.23), (0.23, 0.49), (0.49, 0.8), (0.8, 1 + 1e-5)]
    elif mode == "dockq_bin":
        crits = [(i / 10, (i + 1) / 10) for i in range(10)]
        crits[-1] = (0.9, 1 + 1e-5)
    elif mode == "near_native":
        crits = [(0, 0.23), (0.23, 1 + 1e-5)]

    for comp in dockqs:
        for idx, (c_low, c_high) in enumerate(crits):
            where = np.where(
                (np.array(dockqs[comp]) >= c_low) & (np.array(dockqs[comp]) < c_high)
            )[0]
            t_scores = np.array(scores[comp])[where].tolist()
            energys[idx].extend(t_scores)

    fig, ax = plt.subplots()

    ax.violinplot(
        list(energys.values()),
        positions=list(range(1, len(list(energys.keys())) + 1)),
        showmeans=True,
    )
    ax.set_xticks(list(range(1, len(energys.keys()) + 1)))
    if mode == "capri":
        ax.set_xticklabels(["Incorrect", "Acceptable", "Medium", "High"])
    elif mode == "dockq_bin":
        ax.set_xticklabels([f"{i / 10:.1f}" for i in range(10)])
    elif mode == "near_native":
        ax.set_xticklabels(["Incorrect", "Near native"])
    ax.set_ylabel("Score")

    plt.title(f"Score correlation with {mode}")

    plt.savefig(fn)
    plt.clf()


def get_roc_curve(
    scores: list,
    targets: list,
    fn: str,
    crit: float = 0.23,
):
    targets = torch.tensor(targets)
    targets = torch.where(targets >= crit, 1, 0)
    targets = targets.tolist()

    fpr, tpr, thresholds = roc_curve(
        y_true=targets,
        y_score=scores,
        pos_label=1,
    )
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label="Score ROC curve (area = %0.2f)" % roc_auc)

    plt.plot([0, 1], [0, 1], "r--")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.0])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Receiver Operating Characteristic")
    plt.legend(loc="lower right")
    plt.savefig(fn)
    plt.close()


def main():
    test_set = get_comps()
    all_scores = dict()
    all_dockqs = dict()
    for bu in ["bound", "unbound"]:
        for comp in test_set.keys():
            if not (cwd / bu / comp / f"{comp}_eudockscore_out").exists():
                continue
            all_scores[comp], exists = gather_eu_score(comp, bu)
            all_dockqs[comp] = read_eval(comp, bu)
            all_dockqs[comp] = [all_dockqs[comp][i] for i in exists]

        get_violin_plot(
            scores=all_scores,
            dockqs=all_dockqs,
            mode="near_native",
            fn=f"./step6_near_native_violin_{bu}.png",
        )

        get_violin_plot(
            scores=all_scores,
            dockqs=all_dockqs,
            mode="capri",
            fn=f"./step6_near_native_violin_{bu}.png",
        )

        # get_violin_plot(
        #     scores=all_scores,
        #     dockqs=all_dockqs,
        #     mode="dockq_bin",
        #     fn=f"./step6_dockq_bin_violin_{bu}.png",
        # )

        scores = list()
        for v in all_scores.values():
            scores += v

        targets = list()
        for v in all_dockqs.values():
            targets += v

        get_roc_curve(
            scores=scores,
            targets=targets,
            crit=0.23,
            fn=f"./step6_roc_curve_crit0.23_{bu}.png",
        )
        get_roc_curve(
            scores=scores,
            targets=targets,
            crit=0.49,
            fn=f"./step6_roc_curve_crit0.49_{bu}.png",
        )
        get_roc_curve(
            scores=scores,
            targets=targets,
            crit=0.8,
            fn=f"./step6_roc_curve_crit0.8_{bu}.png",
        )


if __name__ == "__main__":
    main()
