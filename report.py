import json
from collections import defaultdict, namedtuple
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sn
import pandas as pd

from config import DOMAIN, DOTFILE_PATH, DENYLIST


Measure = namedtuple("Measure", ["label", "color"])

MEASURES = {
    "noc": Measure("NOC", "limegreen"),
    "ca": Measure("Ca", "purple"),
    "ce": Measure("Ce", "teal"),
    "instability": Measure("Instability", "deeppink"),
    "dcm_lcom3": Measure("DCM (LCOM3)", "black"),
    "dcm_sim": Measure("DCM (SIM)", "darkorange"),
    "dcm_cc": Measure("DCM (CC)", "blue"),
    "p-depdegree": Measure("P-DepDegree", "red"),
    "dlm": Measure("DLM", "gold"),
}

DEPGRAPH = json.load(open("./data/depgraph.json"))
DATA = {m: json.load(open(f"./data/{m}.json")) for m in MEASURES}


def plot_measurement_values(m: str):
    """
    Plots the sorted measurement values for measure m
    and stores the graph under ./graphs/<m>.png
    """

    data = DATA[m]
    label, color = MEASURES[m]

    xvalues = [i for i in range(len(data))]
    # Plot graphs
    plt.plot(
        xvalues,
        [y for _, y in sorted(data.items(), key=lambda i: i[1])],
        "o",
        label=label,
        color=color,
        markersize=1,
    )
    plt.legend()
    plt.ylabel("measurement values")
    plt.xlabel("packages")

    # plt.show()
    plt.savefig(f"./graphs/{m}.png")
    plt.close()


def plot_comparison(m1: str, m2: str):
    """
    Plots the sorted measurement values for measure m1
    and the corresponding measurement values for m2
    and stores the graph under ./graphs/<m1>_and_<m2>.png
    """
    data_m1 = DATA[m1]
    label_m1, color_m1 = MEASURES[m1]

    data_m2 = DATA[m2]
    label_m2, color_m2 = MEASURES[m2]

    xvalues = [i for i in range(len(data_m1))]
    # Plot graphs
    plt.plot(
        xvalues,
        [y for _, y in sorted(data_m1.items(), key=lambda i: i[1])],
        "o",
        label=label_m1,
        color=color_m1,
        markersize=1,
    )
    plt.plot(
        xvalues,
        [data_m2[p] for p, _ in sorted(data_m1.items(), key=lambda i: i[1])],
        "o",
        label=label_m2,
        color=color_m2,
        markersize=1,
    )
    plt.legend()
    plt.ylabel("measurement values")
    plt.xlabel("packages")

    # plt.show()
    plt.savefig(f"./graphs/{m1}_and_{m2}.png")
    plt.close()


def table(head: tuple, body: list):
    table = []

    header = f"| Rank  | {'|'.join(head)} |"
    table.append(header)
    separator = len(head) * "| ----" + "|"
    table.append(separator)

    for i, d in enumerate(body):
        row = f"| {i + 1} | {'|'.join([f'{e}' for e in d])} |"
        table.append(row)

    return table


def generate():
    # lambdas
    write = (
        lambda x: report.write(x + "\n")
        if isinstance(x, str)
        else report.writelines([l + "\n" for l in x])
    )
    only_pkg = lambda x: x[len(DOMAIN) + 1 :] if x.startswith(DOMAIN) else x

    # group classes by packages
    packages = defaultdict(list)

    for c in DEPGRAPH:
        p = c.rpartition(".")[0]
        packages[p].append(c)

    # create graphs
    for m in MEASURES:
        plot_measurement_values(m)

    plot_comparison("noc", "ce")
    plot_comparison("dcm_cc", "noc")
    plot_comparison("dcm_cc", "ce")
    plot_comparison("dcm_cc", "dcm_lcom3")
    plot_comparison("noc", "dcm_lcom3")

    # create correlation matrix
    corr_data = {}

    for m in sorted(MEASURES.keys()):
        corr_data[MEASURES[m].label] = [DATA[m][p] for p in sorted(packages.keys())]

    df = pd.DataFrame(corr_data, columns=[MEASURES[m].label for m in sorted(MEASURES.keys())])

    corrMatrix = df.corr(method="pearson")
    sn.heatmap(corrMatrix, annot=True)
    plt.xticks(rotation=45)
    plt.savefig("./graphs/corr_matrix.png", bbox_inches="tight")

    # generate report
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = open(f"./reports/{DOMAIN} - {date}.md", "w")

    write("# Report")
    write(
        f"This report for the software system with domain {DOMAIN} was created at {date} based on dot file *{DOTFILE_PATH}*."
    )

    write("## Graphs & Data")
    write("- Data sets for all measures can be found in the folder *./data*")
    write("- Graphs for all measures can be found in the folder *./graphs*")
    write("- Correlation matrix for all measures  can be found in the folder *./graphs*")

    # general information
    write("## General Information")
    write(f"- Number of packages: {len(packages)}")
    write(f"- Number of classes: {len(DEPGRAPH)}")

    nested_classes = [c for c in DEPGRAPH if "$" in c]
    write(f"- Number of nested classes: {len(nested_classes)}")

    deps = [(c, d) for c, deps in DEPGRAPH.items() for d in deps]
    write(f"- Number of dependencies: {len(deps)}")

    # deny list
    write("## Deny List")
    write("Elements of the deny list:")
    for d in DENYLIST:
        write(f"- {d}")

    # measures
    write("## Measures")

    # statistics regarding noc
    write("### Number of Classes (NOC)")

    noc_avg = round(sum(DATA["noc"].values()) / len(DATA["noc"]), 0)
    write(f"- Average NOC: {len(DEPGRAPH)} / {len(packages)} = {noc_avg}")

    noc_below_avg = [p for p, v in DATA["noc"].items() if v < noc_avg]
    write(f"- Number of packages with NOC value below average: {len(noc_below_avg)}")

    noc_below_3 = [p for p, v in DATA["noc"].items() if v < 3]
    write(f"- Number of packages with NOC less than 3: {len(noc_below_3)}")

    write("- The 5 packages with highest NOC:")
    noc_top5 = [
        (only_pkg(p), v)
        for p, v in list(reversed(sorted(DATA["noc"].items(), key=lambda i: i[1])))[:5]
    ]
    write(table(("Packages", "NOC"), noc_top5))

    # statistics regarding ca
    write("### Afferent Coupling (Ca)")

    ca_zero = [p for p, v in DATA["ca"].items() if v == 0]
    write(f"- Number of packages with Ca == 0: {len(ca_zero)}")

    write("- The 5 packages with highest Ca (+ corresponding Ce and I values):")
    ca_top5 = [
        (only_pkg(p), v, DATA["ce"][p], round(DATA["instability"][p], 3))
        for p, v in list(reversed(sorted(DATA["ca"].items(), key=lambda i: i[1])))[:5]
    ]
    write(table(("Packages", "Ca", "Ce", "I"), ca_top5))

    # statistics regarding ce
    write("### Efferent Coupling (Ce)")

    ce_zero = [p for p, v in DATA["ce"].items() if v == 0]
    write(f"- Number of packages with Ce == 0: {len(ce_zero)}")

    write("- The 5 packages with highest Ce (+ corresponding Ca and I values):")
    ce_top5 = [
        (only_pkg(p), v, DATA["ca"][p], round(DATA["instability"][p], 3))
        for p, v in list(reversed(sorted(DATA["ce"].items(), key=lambda i: i[1])))[:5]
    ]
    write(table(("Packages", "Ce", "Ca", "I"), ca_top5))

    # statistics regarding instability
    write("### Instability (I)")

    i_zero = [p for p, v in DATA["instability"].items() if v == 0]
    write(f"- Number of packages with I == 0: {len(i_zero)}")

    i_one = [p for p, v in DATA["instability"].items() if v == 1]
    write(f"- Number of packages with I == 1: {len(i_one)}")

    write("- The 5 packages with highest I:")
    i_top5 = [
        (only_pkg(p), round(v, 3))
        for p, v in list(
            reversed(sorted(DATA["instability"].items(), key=lambda i: i[1]))
        )[:5]
    ]
    write(table(("Packages", "I"), i_top5))

    # statistics regarding dcm_lcom3
    write("### Dependency Cohesion Measures (DCM)")
    write("#### DCM based on LCOM3 (DCM<sub>LCOM3</sub>)")

    dcm_lcom3_avg = round(sum(DATA["dcm_lcom3"].values()) / len(DATA["dcm_lcom3"]), 0)
    write(f"- Average DCM<sub>LCOM3</sub>: {dcm_lcom3_avg}")

    write("- The 5 packages with highest DCM<sub>LCOM3</sub>:")
    dcm_lcom3_top5 = [
        (only_pkg(p), v)
        for p, v in list(
            reversed(sorted(DATA["dcm_lcom3"].items(), key=lambda i: i[1]))
        )[:5]
    ]
    write(table(("Packages", "DCM<sub>LCOM3</sub>"), dcm_lcom3_top5))

    # statistics regarding dcm_sim
    write("#### DCM based on similarity measure (DCM<sub>SIM</sub>")

    write(
        "- The 5 packages with highest DCM<sub>SIM</sub> (+ corresponding DCM<sub>CC</sub> value):"
    )
    dcm_sim_top5 = [
        (only_pkg(p), round(v, 3), round(DATA["dcm_cc"][p], 3))
        for p, v in list(reversed(sorted(DATA["dcm_sim"].items(), key=lambda i: i[1])))[
            :5
        ]
    ]
    write(table(("Packages", "DCM<sub>SIM</sub>", "DCM<sub>CC</sub>"), dcm_sim_top5))

    # statistics regarding dcm_cc
    write("#### DCM based on cohesion count (DCM<sub>CC</sub>")

    write(
        "- The 5 packages with highest DCM<sub>CC</sub> (+ corresponding DCM<sub>SIM</sub> value):"
    )
    dcm_cc_top5 = [
        (only_pkg(p), round(v, 3), round(DATA["dcm_sim"][p], 3))
        for p, v in list(reversed(sorted(DATA["dcm_cc"].items(), key=lambda i: i[1])))[
            :5
        ]
    ]
    write(table(("Packages", "DCM<sub>CC</sub>", "DCM<sub>SIM</sub>"), dcm_cc_top5))

    # statistics regarding p-depdegree
    write("### Package DepDegree (P-DepDegree)")

    write("5 packages with highest P-DepDegree:")
    pdd_top5 = [
        (only_pkg(p), round(v, 3))
        for p, v in list(
            reversed(sorted(DATA["p-depdegree"].items(), key=lambda i: i[1]))
        )[:5]
    ]
    write(table(("Packages", "P-DepDegree"), pdd_top5))

    # statistics regardging dlm
    write("### Dependency Locality Measure (DLM)")

    dlm_zero = [p for p, v in DATA["dlm"].items() if v == 0]
    write(f"- Number of packages with DLM == 0: {len(dlm_zero)}")

    write("- The 5 packages with highest DLM (+ corresponding NOC and Ce values):")
    dlm_top5 = [
        (only_pkg(p), v, DATA["noc"][p], DATA["ce"][p])
        for p, v in list(reversed(sorted(DATA["dlm"].items(), key=lambda i: i[1])))[:5]
    ]
    write(table(("Packages", "DLM", "NOC", "Ce"), dlm_top5))

    report.close()


if __name__ == "__main__":
    generate()