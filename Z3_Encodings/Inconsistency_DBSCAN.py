from z3 import *

def dbscan():
    s = Solver()
    n_points = 4
    m = [[Real(f'm_{i}_{j}') for i in range(2)] for j in range(n_points)]
    eps1 = 0.5
    eps2 = 1
    min_points1 = 2
    min_points2 = 2

    classification1 = Bool('C1')
    classification2 = Bool('C2')

    s.add(Or(classification1 == True, classification1 == False))
    s.add(Or(classification2 == True, classification2 == False))
    seeds1 = [Int(f'seed1_0_{i}') for i in range(n_points)]
    seeds2 = [Int(f'seed2_0_{i}') for i in range(n_points)]

    for i in range(n_points):
        dist_squared = Sum([(m[0][j] - m[i][j]) ** 2 for j in range(len(m[0]))])
        s.add(If(dist_squared < eps1**2, seeds1[i] == 1, seeds1[i] == 0))
        s.add(If(dist_squared < eps2**2, seeds2[i] == 1, seeds2[i] == 0))

    inlier1 = Sum(seeds1) >= min_points1
    s.add(Implies(inlier1, classification1 == True))

    inlier2 = Sum(seeds2) >= min_points2
    s.add(Implies(inlier2, classification2 == True))

    for iter in range(n_points):
        seeds_i1 = [Int(f'seedi1_{iter}_{i}') for i in range(n_points)]
        seeds_i2 = [Int(f'seedi2_{iter}_{i}') for i in range(n_points)]

        for i in range(n_points):
            dist_squared = Sum([(m[0][j] - m[i][j]) ** 2 for j in range(len(m[0]))])
            s.add(If(dist_squared < eps1**2, seeds_i1[i] == 1, seeds_i1[i] == 0))
            s.add(If(dist_squared < eps2**2, seeds_i2[i] == 1, seeds_i2[i] == 0))

        s.add(Implies(And(Sum(seeds_i1) >= min_points1, seeds_i1[0] == 1), classification1 == True))
        s.add(Implies(And(Sum(seeds_i2) >= min_points1, seeds_i2[0] == 1), classification2 == True))

    s.add(classification1!=classification2)

    if s.check() == sat:
        model = s.model()
        print("Found mismatch when:\n")
        print("X:")
        for j in range(n_points):
            assigned_values = [model[m[j][i]] for i in range(2)]
            print(assigned_values)
        print(f"Classification of [{model[m[1][0]]},{model[m[1][1]]}]:")
        print("\tV1:", "Outlier" if not model[classification1] else "Inlier")
        print("\tV2:", "Outlier" if not model[classification2] else "Inlier")
        print("Seeds:")
        print("V1: ", [model[seeds1[j]] for j in range(n_points)])
        print("V2: ", [model[seeds2[j]] for j in range(n_points)])
    else:
        print("UnSat")

dbscan()
