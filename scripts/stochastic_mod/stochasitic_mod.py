
include("grammar/grammar_manifest.py")

gp = GraphPrinter()
gp.withIndex = True

postSection("The rules")

for r in inputRules:
	r.print(gp)

postSection("The graphs")

for g in inputGraphs:
	g.print(gp)

p = lambda d: all(a.vLabelCount("A") <= 6 for a in d.right) 

strategy = (
	addSubset(chain_atom) 
		>> rightPredicate[p] (
			repeat(inputRules)
		)
)

dg = dgRuleComp(inputGraphs, strategy)

dg.calc()

postSection("The deviation graph")

dg.print()
