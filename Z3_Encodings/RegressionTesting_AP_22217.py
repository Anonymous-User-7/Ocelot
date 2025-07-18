"""
PR: https://github.com/scikit-learn/scikit-learn/pull/22217/files

Version: 1.0.2 to 1.1.0
"""

from z3 import *

def simulate_affinity_propagation_old(S, E, never_converged):
    I = [i for i in range(len(E)) if E[i]]
    K = len(I)

    if K == 0:
        return [IntVal(-1) for _ in range(len(S))]

    c = [I.index(max(I, key=lambda j: S[i][j])) for i in range(len(S))]
    for k in range(K):
        ii = [i for i in range(len(c)) if c[i] == k]
        if not ii:
            continue
        best_idx = max(ii, key=lambda j: sum(S[j][jj] for jj in ii))
        I[k] = best_idx

    c = [I.index(max(I, key=lambda j: S[i][j])) for i in range(len(S))]
    labels = [IntVal(I[idx]) for idx in c]
    return labels

def simulate_affinity_propagation_new(S, E, never_converged):
    I = [i for i in range(len(E)) if E[i]]
    K = len(I)

    if K == 0:
        return [IntVal(-1) for _ in range(len(S))]

    labels_real = []
    c = [I.index(max(I, key=lambda j: S[i][j])) for i in range(len(S))]
    for k in range(K):
        ii = [i for i in range(len(c)) if c[i] == k]
        if not ii:
            continue
        best_idx = max(ii, key=lambda j: sum(S[j][jj] for jj in ii))
        I[k] = best_idx
    c = [I.index(max(I, key=lambda j: S[i][j])) for i in range(len(S))]
    labels_real = [IntVal(I[idx]) for idx in c]

    labels = [If(Not(never_converged), labels_real[i], IntVal(-1)) for i in range(len(S))]
    return labels


S = [
    [3, 2, 1,4],
    [2, 3, 1,2],
    [2, 3, 4,1],
    [1, 1, 3,6]
]

E = [False, True,True, False] 

never_converged = Bool("never_converged")

labels_old = simulate_affinity_propagation_old(S, E, never_converged)
labels_new  = simulate_affinity_propagation_new(S, E, never_converged)

solver = Solver()
mismatch = Or([labels_old[i] != labels_new[i] for i in range(len(S))])
solver.add(mismatch)

if solver.check() == sat:
    model = solver.model()
    print("Found mismatch when never_converged =", model[never_converged])
else:
    print("No mismatch found.")
