from z3 import *
import numpy as np # type: ignore

def compute_centroid(cluster, idxs):
    centroid = [Sum([cluster[idx][i] for idx in idxs]) / len(idxs) for i in range(len(cluster[0]))]
    return centroid


def ward_distance(data, id1, id2, iter2=True):
    dist_squared = Sum([(data[id1][i] - data[id2][i]) ** 2 for i in range(len(data[0]))])
    if id1 == 0 and iter2:
        size1 = 2
    else:
        size1 = 1
    size2 = 1
    
    ward_dist = ((size1 * size2) / (size1 + size2) )* dist_squared
    return ward_dist


def HAC(n=4):
    # n = 4
    d = 2
    k = 2
    data_points = [[Real(f'x_{i}_{j}') for j in range(d)] for i in range(n)]
    # clusters = [Real(f'clusters_{i}') for i in range(n)]
    distance = [[Real(f'distance_{i}_{j}') for j in range(n)] for i in range(n)]
    s = Solver()
    

    for i in range(n):
        for j in range(n):
            distance[i][j] = Sum([(data_points[i][k] - data_points[j][k])**2 for k in range(d)])
            distance[i][j] = ward_distance(data_points, i, j, False) # size1 and size2 == 1, 1 - will work same as single link
    for i in range(n):
        for j in range(n):
            if i >= j:
                continue
            if i == 0 and j == 1:
                continue
            s.add(distance[0][1] < distance[i][j])

    
    # Single linkage critarion
    for i in range(n):
        for j in range(n):
            if i >= j:
                continue
            if i == 0 and j == 1:
                continue
            if i == 1 and j == 2:
                continue
            
            s.add(distance[1][2] < distance[i][j])
    
    
    # Ward linkage critarion
    centroid_01 = [Real(f'c01_{j}') for j in range(d)]
    for i in range(d):
        centroid_01[i] = (data_points[0][i] + data_points[1][i]) / 2


    data_ward = [[Real(f'x_{i}_{j}') for j in range(d)] for i in range(n-1)]
    distance_ward = [[Real(f'distance_ward_{i}_{j}') for j in range(n-1)] for i in range(n-1)]

    for i in range(n-1):
        for j in range(d):
            if i == 0:
                data_ward[i][j] = centroid_01[j]
            else:
                data_ward[i][j] = data_points[i+1][j]

    for i in range(n-1):
        for j in  range(n-1):
            s.add(distance_ward[i][j] == ward_distance(data_ward, i, j))
    
    for i in range(n-1):
        for j in range(n-1):
            if i >= j:
                continue
            if i == 1 and j == 2:
                continue
            s.add(distance_ward[1][2] < distance_ward[i][j])    

     


    if s.check() == sat:
        m = s.model()
        print(s.assertions())

        print("Data Points:")
        result_X = np.array([[m.evaluate(data_points[i][j]).as_decimal(5) for j in range(d)] for i in range(n)])
        print(result_X)

        print("\nDistance:")
        result_dist = np.array([[m.evaluate(distance[i][j]).as_decimal(5) for j in range(n)] for i in range(n)])
        print(result_dist)

        print("\n data_ward:")
        result_dist = np.array([[m.evaluate(data_ward[i][j]).as_decimal(5) for j in range(d)] for i in range(n-1)])
        print(result_dist)

        print("\nDistance Matrix ward:")
        result_dist = np.array([[m.evaluate(distance_ward[i][j]).as_decimal(5) for j in range(n-1)] for i in range(n-1)])
        print(result_dist)


    else:
        print("Unsat")
        
HAC(4)

# import time
# for i in range(4,10):
#     t0 = time.time()
#     HAC(i)
#     print(i, time.time()-t0)
