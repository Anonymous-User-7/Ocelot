from z3 import *


def IF(rows, columns, n_trees):
    solver = Solver()

    X = [Real(f'X_{i}') for i in range(rows)]
    for i in range(rows):
        solver.add(X[i] >= 1, X[i] <= 10)
    solver.add(X[1] != X[2])


    Rank1 = [[Int(f'Rank1_{i}_{it}') for it in range(n_trees)] for i in range(rows)]
    Rank2 = [[Int(f'Rank2_{i}_{it}') for it in range(n_trees)] for i in range(rows)]
    rank_accumulated1 = [Int(f'Rank_accumulated1_{i}') for i in range(rows)]
    rank_accumulated2 = [Int(f'Rank_accumulated2_{i}') for i in range(rows)]

    for i in range(rows):
        for it in range(n_trees):
            solver.add(Rank1[i][it] == 0)
            solver.add(Rank2[i][it] == 0)

    for it in range(n_trees):
        solver.push()
        thr1 = [Real(f'thr1_{i}_{it}') for i in range(rows-1)]
        thr2 = [Real(f'thr2_{i}_{it}') for i in range(rows-1)]
        for j in range(rows-1):
            solver.add(thr1[j] >= 1, thr1[j] <= 9)
            solver.add(thr2[j] >= 1, thr2[j] <= 9)

        for i in range(rows):
            rank_expr1 = Sum([If(X[i] > thr1[j], 1, -1) for j in range(rows-1)])
            rank_expr2 = Sum([If(X[i] > thr2[j], 1, -1) for j in range(rows-1)])
            updated_rank1 = Int(f'Updated_Rank_Expr1_{i}_{it}')
            updated_rank2 = Int(f'Updated_Rank_Expr2_{i}_{it}')
            solver.add(updated_rank1 == Rank1[i][it] + rank_expr2)
            solver.add(updated_rank2 == Rank2[i][it] + rank_expr2)
            Rank1[i][it] = updated_rank1
            Rank2[i][it] = updated_rank2

        solver.pop()

    for i in range(rows):
        solver.add(rank_accumulated1[i] == sum([Rank1[i][it] for it in range(n_trees)]))
        solver.add(rank_accumulated2[i] == sum([Rank2[i][it] for it in range(n_trees)]))


    solver.push()
    solver.add(Or([rank_accumulated1[i] != rank_accumulated2[i] for i in range(rows)]))

    if solver.check() == sat:
        model = solver.model()
        print("X Values:")
        for i in range(rows):
            print(f"  X[{i}] = {model[X[i]]}")

        print("Run 1 Results:")
        for i in range(rows):
            print(f"  Rank[{i}] = {model[rank_accumulated1[i]]}")
        
        print("Run 2 Results:")
        for i in range(rows):
            print(f"  Rank[{i}] = {model[rank_accumulated2[i]]}")
    else:
        print("False")
    solver.pop()

IF(4, 1, 10)
