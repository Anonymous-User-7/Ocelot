from z3 import *
import math

def anomaly_score_z3(depth):
    return z3.If(depth == 1, z3.RealVal(0.7423985733387842),
           z3.If(depth == 2, z3.RealVal(0.5511556416954622),
           z3.If(depth == 3, z3.RealVal(0.4097585729429775),
           z3.If(depth == 4, z3.RealVal(0.3048920087278228),
           z3.If(depth == 5, z3.RealVal(0.2265243785653549),
           z3.If(depth == 6, z3.RealVal(0.1682348623622597),
           z3.If(depth == 7, z3.RealVal(0.1249373344214755),
           z3.If(depth == 8, z3.RealVal(0.0928132445006321),
           z3.If(depth == 9, z3.RealVal(0.0689444601177059),
           z3.If(depth == 10, z3.RealVal(0.0510730562630968),
           z3.If(depth == 11, z3.RealVal(0.0374180516351947),
           z3.If(depth == 12, z3.RealVal(0.0274543773485814),
           z3.If(depth == 13, z3.RealVal(0.0200540047223769),
           z3.If(depth == 14, z3.RealVal(0.0144155958754794),
           z3.If(depth == 15, z3.RealVal(0.0103640667325619), 
                z3.RealVal(-1))))))))))))))))



def IF():
    rows = 5
    solver = Solver()

    X = [Real(f'X_{i}') for i in range(rows)]
    solver.add(X[0] > 0)
    for i in range(rows - 1):
        solver.add(X[i] < X[i + 1])

    thr = [Real(f'thr_{i}') for i in range(rows-1)]
    for i in range(rows - 1):
        solver.add(thr[i] > X[i], thr[i] < X[i + 1])
    
    """ Run 1"""
    split_thr1 = [[Real(f'split_thr1_{i}_{j}') for i in range(rows)] for j in range(rows-1)]
    depth_run_1 = [[Int(f'depth_run_1_{i}_{j}') for i in range(rows)] for j in range(rows-1)]

    iter = 0
    for j in range(rows - 1):
    # for j in range(rows - 2, -1, -1):
        if iter == 0:
            for i in range(rows):
                solver.add(If(X[i] < thr[j], split_thr1[iter][i] == -1*thr[j], split_thr1[iter][i] == thr[j]))
                solver.add(If(X[i] < thr[j], depth_run_1[iter][i] == 1, depth_run_1[iter][i] == 1))

            iter+=1
            continue
        
        min_t_if_chain = X[0]
        for i in range(1, rows):
            min_t_if_chain = If(And(X[i] < thr[j], X[i] >= min_t_if_chain), X[i], min_t_if_chain)
        min_t = Real(f'min_t_{iter}')
        solver.add(min_t == min_t_if_chain)
        
        min_value = Real(f"min_value_{iter}")
        for i in range(rows):
            solver.add(Implies(X[i] == min_t, min_value == split_thr1[iter-1][i]))
        for i in range(rows):
            solver.add(split_thr1[iter][i] == If(X[i] < thr[j], 
                                            If(min_value == split_thr1[iter-1][i], -1*thr[j], split_thr1[iter-1][i]), 
                                            If(min_value == split_thr1[iter-1][i], thr[j], split_thr1[iter-1][i])))
            solver.add(depth_run_1[iter][i] == If(X[i] < thr[j], 
                                            If(min_value == split_thr1[iter-1][i], depth_run_1[iter-1][i]+1, depth_run_1[iter-1][i]), 
                                            If(min_value == split_thr1[iter-1][i], depth_run_1[iter-1][i]+1, depth_run_1[iter-1][i])))
        iter += 1

    depth_1 = depth_run_1[-1]
    inlier_r1 = [Int(f'inlier_r1_{i}') for i in range(rows)]
    for i in range(rows):
        solver.add(If(anomaly_score_z3(depth_run_1[-1][i]) > 0.5, inlier_r1[i] == 1, inlier_r1[i] == 0))

    """ Run 2"""
    split_thr2 = [[Real(f'split_thr2_{i}_{j}') for i in range(rows)] for j in range(rows-1)]
    depth_run_2 = [[Int(f'depth_run_2_{i}_{j}') for i in range(rows)] for j in range(rows-1)]

    iter = 0
    for j in range(rows - 1):
    # for j in range(rows - 2, -1, -1):
        if iter == 0:
            for i in range(rows):
                solver.add(If(X[i] < thr[j], split_thr2[iter][i] == -1*thr[j], split_thr2[iter][i] == thr[j]))
                solver.add(If(X[i] < thr[j], depth_run_2[iter][i] == 1, depth_run_2[iter][i] == 1))

            iter+=1
            continue
        
        min_t_if_chain = X[0]
        for i in range(1, rows):
            min_t_if_chain = If(And(X[i] < thr[j], X[i] >= min_t_if_chain), X[i], min_t_if_chain)
        min_t = Real(f'min_t_2_{iter}')
        solver.add(min_t == min_t_if_chain)
        
        min_value = Real(f"min_value_2_{iter}")
        for i in range(rows):
            solver.add(Implies(X[i] == min_t, min_value == split_thr2[iter-1][i]))
        for i in range(rows):
            solver.add(split_thr2[iter][i] == If(X[i] < thr[j], 
                                            If(min_value == split_thr2[iter-1][i], -1*thr[j], split_thr2[iter-1][i]), 
                                            If(min_value == split_thr2[iter-1][i], thr[j], split_thr2[iter-1][i])))
            solver.add(depth_run_2[iter][i] == If(X[i] < thr[j], 
                                            If(min_value == split_thr2[iter-1][i], depth_run_2[iter-1][i]+1, depth_run_2[iter-1][i]), 
                                            If(min_value == split_thr2[iter-1][i], depth_run_2[iter-1][i]+1, depth_run_2[iter-1][i])))
        iter += 1

    inlier_r2 = [Int(f'inlier_r2_{i}') for i in range(rows)]
    anomaly_score_r2 = [Real(f'anomaly_score_r2_{i}') for i in range(rows)]
    threshold = Real('threshold')
    for i in range(rows):
        solver.add(anomaly_score_r2[i] == anomaly_score_z3(depth_run_2[-1][i]))
        solver.add(If(anomaly_score_r2[i] > threshold, inlier_r2[i] == 1, inlier_r2[i] == 0))

    solver.add(Sum(inlier_r2) < 2)
    
    solver.add(Or([inlier_r1[i] != inlier_r2[i] for i in range(rows)]))

    if solver.check() == sat:
        model = solver.model()
        
        X_result = [model[x].as_decimal(3) for x in X]
        print("X:", X_result)
        
        thr_result = [model[t].as_decimal(3) for t in thr]
        print("thr:", thr_result)
        
        split_thr1_result = [[model[split_thr1[j][i]].as_decimal(3) for i in range(rows)] for j in range(rows-1)]
        print(split_thr1_result)

        depth_run_1_result = [[model[depth_run_1[j][i]] for i in range(rows)] for j in range(rows-1)]
        print(depth_run_1_result)

        # depth_1_result = [model[s1].as_long() for s1 in depth_1]
        # print("Depth 1:", depth_1_result)      

        # depth_2_result = [model[s2].as_long() for s2 in depth_2]
        # print("Depth 1:", depth_2_result)

        anomaly_score_r2_result = [model[s1].as_decimal(3) for s1 in anomaly_score_r2]
        print("Score:", anomaly_score_r2_result)

        # anomaly_score_r2_sorted_result = [model[s1].as_decimal(3) for s1 in anomaly_score_r2_sorted]
        # print("Sorted:", anomaly_score_r2_sorted_result)

        inlier_r1_result = [model[a] for a in inlier_r1]
        print("inlier_r1:", inlier_r1_result)
        
        inlier_r2_result = [model[a] for a in inlier_r2]
        print("inlier_r2:", inlier_r2_result)
    else:
        print("No solution")

IF()

