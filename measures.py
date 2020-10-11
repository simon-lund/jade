def pdd(pkg: list, depgraph: dict):
    """
    Calculates P-DepDegree
    """

    tdg = {}
    fringe = set(pkg)

    while fringe:
        c = fringe.pop()
        deps = depgraph[c]
        tdg[c] = deps

        fringe.update({d for d in deps if d not in tdg})

    # return ratio of the number of edges in tdg to the number of edges in depgraph
    return sum([len(tdg[c]) for c in tdg]) / sum([len(depgraph[c]) for c in depgraph])


def _dist(a: str, b: str) -> int:
    """
    Calculates the distance between to packages a, b

    >>> _dist("a.b.c.d.e", "a.b.f.g.h")
    6

    >>> _dist("a.b.c", "a.b.c")
    0

    >>> _dist("a.b.c.d", "a.b")
    2
    """

    path_a = a.split(".")
    path_b = b.split(".")

    # remove shared path
    # i.e. "a.b.c.d" & "a.b.e.f" => "c.d" & "e.f"
    zipped = list(zip(path_a, path_b))
    for i, j in zipped:
        if i == j:
            path_a.pop(0)
            path_b.pop(0)

    return len(path_a) + len(path_b)


def dlm(pkg_name: str, deps: set) -> int:
    """
    Calculates the dependency locality measure for package pkg and its dependencies
    Format of strings must be "a.b.c.A" (i.e. package tree path + class name)
    """

    from collections import Counter

    # 1. Determine the packages the dependencies lie in
    packages = Counter()
    for d in deps:
        p = d.rpartition(".")[0]
        packages[p] += 1

    # 2. Determine the distance between pkg and each p in packages
    distances = {p: _dist(pkg_name, p) for p in packages}

    # 3. Calculate dlm for pkg
    return sum([distances[p] * packages[p] for p in packages])


def dcm_lcom3(pkg: list):
    """
    Variant of dcm based on LCOM3
    """
    counter = 0

    for i, c in enumerate(pkg):
        for j in pkg[i + 1 :]:
            if c & j:
                counter += 1

    return counter


def dcm_sim(pkg: list):
    """
    Variant of dcm based on similarity measure
    """

    # Similarity function
    sim = lambda a, b: len(a & b) / len(a | b) if len(a | b) > 0 else 0

    pairs = []

    for i, c in enumerate(pkg):
        pairs.extend([(c, j) for j in pkg[i + 1 :]])

    sims = [sim(i, j) for (i, j) in pairs]

    return sum(sims) / len(pairs) if len(pairs) > 0 else 0


def dcm_cc(pkg: list):
    """
    Variant of dcm based on cohesion count
    """

    # Count function
    count = lambda d, package: len([c for c in pkg if d in c])

    deps = set.union(*pkg)
    counts = [count(d, pkg) for d in deps]

    return sum(counts) / (len(pkg) * len(deps)) if len(pkg) > 0 and len(deps) > 0 else 0


def noc(pkg):
    """
    Number of classes (and interfaces)
    """

    return len(pkg)


def ca(pkg: list, depgraph: dict):
    """
    Afferent coupling

    The number of classes outside the package that dependend on classes within the package
    """

    return len(
        [c for c in depgraph if c not in pkg and set(depgraph[c]).intersection(pkg)]
    )


def ce(pkg: list, depgraph: dict):
    """
    Efferent coupling

    The number of classes of a package that depend on classes outside the package
    """

    return len([c for c in pkg if set(depgraph[c]).difference(pkg)])


def instability(pkg, depgraph):
    """
    Instability of a package
    """

    aff = ca(pkg, depgraph)
    eff = ce(pkg, depgraph)

    return eff / (aff + eff) if aff + eff > 0 else 0
   


def calc() -> None:
    """
    Calculates all defined measures for all packages based on the dependency graph of a system
    """

    import json
    from collections import defaultdict, OrderedDict

    depgraph = json.load(open("./data/depgraph.json", "r"))

    # group classes by packages
    packages = defaultdict(list)

    for c in depgraph:
        p = c.rpartition(".")[0]
        packages[p].append(c)

    results = defaultdict(dict)

    # calculate measures for all packages
    for p, pkg_classes in packages.items():
        # number of classes (and interfaces)
        results["noc"][p] = noc(pkg_classes)

        # coupling measure
        results["ca"][p] = ca(pkg_classes, depgraph)
        results["ce"][p] = ce(pkg_classes, depgraph)
        results["instability"][p] = instability(pkg_classes, depgraph)

        # dependency cohesion measure
        class_deps = [set(depgraph[c]) for c in pkg_classes]

        results["dcm_lcom3"][p] = dcm_lcom3(class_deps)
        results["dcm_sim"][p] = dcm_sim(class_deps)
        results["dcm_cc"][p] = dcm_cc(class_deps)

        # package depdegree
        results["p-depdegree"][p] = pdd(pkg_classes, depgraph)

        # dependency locality measure
        pkg_deps = set().union(*[depgraph[c] for c in pkg_classes])
        results["dlm"][p] = dlm(p, pkg_deps)

    # store the measurement values
    for m, values in results.items():
        od = OrderedDict(sorted(values.items(), key = lambda i: i[1]))
        json.dump(od, open(f"./data/{m}.json", "w"), indent = 4)
     


if __name__ == "__main__":
    calc()