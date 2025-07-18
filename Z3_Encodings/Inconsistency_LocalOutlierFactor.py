from z3 import *
import sys

def Min(values):
    if len(values) == 1:
        return values[0]
    else:
        return If(values[0] < Min(values[1:]), values[0], Min(values[1:]))

def pairwise_knn():
    s = Solver()
    num_points = 4
    contamination = 0.1
    X = [[Real(f'X_{i}_{j}') for j in range(1)] for i in range(num_points)]
    for i in range(num_points):
        for j in range(1):
            s.add(And(X[i][j] >= -100, X[i][j] <= 100))

    distances = [[Real(f'distance_{i}_{j}') for j in range(num_points)] for i in range(num_points)]

    for i in range(num_points):
        s.add(distances[i][i] == 9999)
        for j in range(i + 1, num_points):
            dist = (X[i][0] - X[j][0])
            
            s.add(If(dist < 0, distances[i][j] == dist*-1, distances[i][j] == dist))
            s.add(If(dist < 0, distances[j][i] == dist*-1, distances[j][i] == dist))

    knn_indices = [[Int(f'knn_indices_{i}_{j}') for j in range(2)] for i in range(num_points)]
    knn = [[Real(f'knn_{i}_{j}') for j in range(2)] for i in range(num_points)]

    for i in range(num_points):
        sorted_dist = [Real(f'sorted_dist_{i}_{j}') for j in range(num_points)]
        s.add(Or(sorted_dist[0] == distances[i][0], sorted_dist[0] == distances[i][1], sorted_dist[0] == distances[i][2], sorted_dist[0] == distances[i][3]))
        s.add(Or(sorted_dist[1] == distances[i][0], sorted_dist[1] == distances[i][1], sorted_dist[1] == distances[i][2], sorted_dist[1] == distances[i][3]))
        s.add(Or(sorted_dist[2] == distances[i][0], sorted_dist[2] == distances[i][1], sorted_dist[2] == distances[i][2], sorted_dist[2] == distances[i][3]))
        s.add(Or(sorted_dist[3] == distances[i][0], sorted_dist[3] == distances[i][1], sorted_dist[3] == distances[i][2], sorted_dist[3] == distances[i][3]))

        s.add(sorted_dist[0] < sorted_dist[1])
        s.add(sorted_dist[1] < sorted_dist[2])
        s.add(sorted_dist[2] < sorted_dist[3])

        s.add(knn[i][0] == sorted_dist[0])
        s.add(knn[i][1] == sorted_dist[1])

        for j in range(num_points):
            s.add(Implies(knn[i][0] == distances[i][j], knn_indices[i][0] == j))
            s.add(Implies(knn[i][1] == distances[i][j], knn_indices[i][1] == j))
        
    dist_k = [[Real(f'dist_k_{i}_{j}') for j in range(2)] for i in range(num_points)]
    for i in range(num_points):
        for j in range(num_points):
            if i!=j:
                s.add(Implies(knn_indices[i][0] == j, dist_k[i][0] == knn[j][1]))
                s.add(Implies(knn_indices[i][1] == j, dist_k[i][1] == knn[j][1]))
    
    reach_dist_array = [[Real(f'reach_dist_array_{i}_{j}') for j in range(2)] for i in range(num_points)]
    for i in range(num_points):
        for j in range(2):
            s.add(If(dist_k[i][j] <= knn[i][j], reach_dist_array[i][j] == knn[i][j], reach_dist_array[i][j] == dist_k[i][j]))

    _lrd = [Real(f'_lrd_{i}') for i in range(num_points)]
    for i in range(num_points):
        s.add(_lrd[i] == 1/((reach_dist_array[i][0]+reach_dist_array[i][1])/2 + 1e-10))

    lrd_ratios_array = [[Real(f'lrd_ratios_array_{i}_{j}') for j in range(2)] for i in range(num_points)]
    for i in range(num_points):
        for j in range(num_points):
            if i!=j:
                s.add(Implies(knn_indices[i][0] == j, lrd_ratios_array[i][0] == _lrd[j]/_lrd[i]))
                s.add(Implies(knn_indices[i][1] == j, lrd_ratios_array[i][1] == _lrd[j]/_lrd[i]))

    _nof = [Real(f'_nof_{i}') for i in range(num_points)]
    for i in range(num_points):
        s.add(_nof[i] == -1*((lrd_ratios_array[i][0]+lrd_ratios_array[i][1])/2))

    labels_sk = [Int(f'labels_sk_{i}') for i in range(num_points)]
    labels_mat = [Int(f'labels_mat_{i}') for i in range(num_points)]

    for i in range(num_points):
        s.add(If(_nof[i] < -1.5, labels_sk[i] == -1, labels_sk[i] == 1))
    s.add(Or([labels_sk[i] == -1 for i in range(4)]))

    threshold = Real('threshold')
    s.add(If(contamination < 0.25, threshold == Min(_nof), threshold == -1.5))
    for i in range(num_points):
        s.add(If(_nof[i] < threshold, labels_mat[i] == -1, labels_mat[i] == 1))

    if s.check() == sat:
        model = s.model()
        print("Found mismatch when:\n")
        print("X:")
        X_result = [[model.evaluate(X[i][j]).as_decimal(6) for j in range(1)] for i in range(num_points)]
        print(X_result)

        labels_sk_result = [model.evaluate(labels_sk[i]) for i in range(num_points)]
        print("Sklearn Labels:", labels_sk_result)

        labels_mat_result = [model.evaluate(labels_mat[i]) for i in range(num_points)]
        print("Matrix Labels:", labels_mat_result)

    else:
        print("Unsatisfiable")


pairwise_knn()