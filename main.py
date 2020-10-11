import os

# create folders ./data, ./graphs and ./reports if they do not exist
if not os.path.exists('./data'):
    os.makedirs('data')

if not os.path.exists('./graphs'):
    os.makedirs('graphs')

if not os.path.exists("./reports"):
    os.mkdir("reports")  


print("Parsing dependency graph...")
import depgraph
depgraph.build_from_dotfile()

print("Calculating measurement values...")
import measures
measures.calc()

print("Creating report...")
import report
report.generate()

print("Done.")