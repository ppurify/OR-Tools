from ortools.linear_solver import pywraplp
import numpy as np


solver = pywraplp.Solver.CreateSolver('SCIP')
if not solver:
    print("solver doesn't exist")


# Parameter
jobs = 7
job_weight = [0, 18, 12, 8, 8, 17, 16]
job_process = [3, 6, 6, 5, 4, 8, 9]

Big_M = 100000

data = {}

def create_data_model():
    data['job_count'] = jobs
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

# Subject to
for i in range(data['job_count']):
    for j in range(data['job_count']):
        if i< j:
            solver.Add( Big_M * (1 - x[(i,j)]) +  c[j] >= c[i] + data['process'][j])
            solver.Add( Big_M * x[(i,j)] +  c[i] >= c[j] + data['process'][i])


# c_j >= p_j
for j in range(data['job_count']):
    solver.Add(c[j] >= data['process'][j])


# Objective Function
objective = solver.Objective()
for j in range(data['job_count']):
    objective.SetCoefficient(c[j], 1)
objective.SetMinimization()



# Solve
status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print('Objective value =', solver.Objective().Value())
    print()

    c_j = np.array([])
    sorted_list = list(range(data['job_count']))

    for i in range(data['job_count']):
        c_j = np.append(c_j, c[i].solution_value())
        for j in range(data['job_count']):
            if i<j:
                # print(x[(i,j)].name(), ' = ', x[(i,j)].solution_value())
                i_index = sorted_list.index(i)
                j_index = sorted_list.index(j)
                if ( x[(i,j)].solution_value() == 0 ) & (i_index > j_index):
                    pass
                elif ( x[(i,j)].solution_value() == 1 ) & (i_index < j_index):
                    pass
                else:
                    sorted_list[i_index], sorted_list[j_index] = sorted_list[j_index], sorted_list[i_index]
                    # i_value = sorted_list[i_index]
                    # j_value = sorted_list[j_index]
                    # sorted_list[i_index] = j_value
                    # sorted_list[j_index] = i_value
                    

    print('process time : ', data['process'])
    print('weight : ', data['weight'])
    print('completion time : ', c_j)
    print('C_max : ', max(c_j))
    
    print()
    print('process time : ', np.array(data['process'])[sorted_list])
    print('completion time : ', c_j[sorted_list])
    start_time = c_j - data['process']
    print('start_time : ', start_time[sorted_list])

    # print()
    # print('Problem solved in %f milliseconds' % solver.wall_time())
    # print('Problem solved in %d iterations' % solver.iterations())
    # print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
else:
    print('The problem does not have an optimal solution.')


# https://plotly.com/python/gantt/
import plotly.figure_factory as ff

# df에 start랑 finish에는 float 적용 안됨! int로 변형 시켜야 함
start_time = start_time.astype(np.int64)
c_j = c_j.astype(np.int64)

job_name = []
df = []
for j in range(data['job_count']):
    job_name.append('job {number}'.format(number = j + 1))
    # df.append(dict(Task = job_name[j], Start=start_time[j], Finish=c_j[j]))
    df.append(dict(Task = 'Machine 1', Subtask= job_name[j], Start=start_time[j], Finish=c_j[j]))

# https://community.plotly.com/t/gantt-chart-resolve-overlap-in-grouped-tasks/38221
# 그룹으로 묶어주기 (Machine 1으로) : group_tasks = True  
fig = ff.create_gantt(df, index_col = 'Subtask', show_colorbar=True, bar_width=0.2, group_tasks= True)
fig.update_layout(xaxis_type='linear')

# 투명도
for shape in fig['data']:
    shape['opacity'] = 0.6

fig.show()
