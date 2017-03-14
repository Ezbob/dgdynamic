rule [
    ruleID "chain decomposition"
    left [
        node [ id 4 label "A" ]
        edge [ source 1 target 4 label "-" ]
        edge [ source 4 target 2 label "-" ]
    ]
    context [
        node [ id 1 label "A" ]
        node [ id 2 label "A" ]
        node [ id 3 label "B" ]
        edge [ source 2 target 3 label "-" ]
    ]
    right [
        node [ id 4 label "B" ]
        edge [ source 1 target 4 label "-" ]
    ]
    constrainAdj [ 
        id 1 op "<" count 2 nodeLabels [ label "A" ]
    ]
    constrainAdj [ 
        id 2 op "<" count 2 nodeLabels [ label "A" ] 
    ]
    constrainAdj [
        id 3 op "<" count 2 nodeLabels [ label "A" ]
    ]
    constrainAdj [
        id 4 op "<" count 2 nodeLabels [ label "A" ]
    ]
]