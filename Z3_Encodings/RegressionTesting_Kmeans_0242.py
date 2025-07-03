"""
PR: https://github.com/scikit-learn/scikit-learn/pull/20200/files

Version: 0.24.2 to 1.0.0

"""

from z3 import *

def main(n_samples, k, n_init=10):
    best_labels_v1 = [[Int(f'best_labels_v1_{i}_{j}') for j in range(n_samples)] for i in range(n_init)]
    best_labels_v2 = [[Int(f'best_labels_v2_{i}_{j}') for j in range(n_samples)] for i in range(n_init)]
    

    best_inertia_v1 = [Real('best_inertia_v1_{i}') for i in range(n_init)]
    best_inertia_v2 = [Real('best_inertia_v2_{i}') for i in range(n_init)]
    

    s = Solver()


    labels = [[Int(f'label_v1_{i}_{j}') for j in range(n_samples)] for i in range(n_init)]
    inertia = [Real(f'inertia_{i}') for i in range(n_init)]

    for n_i in range(n_init):
        if n_i == 0:
            for j in range(n_samples):
                s.add(best_labels_v1[n_i][j] == labels[n_i][j])
                s.add(best_labels_v2[n_i][j] == labels[n_i][j])
            s.add(best_inertia_v1[n_i] == inertia[n_i])
            s.add(best_inertia_v2[n_i] == inertia[n_i])

        for j in range(n_samples):
            s.add(best_labels_v1[n_i][j] == If(inertia[n_i] < best_inertia_v1[n_i - 1] * (1 - 1e-6), labels[n_i][j], best_labels_v1[n_i - 1][j]))
            s.add(best_labels_v2[n_i][j] == If(inertia[n_i] < best_inertia_v2[n_i - 1], labels[n_i][j], best_labels_v2[n_i - 1][j]))
        s.add(best_inertia_v1[n_i] == If(inertia[n_i] < best_inertia_v1[n_i - 1] * (1 - 1e-6), inertia[n_i], best_inertia_v1[n_i - 1]))
        s.add(best_inertia_v2[n_i] == If(inertia[n_i] < best_inertia_v2[n_i - 1], inertia[n_i], best_inertia_v2[n_i - 1]))

        
    s.add(Or([best_labels_v1[n_init-1][i] != best_labels_v2[n_init-1][i] for i in range(n_samples)]))
    # s.add(best_inertia_v1[n_init-1] != best_inertia_v2[n_init-1])

    if s.check() == sat:
        m = s.model()
        print("Best Inertia V1:", m.evaluate(best_inertia_v1[n_init - 1]))
        print("Best Labels V1:", [m.evaluate(best_labels_v1[n_init - 1][i]) for i in range(n_samples)])
        print("Best Inertia V2:", m.evaluate(best_inertia_v2[n_init - 1]))
        print("Best Labels V2:", [m.evaluate(best_labels_v2[n_init - 1][i]) for i in range(n_samples)])
    else:
        print("Unsatisfiable")

main(n_samples=5, k=3)
