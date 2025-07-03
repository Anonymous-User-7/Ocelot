"""
PR: https://github.com/scikit-learn/scikit-learn/pull/28121
Example of behaviour changed by this PR:

from sklearn.cluster import AffinityPropagation
c = [[0], [0], [0], [0], [0], [0], [0], [0]]
af = AffinityPropagation(damping = 0.5,affinity = 'euclidean').fit (c)
print (af.labels_)
output before this PR:

[0 1 0 1 2 1 1 0]
output after this PR:

[0 0 0 0 0 0 0 0]

https://stats.stackexchange.com/questions/156924/affinity-propagation-sklearn-strange-behavior/323665

Version 1.4.0 to 1.4.1

"""

from z3 import *

def Version1(s, S, n_samples, median):
    labels = [Int(f'label_v1_{i}') for i in range(n_samples)]

    for i in range(n_samples):
        s.add(labels[i] == (If(median >= S[0][n_samples-1], 0, i)))

    return labels


def Version2(s, S, n_samples, median):
    labels = [Int(f'label_v2_{i}') for i in range(n_samples)]
    
    for i in range(n_samples):
        s.add(labels[i] == (If(median > S[0][n_samples-1], 0, i)))

    return labels
   
def main():
    n_samples = 3
    n_features = 2

    X = [[Real(f'x_{i}_{j}') for j in range(n_features)] for i in range(n_samples)]


    S = [[Real(f's_{i}_{j}') for j in range(n_samples)] for i in range(n_samples)]

    labels1 = [Int(f'label1_{i}') for i in range(n_samples)]
    labels2 = [Int(f'label2_{i}') for i in range(n_samples)]

    s = Solver()
    for i in range(n_samples):
        for j in range(n_samples):
            s.add(S[i][j]**2 == -1*Sum([(X[i][k] - X[j][k])**2 for k in range(n_features)]))

    flat_S = [S[i][j] for i in range(n_samples) for j in range(n_samples)]

    median = Real('median')
    count_le = Sum([If(x <= median, 1, 0) for x in flat_S])
    count_ge = Sum([If(x >= median, 1, 0) for x in flat_S])
    s.add(count_le >= 5)
    s.add(count_ge >= 5)

    labels1 = Version1(s, S, n_samples, median)
    labels2 = Version2(s, S, n_samples, median)
    
    s.add(Or([labels1[i] != labels2[i] for i in range(n_samples)]))

    if s.check() == sat:
        m = s.model()
        print("X")
        for i in range(n_samples):
            print([m.evaluate(X[i][j]) for j in range(n_features)])

        print("\nS:")
        for i in range(n_samples):
            print([m.evaluate(S[i][j]) for j in range(n_samples)])

        print("\nLabels:")
        print([m.evaluate(labels1[i]) for i in range(n_samples)])
        print([m.evaluate(labels2[i]) for i in range(n_samples)])

        print("\nMedian of S:", m.evaluate(median))
    else:
        print("Unsatisfiable")


main()