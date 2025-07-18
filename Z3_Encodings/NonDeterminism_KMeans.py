from z3 import *
import numpy as np # type: ignore
import random


def kmeans():
    solver = Solver()
    num_points = 4
    num_features = 1
    num_clusters = 2
    max_iter = 1

    data = [[Real(f'x_{i}_{j}') for j in range(num_features)] for i in range(num_points)]

    centroids_init = [[Real(f'c_{j}_{f}') for f in range(num_features)] for j in range(num_clusters)]
    
    labels1 = [Int(f'label1_{i}') for i in range(num_points)]
    labels2 = [Int(f'label2_{i}') for i in range(num_points)]
    
    centroids_1 = [[Real(f'c1_{j}_{f}') for f in range(num_features)] for j in range(num_clusters)]
    centroids_2 = [[Real(f'c2_{j}_{f}') for f in range(num_features)] for j in range(num_clusters)]


    for iter in range(max_iter):
        labels1_new = [Int(f'label1_{i}_{iter}') for i in range(num_points)]
        labels2_new = [Int(f'label2_{i}_{iter}') for i in range(num_points)]

        for i in range(num_points):
            distance1_c1 = Sum([(data[i][f] - centroids_1[0][f]) ** 2 for f in range(num_features)])
            distance1_c2 = Sum([(data[i][f] - centroids_1[1][f]) ** 2 for f in range(num_features)])
            solver.add(Implies(distance1_c1 > distance1_c2, labels1_new[i] == 0))
            solver.add(Implies(distance1_c1 <= distance1_c2, labels1_new[i] == 1))
            
            distance2_c1 = Sum([(data[i][f] - centroids_2[0][f]) ** 2 for f in range(num_features)])
            distance2_c2 = Sum([(data[i][f] - centroids_2[1][f]) ** 2 for f in range(num_features)])
            solver.add(Implies(distance2_c1 > distance2_c2, labels2_new[i] == 0))
            solver.add(Implies(distance2_c1 <= distance2_c2, labels2_new[i] == 1))

        centroids_1_new = [[Real(f'c1_{j}_{f}_{iter}') for f in range(num_features)] for j in range(num_clusters)]
        centroids_2_new = [[Real(f'c2_{j}_{f}_{iter}') for f in range(num_features)] for j in range(num_clusters)]
        for j in range(num_clusters):
            for f in range(num_features):
                sum_c1 = Sum([If(labels1_new[i] == j, data[i][f], 0) for i in range(num_points)])
                count_c1 = Sum([If(labels1_new[i] == j, 1, 0) for i in range(num_points)])

                sum_c2 = Sum([If(labels2_new[i] == j, data[i][f], 0) for i in range(num_points)])
                count_c2 = Sum([If(labels2_new[i] == j, 1, 0) for i in range(num_points)])
                solver.add(If(count_c1 > 0, centroids_1_new[j][f] == sum_c1 / count_c1, centroids_1_new[j][f] == centroids_1[j][f]))
                solver.add(If(count_c2 > 0, centroids_2_new[j][f] == sum_c2 / count_c2, centroids_2_new[j][f] == centroids_2[j][f]))

        centroids_1 = centroids_1_new
        centroids_2 = centroids_2_new
        labels1 = labels1_new
        labels2 = labels2_new

    solver.add(Or([labels1[i] == labels2[i] for i in range(num_points)]))

    if solver.check() == sat:
        model = solver.model()
        print("Found mismatch when:\n")
        print("X:")
        print([model[data[i][j]] for i in range(num_points) for j in range(num_features)])

        print("V1 Centroids:")
        print([float(model[centroids_1[j][f]].as_decimal(10)) for j in range(num_clusters) for f in range(num_features)])
        print("V2 Centroids:")
        print([float(model[centroids_2[j][f]].as_decimal(10)) for j in range(num_clusters) for f in range(num_features)])

        print("\nResults:\n")
        result_labels1 = [model[label].as_long() for label in labels1]
        result_labels2 = [model[label].as_long() for label in labels2]
        print("V1 Cluster labels:", result_labels1)
        print("V2 Cluster labels:", result_labels2)

    else:
        print("Unsatisfiable")



kmeans()

    
    
    