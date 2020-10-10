# Domain of the project
DOMAIN = ""

# Path to the dependency graph generated by jdeps
DOTFILE_PATH = ""

# List of paths for which all classes starting with the path should be ignored
DENYLIST = []


# Example
DOMAIN = "org.sosy_lab.cpachecker"
DOTFILE_PATH = "./data/cpachecker.jar.dot"
DENYLIST = [
        "org.sosy_lab.cpachecker.cpa.smg.graphs.object.test.",
        "org.sosy_lab.cpachecker.util.test.",
        "org.sosy_lab.cpachecker.cpa.policyiteration.tests.",
        "org.sosy_lab.cpachecker.cpa.arg.witnessexport.WitnessExporterTest$",
        "org.sosy_lab.cpachecker.cpa.automaton.AutomatonInternalTest$",
        "org.sosy_lab.cpachecker.cpa.invariants.InvariantsTestSuite",
    ]
