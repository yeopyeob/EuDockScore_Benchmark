import json
import torch
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

cwd = Path.cwd()
af_eval_dir = Path.home()  # masked


def get_comps():
    with open("test_set.json") as f:  # masked
        test_set = json.load(f)
    return test_set


def read_eval(comp: str):
    with open(af_eval_dir / comp / "sorted_data.json") as f:
        datas = json.load(f)
    return datas["dockq"]


def gather_eu_score(comp: str):
    output_fn = cwd / comp / f"{comp}_eudockscore_out"
    scores = list()
    with open(output_fn) as f:
        for line in f:
            if "File" in line:
                continue
            _, score = line.strip().split(",")
            scores.append(float(score))
    if len(scores) != 100:
        print(comp, len(scores))
    return scores


def get_violin_plot(
    dockqs: dict,
    scores: dict,
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

    plt.savefig(f"./step6_{mode}_violin.png")
    plt.clf()


def get_roc_curve(
    scores: list,
    targets: list,
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
    plt.savefig(f"step6_roc_curve_crit{crit}.png")
    plt.close()


def main():
    test_set = get_comps()
    all_scores = dict()
    all_dockqs = dict()
    for comp in test_set.keys():
        all_scores[comp] = gather_eu_score(comp)
        all_dockqs[comp] = read_eval(comp)

    get_violin_plot(
        scores=all_scores,
        dockqs=all_dockqs,
        mode="near_native",
    )

    get_violin_plot(
        scores=all_scores,
        dockqs=all_dockqs,
        mode="capri",
    )

    get_violin_plot(
        scores=all_scores,
        dockqs=all_dockqs,
        mode="dockq_bin",
    )

    scores = list()
    for v in all_scores.values():
        scores += v

    targets = list()
    for v in all_dockqs.values():
        targets += v

    get_roc_curve(scores=scores, targets=targets, crit=0.23)
    get_roc_curve(scores=scores, targets=targets, crit=0.49)
    get_roc_curve(scores=scores, targets=targets, crit=0.8)


if __name__ == "__main__":
    main()
