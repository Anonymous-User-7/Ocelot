from z3 import *
import numpy as np
import random


def kmeans():
    solver = Solver()
    
    
    num_points = 20
    num_features = 3
    num_clusters = 3
    
    data = [[Real(f'x_{i}_{j}') for j in range(num_features)] for i in range(num_points)]

    centroids1 = [[Real(f'c1_{j}_{f}') for f in range(num_features)] for j in range(num_points)]
    centroids2 = [[Real(f'c2_{j}_{f}') for f in range(num_features)] for j in range(num_points)]
    
    labels1 = [Int(f'label1_{i}') for i in range(num_points)]
    labels2 = [Int(f'label2_{i}') for i in range(num_points)]
    
    for i in range(num_points):
        solver.add(And(labels1[i] >= 0, labels1[i] < num_clusters))
        solver.add(And(labels2[i] >= 0, labels2[i] < num_clusters))

    for i in range(num_points):
        for j in range(num_clusters):
            centroid = centroids1[j]
            distance = Sum([(data[i][f] - centroid[f]) ** 2 for f in range(num_features)])
            solver.add(Implies(labels1[i] == j, And([distance <= Sum([(data[i][f] - centroids1[k][f]) ** 2 for f in range(num_features)]) for k in range(num_clusters) if k != j])))
    
    for i in range(num_points):
        for j in range(num_clusters):
            centroid = centroids2[j]
            distance = Sum([(data[i][f] - centroid[f]) ** 2 for f in range(num_features)])
            solver.add(Implies(labels2[i] == j, And([distance <= Sum([(data[i][f] - centroids2[k][f]) ** 2 for f in range(num_features)]) for k in range(num_clusters) if k != j])))
    
    
    solver.add(Or([labels1[i] != labels2[i] for i in range(num_points)]))
    if solver.check() == sat:
        print("Constraints:")
        for constraint in solver.assertions():
            print(constraint)
        model = solver.model()
        result_labels1 = [model[label].as_long() for label in labels1]
        result_labels2 = [model[label].as_long() for label in labels2]
        print("Cluster labels1:", result_labels1)
        print("Cluster labels2:", result_labels2)
        
        for i in range(num_points):
            point = [model[data[i][j]] for j in range(dimension)]
            print(f"Data point {i}: {point}")
    else:
        print("False.")



kmeans()
    
    