"""
PR: https://github.com/mhahsler/dbscan/commit/e865cd3766a9a2c0c7220485aeaaf17a59c3c91c

Version: dbscan_0.9-6 to dbscan_0.9-7 
"""

from z3 import *
import sys

def Min(values):
    if len(values) == 1:
        return values[0]
    else:
        return If(values[0] < Min(values[1:]), values[0], Min(values[1:]))

def pairwise_knn(X):
    s = Solver()
    n_samples = 4
    X = [[Real(f'X_{i}_{j}') for j in range(1)] for i in range(n_samples)]
    for i in range(n_samples):
        for j in range(1):
            s.add(And(X[i][j] >= -100, X[i][j] <= 100))
    distances = [[Real(f'distance_{i}_{j}') for j in range(n_samples)] for i in range(n_samples)]

    for i in range(n_samples):
        s.add(distances[i][i] == 9999)
        for j in range(i + 1, n_samples):
            dist = (X[i][0] - X[j][0])
            
            s.add(If(dist < 0, distances[i][j] == dist*-1, distances[i][j] == dist))
            s.add(If(dist < 0, distances[j][i] == dist*-1, distances[j][i] == dist))

    knn_indices = [[Int(f'knn_indices_{i}_{j}') for j in range(2)] for i in range(n_samples)]
    knn = [[Real(f'knn_{i}_{j}') for j in range(2)] for i in range(n_samples)]

    for i in range(n_samples):
        sorted_dist = [Real(f'sorted_dist_{i}_{j}') for j in range(n_samples)]
        s.add(Or(sorted_dist[0] == distances[i][0], sorted_dist[0] == distances[i][1], sorted_dist[0] == distances[i][2], sorted_dist[0] == distances[i][3]))
        s.add(Or(sorted_dist[1] == distances[i][0], sorted_dist[1] == distances[i][1], sorted_dist[1] == distances[i][2], sorted_dist[1] == distances[i][3]))
        s.add(Or(sorted_dist[2] == distances[i][0], sorted_dist[2] == distances[i][1], sorted_dist[2] == distances[i][2], sorted_dist[2] == distances[i][3]))
        s.add(Or(sorted_dist[3] == distances[i][0], sorted_dist[3] == distances[i][1], sorted_dist[3] == distances[i][2], sorted_dist[3] == distances[i][3]))

        s.add(sorted_dist[0] <= sorted_dist[1])
        s.add(sorted_dist[1] <= sorted_dist[2])
        s.add(sorted_dist[2] <= sorted_dist[3])

        s.add(knn[i][0] == sorted_dist[0])
        s.add(knn[i][1] == sorted_dist[1])

        for j in range(n_samples):
            s.add(Implies(knn[i][0] == distances[i][j], knn_indices[i][0] == j))
            s.add(Implies(knn[i][1] == distances[i][j], knn_indices[i][1] == j))
        
    dist_k = [[Real(f'dist_k_{i}_{j}') for j in range(2)] for i in range(n_samples)]
    for i in range(n_samples):
        for j in range(n_samples):
            if i!=j:
                s.add(Implies(knn_indices[i][0] == j, dist_k[i][0] == knn[j][1]))
                s.add(Implies(knn_indices[i][1] == j, dist_k[i][1] == knn[j][1]))
    
    reach_dist_array = [[Real(f'reach_dist_array_{i}_{j}') for j in range(2)] for i in range(n_samples)]
    for i in range(n_samples):
        for j in range(2):
            s.add(If(dist_k[i][j] <= knn[i][j], reach_dist_array[i][j] == knn[i][j], reach_dist_array[i][j] == dist_k[i][j]))

    _lrd = [Real(f'_lrd_{i}') for i in range(n_samples)]
    for i in range(n_samples):
        s.add(If((reach_dist_array[i][0] + reach_dist_array[i][1]) == 0, 
             _lrd[i] == -1, 
             _lrd[i] == 1/((reach_dist_array[i][0] + reach_dist_array[i][1])/2)))

    lrd_ratios_array = [[Real(f'lrd_ratios_array_{i}_{j}') for j in range(2)] for i in range(n_samples)]
    for i in range(n_samples):
        for j in range(n_samples):
            if i!=j:
                s.add(Implies(knn_indices[i][0] == j, 
                              If(_lrd[i] <= 0, lrd_ratios_array[i][0] == -1, lrd_ratios_array[i][0] == _lrd[j]/_lrd[i])))
                s.add(Implies(knn_indices[i][1] == j, 
                              If(_lrd[i] <= 0, lrd_ratios_array[i][1] == -1, lrd_ratios_array[i][1] == _lrd[j]/_lrd[i])))

    _lof = [Real(f'_nof_{i}') for i in range(n_samples)]
    for i in range(n_samples):
        s.add(If(Or(lrd_ratios_array[i][0] == -1, lrd_ratios_array[i][1] == -1), 
                 _lof[i] == -1, 
                 _lof[i] == ((lrd_ratios_array[i][0]+lrd_ratios_array[i][1])/2)))

    lof_v1 = [Real(f'lof_v1_{i}') for i in range(n_samples)]
    lof_v2 = [Real(f'lof_v2_{i}') for i in range(n_samples)]

    for i in range(n_samples):
        s.add(lof_v1[i] == _lof[i])
        s.add(If(_lof[i] == -1, lof_v2[i] == 1, lof_v1[i] == _lof[i]))
      
    s.add(Or([lof_v1[i] != lof_v2[i] for i in range(n_samples)]))

    if s.check() == sat:
        model = s.model()
        print("Dataset:")
        X_result = [[model.evaluate(X[i][j]).as_decimal(6) for j in range(1)] for i in range(n_samples)]
        print(X_result)

        lof_v1_result = [model.evaluate(lof_v1[i]) for i in range(n_samples)]
        print(lof_v1_result)

        lof_v2_result = [model.evaluate(lof_v2[i]) for i in range(n_samples)]
        print(lof_v2_result)

    else:
        print("No solution found.")

k = 2 

pairwise_knn(X)
