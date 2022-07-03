from pulp import *
import pandas
import csv



def supply_or_demand_of_nodes(start_point, end_point, all_nodes):
    '''
    :param start_point:
    :param end_point:
    :return: Dictionary Country names are keys values are list which has 2 items first one represents supply second
            one represent demand. In our case, starting point supply part equals to 1, end point demand part equals to 1
            {'Austria': [1, 0],
              'Bulgaria': [0, 0],
              'Crotia': [0, 0],
              'Denmark': [0, 0],
              'Estonia': [0, 0],
              'Finland': [0, 1],
              }
    '''
    node_data = dict()
    for node in all_nodes:
        if start_point == node:
            node_data[node] = [1, 0]
        elif end_point == node:
            node_data[node] = [0, 1]
        else:
            node_data[node] = [0, 0]
    return node_data


def generate_arc_list(shipment_company, from_country, to_country):
    '''
    :param shipment_company:
    :param from_country:
    :param to_country:
    :return: Returns each possible direction as a list that contains tuples.
            (k, i, j) k -> company index i -> start point j -> destination
    [(1, 1, 2), (1, 1, 3), (1, 2, 3), (1, 2, 4), (1, 3, 4),
    (2, 1, 2), (2, 1, 3), (2, 2, 3), (2, 2, 4), (2, 3, 4)]
    '''
    arcs = list()
    for index in range(len(from_country)):
        arcs.append((shipment_company[index], from_country[index], to_country[index]))
    return arcs


def generate_arc_data(arcs, cost):
    '''
    :param arcs:
    :param cost:
    :return:  (cost, min_flow, max_flow)
              {(1, 1, 2): [2, 0, 1], (1, 1, 3): [2, 0, 1], (1, 2, 3): [1, 0, 1],
              (1, 2, 4): [3, 0, 1], (1, 3, 4): [1, 0, 1], (2, 1, 2): [2, 0, 1],
              (2, 1, 3): [2, 0, 1], (2, 2, 3): [2, 0, 1], (2, 2, 4): [2, 0, 1], (2, 3, 4): [2, 0, 1] }
    '''
    arc_data = dict()
    for index in range(len(cost)):
        arc_data[arcs[index]] = [cost[index], 0, 1]
    return arc_data


def generate_and_solve_model(node_data, arc_data):
    # Splits the dictionaries to be more understandable
    (supply, demand) = splitDict(node_data)
    (costs, mins, maxs) = splitDict(arc_data)

    # Creates Variables as Binary
    variables = LpVariable.dicts("Route", arcs, None, None, LpBinary)

    # Creates the 'prob' variable to contain the problem data
    prob = LpProblem("Minimum Cost Flow Problem Sample", LpMinimize)

    # Creates the objective function
    prob += lpSum([variables[a] * costs[a] for a in arcs]), "Total Cost of Transport"

    # Creates all problem constraints - this ensures the amount going into each node is
    # at least equal to the amount leaving
    for n in nodes:
        prob += (supply[n] + lpSum([variables[(k, i, j)] for (k, i, j) in arcs if j == n]) >=
                 demand[n] + lpSum([variables[(k, i, j)] for (k, i, j) in arcs if i == n])), \
                "Flow Conservation in Node %s" % n

    # The problem is solved using PuLP's choice of Solver
    prob.solve()

    # The optimised objective function value is printed to the screen
    print("Total Cost of Transportation = ", value(prob.objective))

    result = []
    for i in variables:
        if variables[i].varValue:
            print(i, '-->', variables[i].varValue)
            result.append(i)


    return value(prob.objective), result

def check_order(fromdata,routelist):
    days = len(routelist)
    if fromdata not in routelist[0]:
        new_list = list(reversed(routelist))
        return new_list,days

    return routelist,days
df = pandas.read_csv('shipment_prices.csv')
shipment_company = df["shipment_company"].tolist()
from_country = df["from_country"].tolist()
to_country = df["to_country"].tolist()
cost = df["cost"].tolist()

# list of nodes
nodes = list(set(from_country))  # i.e. [Austria, Bulgaria, etc.]


arcs = generate_arc_list(shipment_company, from_country, to_country)
arc_data = generate_arc_data(arcs, cost)
data=[]
for from_ in nodes:
    for to_ in nodes:
        data_dict = {}
        if from_ == to_:
            continue
        node_data = supply_or_demand_of_nodes(from_,to_, nodes)
        total_cost, routes_as_list = generate_and_solve_model(node_data, arc_data)
        data_dict['to']=to_
        data_dict['from']=from_
        data_dict['cost']=total_cost
        data_dict['path'],data_dict['num_of_days']=check_order(from_,routes_as_list)
        data.append(data_dict)
header = ['from', 'to', 'cost', 'path',"num_of_days"]
with open('result.csv', 'w') as f:
    writer = csv.DictWriter(f,fieldnames=header)
    writer.writeheader()
    writer.writerows(data)