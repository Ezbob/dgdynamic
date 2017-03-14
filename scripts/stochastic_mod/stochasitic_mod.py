
include("grammar/grammar_manifest.py")

gp = GraphPrinter()
gp.withIndex = True

postSection("The rules")

for r in inputRules:
	r.print(gp)

postSection("The graphs")

for g in inputGraphs:
	g.print(gp)

strategy = (
	addSubset(chain_atom) 
		>> repeat[10](inputRules)
)

dg = dgRuleComp(inputGraphs, strategy)

dg.calc()

postSection("The deviation graph")

dg.print()
