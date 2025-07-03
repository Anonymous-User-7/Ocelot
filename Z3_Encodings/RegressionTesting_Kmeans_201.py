"""
https://cran.r-project.org/src/base/R-2/

Version: 2.0.1 - 2.1.0

"""

from z3 import *
import numpy as np # type: ignore
import random


def kmeans():
    solver = Solver()
    num_points = 3
    num_features = 1
    num_clusters = 2
    max_iter = 1

    data = [[Real(f'x_{i}_{j}') for j in range(num_features)] for i in range(num_points)]

    centroids_init = [[Real(f'c_{j}_{f}') for f in range(num_features)] for j in range(num_clusters)]
    new_centroids_init = [[Real(f'new_c_{j}_{f}') for f in range(num_features)] for j in range(num_clusters)]
    
    for j in range(num_clusters):
        options = []
        for i in range(num_points):
            match = And([centroids_init[j][f] == data[i][f] for f in range(num_features)])
            options.append(match)
        solver.add(Or(options))

    for j in range(num_clusters):
        options = []
        for i in range(num_points):
            match = And([new_centroids_init[j][f] == data[i][f] for f in range(num_features)])
            options.append(match)
        solver.add(Or(options))

    for i in range(num_clusters):
        for j in range(i + 1, num_clusters):
            solver.add(Or([new_centroids_init[i][f] != new_centroids_init[j][f] for f in range(num_features)]))
            
    centroids_1 = [[Real(f'c1_{j}_{f}') for f in range(num_features)] for j in range(num_clusters)]
    centroids_2 = [[Real(f'c2_{j}_{f}') for f in range(num_features)] for j in range(num_clusters)]

    for j in range(num_clusters):
        for f in range(num_features):
            solver.add(centroids_1[j][f] == centroids_init[j][f])


    centroids_init_unique = And([
        Or([centroids_init[i][f] != centroids_init[j][f] for f in range(num_features)])
        for i in range(num_clusters) for j in range(i + 1, num_clusters)
    ])

    cond1 = And([
        centroids_2[j][f] == centroids_init[j][f]
        for j in range(num_clusters) for f in range(num_features)
    ])
    cond2 = And([
        centroids_2[j][f] == new_centroids_init[j][f]
        for j in range(num_clusters) for f in range(num_features)
    ])

    solver.add(Implies(centroids_init_unique, cond1))
    solver.add(Implies(Not(centroids_init_unique), cond2))

    solver.push()
    for j in range(num_clusters):
        solver.add(Or([centroids_1[j][i] != centroids_2[j][i] for i in range(num_features)]))

    if solver.check() == sat:
        model = solver.model()
        result_centroids1 = [[float(model[centroids_1[j][f]].as_decimal(10)) for f in range(num_features)] for j in range(num_clusters)]
        result_centroids2 = [[float(model[centroids_2[j][f]].as_decimal(10)) for f in range(num_features)] for j in range(num_clusters)]
        print("Centroids 1:", result_centroids1)
        print("Centroids 2:", result_centroids2)
        dataset = []
        for i in range(num_points):
            point = [(model[data[i][j]]) for j in range(num_features)] 
            dataset.append(point)
            print(f"Data point {i}: {point}")
    else:
        print("False.")
    solver.pop()


    labels1 = [Int(f'label1_{i}') for i in range(num_points)]
    labels2 = [Int(f'label2_{i}') for i in range(num_points)]


    # for j in range(num_clusters):
    #     for f in range(num_features):
    #         solver.add(centroids_1[j][f] == centroids_init[j][f])
    #         solver.add(centroids_2[j][f] == centroids_init[j][f])

    for iter in range(max_iter):
        labels1_new = [Int(f'label1_{i}_{iter}') for i in range(num_points)]
        labels2_new = [Int(f'label2_{i}_{iter}') for i in range(num_points)]

        for i in range(num_points):
            distance1_c1 = Sum([(data[i][f] - centroids_1[0][f]) ** 2 for f in range(num_features)])
            distance1_c2 = Sum([(data[i][f] - centroids_1[1][f]) ** 2 for f in range(num_features)])
            # solver.add(If(distance1_c1 > distance1_c2, labels1_new[i] == 0, labels1_new[i] == 1))
            solver.add(Implies(distance1_c1 > distance1_c2, labels1_new[i] == 0))
            solver.add(Implies(distance1_c1 <= distance1_c2, labels1_new[i] == 1))
            
            distance2_c1 = Sum([(data[i][f] - centroids_2[0][f]) ** 2 for f in range(num_features)])
            distance2_c2 = Sum([(data[i][f] - centroids_2[1][f]) ** 2 for f in range(num_features)])
            # solver.add(If(distance2_c1 > distance2_c2, labels2_new[i] == 0, labels2_new[i] == 1))
            solver.add(Implies(distance2_c1 > distance2_c2, labels2_new[i] == 0))
            solver.add(Implies(distance2_c1 <= distance2_c2, labels2_new[i] == 1))
            # # solver.add(Implies(distance2_c1 == distance2_c2, labels2_new[i] == labels2[i]))

        solver.push()
        if solver.check() == sat:
            model = solver.model()
            result_labels1 = [model[label].as_long() for label in labels1_new]
            result_labels2 = [model[label].as_long() for label in labels2_new]
            print("Cluster labels1:", result_labels1)
            print("Cluster labels2:", result_labels2)
        solver.pop()

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

    solver.add(Or([labels1[i] != labels2[i] for i in range(num_points)]))

    if solver.check() == sat:
        model = solver.model()
        result_labels1 = [model[label].as_long() for label in labels1]
        result_labels2 = [model[label].as_long() for label in labels2]
        print("Cluster labels1:", result_labels1)
        print("Cluster labels2:", result_labels2)
        dataset = []
        centers = []
        for i in range(num_points):
            point = [(model[data[i][j]]) for j in range(num_features)] 
            dataset.append(point)
            print(f"Data point {i}: {point}")
        print("Centers")
        for i in range(num_clusters):
            center = [(model[centroids_init[i][j]].as_decimal(10)) for j in range(num_features)]
            centers.append(center)
            print(f"{i}: {point}")
        print("Unique centers")
        for i in range(num_clusters):
            center = [(model[new_centroids_init[i][j]]) for j in range(num_features)]
            centers.append(center)
            print(f"{i}: {point}")
        # from sklearn.cluster import KMeans
        # kmeans = KMeans(n_clusters=2, init=centers, n_init=1, random_state=42)
        # kmeans.fit(dataset)
        # print(kmeans.labels_)

    else:
        print("False.")



kmeans()

    
    
    