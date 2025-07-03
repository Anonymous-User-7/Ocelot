from z3 import *
import numpy as np # type: ignore
import time




def Max(*args):
    max_val = args[0]
    for i in range(1, len(args)):
        max_val = If(args[i] > max_val, args[i], max_val)
    return max_val

def Min(*args):
    return If(args[0] < args[1], args[0], args[1])

def funct(n_samples, dimension, max_iter=1, damping=0.5):
    
    s = Solver()
    X = [[Real(f'x_{i}_{j}') for j in range(dimension)] for i in range(n_samples)]
    
    preference = Real('preference')
    Sdist = [[Real(f'Sdist_{i}_{j}') for j in range(n_samples)] for i in range(n_samples)]
    S1 = [[Real(f'S1_{i}_{j}') for j in range(n_samples)] for i in range(n_samples)]
    S2 = [[Real(f'S2_{i}_{j}') for j in range(n_samples)] for i in range(n_samples)]
    # noise1 = [[Real(f'noise1_{i}_{j}') for j in range(n_samples)] for i in range(n_samples)]
    # noise2 = [[Real(f'noise2_{i}_{j}') for j in range(n_samples)] for i in range(n_samples)]

    for i in range(n_samples):
        for j in range(n_samples):
            s.add(Sdist[i][j] == -1*Sum([(X[i][k] - X[j][k])**2 for k in range(dimension)]))

    for i in range(n_samples):
        for j in range(n_samples):
            # s.add(Or(noise1[i][j] == (2.220446049250313e-16 * Sdist[i][j] + 2.2250738585072014e-308 * 100) * -6, noise1[i][j] == (2.220446049250313e-16 * Sdist[i][j] + 2.2250738585072014e-308 * 100) * 6))
            # s.add(Or(noise2[i][j] == (2.220446049250313e-16 * Sdist[i][j] + 2.2250738585072014e-308 * 100) * -6, noise2[i][j] == (2.220446049250313e-16 * Sdist[i][j] + 2.2250738585072014e-308 * 100) * 6))
            # s.add(Or(noise1[i][j] == -0.6, noise1[i][j] == 0.6))
            # s.add(Or(noise2[i][j] == -0.00006, noise2[i][j] == 0.00006))
            
            if i != j:
                s.add(S1[i][j] == -1*Sum([(X[i][k] - X[j][k])**2 for k in range(dimension)]) + (2.220446049250313e-16 * Sdist[i][j] + 2.2250738585072014e-308 * 100) * 6)
                s.add(S2[i][j] == -1*Sum([(X[i][k] - X[j][k])**2 for k in range(dimension)]) - (2.220446049250313e-16 * Sdist[i][j] + 2.2250738585072014e-308 * 100) * 6)
                # s.add(S1[i][j] == -1*Sum([(X[i][k] - X[j][k])**2 for k in range(dimension)]) + noise1[i][j])
                # s.add(S2[i][j] == -1*Sum([(X[i][k] - X[j][k])**2 for k in range(dimension)]) + noise2[i][j])
            else:
                # s.add(S1[i][j] == preference + noise1[i][j])
                # s.add(S2[i][j] == preference + noise2[i][j])
                s.add(S1[i][j] == preference + (2.220446049250313e-16 * Sdist[i][j] + 2.2250738585072014e-308 * 100) * 6)
                s.add(S2[i][j] == preference - (2.220446049250313e-16 * Sdist[i][j] + 2.2250738585072014e-308 * 100) * 6)
                
            
    A1 = [[[Real(f'A1_{i}_{j}_{iter}') for j in range(n_samples)] for i in range(n_samples)] for iter in range(max_iter+1)]
    A2 = [[[Real(f'A2_{i}_{j}_{iter}') for j in range(n_samples)] for i in range(n_samples)] for iter in range(max_iter+1)]
    R1 = [[[Real(f'R1_{i}_{j}_{iter}') for j in range(n_samples)] for i in range(n_samples)] for iter in range(max_iter+1)]
    R2 = [[[Real(f'R2_{i}_{j}_{iter}') for j in range(n_samples)] for i in range(n_samples)] for iter in range(max_iter+1)]
    
    for i in range(n_samples):
        for j in range(n_samples):
            A1[0][i][j] = RealVal(0)
            R1[0][i][j] = RealVal(0)
            A2[0][i][j] = RealVal(0)
            R2[0][i][j] = RealVal(0)
            
    for iteration in range(max_iter):
        for i in range(n_samples):
            for k in range(n_samples):
                max_AS1 = Max(*[A1[iteration][i][kk] + S1[i][kk] for kk in range(n_samples) if kk != k])
                max_AS2 = Max(*[A2[iteration][i][kk] + S2[i][kk] for kk in range(n_samples) if kk != k])

                new_responsibility1 = S1[i][k] - max_AS1
                s.add(R1[iteration+1][i][k] == damping * R1[iteration][i][k] + (1 - damping) * new_responsibility1)
                new_responsibility2 = S2[i][k] - max_AS2
                s.add(R2[iteration+1][i][k] == damping * R2[iteration][i][k] + (1 - damping) * new_responsibility2)
                
        for i in range(n_samples):
            for k in range(n_samples):
                R_positive1 = [Max(R1[iteration+1][j][k], 0) for j in range(n_samples) if j != i]
                sum_Rp1 = Sum(R_positive1)
                R_positive2 = [Max(R2[iteration+1][j][k], 0) for j in range(n_samples) if j != i]
                sum_Rp2 = Sum(R_positive2)
                if i != k:
                    sum_Rp1 = If(0 < R1[iteration+1][k][k] + sum_Rp1, 0, R1[iteration+1][k][k] + sum_Rp1)
                    sum_Rp2 = If(0 < R2[iteration+1][k][k] + sum_Rp2, 0, R2[iteration+1][k][k] + sum_Rp2)

                s.add(A1[iteration+1][i][k] == damping * A1[iteration][i][k] + (1 - damping) * sum_Rp1)
                s.add(A2[iteration+1][i][k] == damping * A2[iteration][i][k] + (1 - damping) * sum_Rp2)
        

        s.push()
        exemplars1 = [Bool(f'exemplar1_{i}_{iteration}') for i in range(n_samples)]
        exemplars2 = [Bool(f'exemplar2_{i}_{iteration}') for i in range(n_samples)]
        for i in range(n_samples):
            s.add(exemplars1[i] == (A1[iteration][i][i] + R1[iteration][i][i] > 0))
            s.add(exemplars2[i] == (A2[iteration][i][i] + R2[iteration][i][i] > 0))

        s.add(Or([exemplars1[i] != exemplars2[i] for i in range(n_samples)]))
        if s.check() == sat:
            # print("Constraints:")
            # for constraint in s.assertions():
            #     print(constraint)
            print(f"Iteration {iteration + 1}: Exemplars are different.")
            m = s.model()
            result_X = np.array([[m.evaluate(X[i][j]).as_decimal(5) for j in range(dimension)] for i in range(n_samples)])
            print("X:")
            print(result_X)
            exemplars1_values = [i for i in range(n_samples) if m.eval(exemplars1[i])]
            exemplars2_values = [i for i in range(n_samples) if m.eval(exemplars2[i])]
            print(f"Exemplars 1: {exemplars1_values}")
            print(f"Exemplars 2: {exemplars2_values}")
            break
        else:
            print(f"Iteration {iteration + 1}: Exemplars are the same.")
        s.pop()
        


t0 = time.time()
funct(3, 2, max_iter=20)
print(time.time()-t0)
