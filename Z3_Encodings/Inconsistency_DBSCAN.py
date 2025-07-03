from z3 import *

# def region_query(s, m, point_id, eps, n_points):
#     seeds = [Int(f'seed_{point_id}_{i}') for i in range(n_points)]
#     for i in range(n_points):
#         dist_squared = Sum([(m[point_id][j] - m[i][j]) ** 2 for j in range(len(m[0]))])
#         s.add(If(dist_squared < eps**2, seeds[i] == 1, seeds[i] == 0))
    
#     return seeds

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

    # seeds1 = region_query(s, m, 0, eps1, n_points)
    inlier1 = Sum(seeds1) >= min_points1
    s.add(Implies(inlier1, classification1 == True))
    # s.add(classification1 == If(inlier1, True, False))

    # seeds2 = region_query(s, m, 0, eps2, n_points)
    inlier2 = Sum(seeds2) >= min_points2
    s.add(Implies(inlier2, classification2 == True))
    # s.add(classification2 == If(inlier2, True, False))

    # s.add(inlier1!=inlier2)

    for iter in range(n_points):
        # seeds_i = region_query_1(s, m, i, eps, n_points)
        seeds_i1 = [Int(f'seedi1_{iter}_{i}') for i in range(n_points)]
        seeds_i2 = [Int(f'seedi2_{iter}_{i}') for i in range(n_points)]

        for i in range(n_points):
            dist_squared = Sum([(m[0][j] - m[i][j]) ** 2 for j in range(len(m[0]))])
            s.add(If(dist_squared < eps1**2, seeds_i1[i] == 1, seeds_i1[i] == 0))
            s.add(If(dist_squared < eps2**2, seeds_i2[i] == 1, seeds_i2[i] == 0))

        s.add(Implies(And(Sum(seeds_i1) >= min_points1, seeds_i1[0] == 1), classification1 == True))
        s.add(Implies(And(Sum(seeds_i2) >= min_points1, seeds_i2[0] == 1), classification2 == True))

    
    # s.add(classification1==False)
    # s.add(classification2==True)
    s.add(classification1!=classification2)

    if s.check() == sat:
        model = s.model()
        print("Dataset:")
        for j in range(n_points):
            assigned_values = [model[m[j][i]] for i in range(2)]
            print(f"P{j}: {assigned_values}")
        print(model[classification1])
        print(model[classification2])
        for j in range(n_points):
            print(model[seeds1[j]])
        for j in range(n_points):
            print(model[seeds2[j]])
    else:
        print("UnSat")

dbscan()
