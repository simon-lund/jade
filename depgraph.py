from config import DOMAIN, DOTFILE_PATH, DENYLIST

def is_valid(c: str) -> bool:
    """
    Check if class c is valid

    Returns true if c is within the domain, does not end on "Test",
    is not "package-info" and should not be ignored according to the deny  list
    """

    in_denylist = lambda x: len([p for p in DENYLIST if x.startswith(p)]) > 0

    return (
        c.startswith(DOMAIN)
        and not c.endswith("Test")
        and not c.endswith("package-info")
        and not in_denylist(c)
    )


def parse() -> dict:
    """
    Parses the dependencies of a directed graph stored in a dot file
    """

    import re

    PATTERN = r'\s*"([\w._$-]*)"\s*->\s*"([\w.$_]*)(\s*\([a-zA-Z.\s]*\)\s*)?";'

    with open(DOTFILE_PATH) as dotfile:
        lines = dotfile.readlines()

    # ignore first two lines and last line of dotfile
    # (contain only digraph syntax elements)
    lines = lines[2:-1]

    raw_deps = []

    for l in lines:
        match = re.match(PATTERN, l)
        c = match.group(1)
        d = match.group(2)

        raw_deps.append((c, d))

    return raw_deps


def refine_deps(deps: dict) -> list:
    """
    Refines the given dependencies by removing references to classes
    that are not in the given domain or should be removed according to the deny list
    """

    refined_deps = []

    for (c, d) in deps:
        # validate classes and add classes
        if is_valid(c) and is_valid(d):
            refined_deps.append((c, d))

    return refined_deps


def get_classes(deps: dict) -> list:
    """
    Returns a list of classes within in the domain that should not be ignored according to the deny list
    """

    classes = []

    for (c, d) in deps:
        if is_valid(c):
            classes.append(c)

        if is_valid(d):
            classes.append(d)

    return classes


def build(classes: list, deps: list) -> dict:
    """
    Build the depenency graph from the given dependencies
    """
    
    depgraph = {}

    for c in classes:
        depgraph[c] = []

    for (c, d) in deps:
        depgraph[c].append(d)

    return depgraph


def build_from_dotfile():
    """
    Builds the refined dependency graph for a project from dot file
    """

    import json

    raw_deps = parse()
    refined_deps = refine_deps(raw_deps)
    classes = get_classes(raw_deps)

    depgraph = build(classes, refined_deps)

    json.dump(depgraph, open("./data/depgraph.json", "w"), indent=4)


if __name__ == "__main__":
    build_from_dotfile()