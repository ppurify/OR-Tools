from ortools.linear_solver import pywraplp
import numpy as np

solver = pywraplp.Solver.CreateSolver('SCIP')
if not solver:
    print("solver doesn't exist")


# Parameter
jobs = 7
job_array = np.arange(1,jobs + 1)

job_weight = np.array([0, 18, 12, 8, 8, 17, 16])
job_process = np.array([3, 6, 6, 5, 4, 8, 9])

Big_M = 100000

data = {}

def create_data_model():
    data['job_count'] = jobs
    data['jobs'] = job_array
    data['weight'] = job_weight
    data['process'] = job_process
    return data
    
data = create_data_model()


# Decision Variables
x = {}
# 0 ~ 6
for i in range(data['job_count']):
    for j in range(data['job_count']):
        if i < j :
            x[(i,j)] = solver.IntVar(0, 1, 'x_%i_%i' % (i, j))

c = {}
infinity = solver.infinity()

for i in range(data['job_count']):
    c[i] = solver.IntVar(0, infinity, 'c_%i' % i)

# c_max = solver.IntVar(0, infinity, 'C_max')

# Subject to
for i in range(data['job_count']):
    for j in range(data['job_count']):
        solver.Add(i < j)

        # if i < j:
        #     solver.Add( Big_M * (1 - x[i,j]) +  c[j] >= c[j] + data['process'][j])


# # c_j >= p_j
# for j in range(data['job_count']):
#     solver.Add(c[j] >= data['process'][j])

# # c_max >= c_j
# for j in range(data['job_count']):
#     solver.Add(c_max >= c[j])
    
# solver.Add(c_max >= sum(data['process']))


# Objective Function
objective = solver.Objective()
for j in range(data['job_count']):
    objective.SetCoefficient(c[j], 1)
objective.SetMinimization()

# total_completion_time = []
# for j in range(data['job_count']):
#     total_completion_time.append(c[j])
# objective = sum(total_completion_time)
# solver.Minimize(objective)

# Solve
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print('Objective value =', solver.Objective().Value())
    for i in range(data['job_count']):
        for j in range(data['job_count']):
            if i < j:
                print(x[i,j].name(), ' = ', x[i,j].solution_value())
                print(c[i].name(), ' = ', x[i,j].solution_value())

    # print()
    # print('Problem solved in %f milliseconds' % solver.wall_time())
    # print('Problem solved in %d iterations' % solver.iterations())
    # print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
else:
    print('The problem does not have an optimal solution.')