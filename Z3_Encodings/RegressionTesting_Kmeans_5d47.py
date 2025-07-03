"""

1. Commit: 5d47ce279042ed0ea9eb33f411b5ec67c40bdde7
2. Commit: https://github.com/scikit-learn/scikit-learn/commit/94d3bd42f863e90fbd7ad3659cee17d8b79d931b

Version 0.15 to 0.15.1
"""

from z3 import *


def Calcualte_Variance_Mean(X, n_samples, n_features):
    col_means = []
    for j in range(n_features):
        col_sum = Sum([X[i][j] for i in range(n_samples)])
        col_means.append(col_sum / n_samples)

    col_vars = []
    for j in range(n_features):
        var_sum = Sum([(X[i][j] - col_means[j]) ** 2 for i in range(n_samples)])
        col_vars.append(var_sum / n_samples)

    avg_var = Sum(col_vars) / n_features
    return avg_var


n_samples = 10
n_features = 2 
k = 2
# tol=1e-4
tol = RealVal(0)

X = [[Real(f"x_{i}_{j}") for j in range(n_features)] for i in range(n_samples)]

centers_old = [[Real(f"centers_old_{i}_{j}") for j in range(n_features)] for i in range(k)]
centers = [[Real(f"centers_{i}_{j}") for j in range(n_features)] for i in range(k)]

total_shift = Sum([
    Sum([(centers_old[i][j] - centers[i][j]) ** 2 for j in range(n_features)])
    for i in range(k)
])

avg_var = Calcualte_Variance_Mean(X, n_samples, n_features)

# cond1 = And(total_shift < tol, total_shift >= tol * avg_var)
# cond2 = And(total_shift >= tol, total_shift < tol * avg_var)
# final_condition = Or(cond1, cond2)


solver = Solver()
# solver.add(avg_var == 2)
# solver.add(total_shift < tol)

# solver.add(final_condition)
a = total_shift < tol * avg_var # Initial implementation
b = total_shift < tol # Edit 1: Sparse matrix support in KMeans. Commit: 5d47ce279042ed0ea9eb33f411b5ec67c40bdde7
c = total_shift <= tol # Edit 2: Fix bug https://github.com/scikit-learn/scikit-learn/issues/3374 for tol = 0

solver.add(Xor(a, b)) # True
solver.add(Xor(b, c)) # True


if solver.check() == sat:
    model = solver.model()
    print("Solution found:")
    for i in range(n_samples):
        row = []
        for j in range(n_features):
            row.append(model.evaluate(X[i][j]))
        print(f"Row {i}: {row}")

    def eval_expr(expr):
        return simplify(model.evaluate(expr, model_completion=True))

    evaluated_avg_var = eval_expr(avg_var)
    print(f"\nEvaluated avg_var: {evaluated_avg_var}")
    print("total_shift =", model.evaluate(total_shift))
    for i in range(k):
        for j in range(n_features):
            print(f"centers_old[{i}][{j}] = {model.evaluate(centers_old[i][j])}")
            print(f"centers    [{i}][{j}] = {model.evaluate(centers[i][j])}")
else:
    print("No solution found.")