"""Capacited Vehicles Routing Problem (CVRP)."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pickle
from dotenv import load_dotenv
import os
import math
import sqlite3
import copy
# from database_setup import create_connection, add_assignment, add_processed_demand, add_dropped
from . import database_setup
from . import process_data
from . import produce_matricies

# db_name = '/home/trogers/hobie_dashboard/demands.sqlite3'
db_name = 'demands.sqlite3'

"""GLOBALS"""
DURATION_TO_DISTANCE = (
    80476.2/3600)  # each additional hour has a 50 mile penalty in cost


# def create_data_model():
#     """Stores the data for the problem."""
#     load_dotenv()

#     data = {}

#     database = "demands.sqlite3"

#     conn = database_setup.create_connection(database)
#     if not conn:
#         print("Problem connecting to database")
#         exit()
#     else:
#         print(conn)

#     cur = conn.cursor()

#     cur.execute("SELECT address FROM demands")

#     addresses = cur.fetchall()

#     data['addresses'] = [address[0] for address in addresses]

#     # data['addresses'] = ['4925+Oceanside+Blvd+Oceanside+CA',
#     #                      '420+S+Coast+Hwy+Oceanside+CA',
#     #                      '34671+Puerto+Pl+Dana+Point+CA',
#     #                      '883+Sebastopol+Rd+Santa+Rosa+CA',
#     #                      '7812+Auburn+Blvd+Citrus+Heights+CA',
#     #                      '159+Paseo+del+Sol+Ave+Lake+Havasu+City+AZ',
#     #                      '1601+N+Lincoln+Ave+Loveland+CO',
#     #                      '4351+S+89th+St+Omaha+NE',
#     #                      '11110+N+Stemmons+Fwy+Dallas+TX',
#     #                      '3959+US-61+White+Bear+Lake+MN',
#     #                      '32+Weber+Rd+Central+Square+NY',
#     #                      '5211+Old+Post+Rd+Charlestown+RI',
#     #                      '1400+S+Federal+Hwy+Fort+Lauderdale+FL',
#     #                      '3+Varney+Point+Rd+Gilford+NH']

#     data['API_KEY'] = os.getenv('API_KEY')

#     cur.execute("SELECT load FROM demands")

#     loads = cur.fetchall()

#     data['demands'] = [load[0] for load in loads]
#     print("SUM:", sum(data['demands']))
#     # data['demands'] = [0, 1, 1, 2, 4, 2, 4, 32, 8, 1, 2, 27, 2, 20]

#     cur.execute("SELECT capacity FROM trucks")

#     capacities = cur.fetchall()

#     data['vehicle_capacities'] = [capacity[0] for capacity in capacities]
#     # data['vehicle_capacities'] = [15, 15, 15, 15, 15, 15, 15]
#     data['num_vehicles'] = len(data['vehicle_capacities'])
#     data['depot'] = 0

#     return data


def handle_split_loads(data):
    """If a load is larger then a vehicle capacity, split it into multiple loads."""
    max_capacity = min(data['vehicle_capacities'])

    location_dict = {}

    copy_loc = 0
    split_demands = []
    """location_dict holds keys as the demand # and the value as the original stop ID"""
    for i, demand in enumerate(data['demands']):
        copy_demand = demand
        if demand > max_capacity:
            location_dict[copy_loc] = i
            # loc = i
            while copy_demand > max_capacity:

                split_demands.append(max_capacity)
                copy_demand -= max_capacity
                data = duplicate_matrix_entry(data, copy_loc)
                location_dict[copy_loc] = i

                copy_loc += 1

        location_dict[copy_loc] = i
        split_demands.append(copy_demand)
        copy_loc += 1

        # temp = data['demands']
        data['demands'] = split_demands

    return data, location_dict


def add_all_processed_demands(conn, data, location_dict):
    """Adds all processed demands to the database."""

    print(data['demands'])
    for i, demand in enumerate(data['demands']):
        cur = conn.cursor()

        if i in location_dict:
            preprocess_id = location_dict[i]
        else:
            preprocess_id = i

        # address = data['addresses'][preprocess_id]
        cur.execute("SELECT address FROM demands WHERE demand_id = ?",
                    (preprocess_id+1,))
        # print(cur.fetchall(), preprocess_id)
        address = cur.fetchall()[0][0]
        processed_demand = (preprocess_id+1, address, demand)

        database_setup.add_processed_demand(conn, processed_demand)


def duplicate_matrix_entry(data, i):
    """Diplicates a matrix row/column and edits the distance/duration matrix"""
    distance_row, duration_row = copy.deepcopy(
        data['distance_matrix'][i]), copy.deepcopy(data['duration_matrix'][i])

    data['distance_matrix'].insert(i+1, distance_row)
    data['duration_matrix'].insert(i+1, duration_row)

    rows = len(data['distance_matrix'])

    distance_col = []
    duration_col = []
    for j in range(rows):
        distance_col.append(data['distance_matrix'][j][i])
        duration_col .append(data['duration_matrix'][j][i])

    for j in range(rows):
        data['distance_matrix'][j].insert(i+1, distance_col[j])
        data['duration_matrix'][j].insert(i+1, duration_col[j])

    return data


def calculate_penalties(data):
    """Calculates the penalties for each vehicle."""
    min_penalty = calculate_min_penalty(data)
    data['penalties'] = []
    print("Demands:", len(data['demands']))
    print("Distance:", len(data['distance_matrix']),
          len(data['distance_matrix'][0]))
    for i, demand in enumerate(data['demands']):

        penalty = min_penalty + \
            demand*(data['distance_matrix'][i][0] +
                    DURATION_TO_DISTANCE*data['duration_matrix'][i][0])

        data['penalties'].append(penalty)

    return data


def calculate_min_penalty(data):
    """Calculates the minimum penalty by caculating the sum of costs"""
    min_penalty = 0
    for i in range(len(data['distance_matrix'])):
        for j in range(len(data['distance_matrix'][0])):
            min_penalty += data['distance_matrix'][i][j] + \
                DURATION_TO_DISTANCE*data['duration_matrix'][i][j]

    return min_penalty


def print_solution(data, manager, routing, solution, location_dict):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}\n')

    total_distance = 0
    total_duration = 0
    total_load = 0

    dropped_nodes = 'Dropped nodes:'
    for node in range(routing.Size()):
        if routing.IsStart(node) or routing.IsEnd(node):
            continue
        if solution.Value(routing.NextVar(node)) == node:
            dropped_nodes += ' {}'.format(manager.IndexToNode(node))
            dropped_nodes += ' (Distance = {0}, Duration = {1}, Load = {2})'.format(
                data['distance_matrix'][node][0], data['duration_matrix'][node][0], data['demands'][node])
    print(dropped_nodes + "\n")

    for vehicle_id in range(data['num_vehicles']):

        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id+1)
        route_distance = 0
        route_duration = 0
        route_load = 0

        while not routing.IsEnd(index):

            node_index = manager.IndexToNode(index)
            curr_delivery = data['demands'][node_index]
            route_load += curr_delivery

            stop_id = location_dict[node_index] if node_index in location_dict else node_index

            plan_output += ' Stop ID: {0} (Delivery: {1} | Total: {2}) -> '.format(
                stop_id, curr_delivery, route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            # route_distance += routing.GetArcCostForVehicle(
            #     previous_index, index, vehicle_id)

            from_node = manager.IndexToNode(previous_index)
            to_node = manager.IndexToNode(index)
            print(data['distance_matrix'][from_node]
                  [to_node], from_node, "->", to_node)
            route_distance += data['distance_matrix'][from_node][to_node]
            route_duration += data['duration_matrix'][from_node][to_node]

        # final_stop = manager.IndexToNode(index)
        # plan_output += ' Stop ID: {0} (Delivery: {1} | Total: {2}))\n'.format(
        #     final_stop, data['demands'][final_stop], route_load)

        plan_output += 'END\n'
        plan_output += 'Distance of the route: {} miles\n'.format(
            round(route_distance*0.000621371, 2))
        plan_output += 'Duration of the route: {} hours\n'.format(
            round(route_duration/3600, 2))
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)

        total_distance += route_distance
        total_duration += route_duration
        total_load += route_load

    print('Total distance of all routes: {} miles'.format(
        round(total_distance*0.000621371, 2)))
    print("Total duration of all routes: {} hours".format(
        round(total_duration/3600, 2)))
    print('Total load of all routes: {}'.format(total_load))


def send_solution_to_db(data, manager, routing, solution, location_dict, conn):

    database = db_name
    conn = database_setup.create_connection(database)

    cur = conn.cursor()

    cur.execute("DELETE FROM assignments")
    cur.execute("DELETE FROM dropped")

    for node in range(routing.Size()):
        if routing.IsStart(node) or routing.IsEnd(node):
            continue
        if solution.Value(routing.NextVar(node)) == node:
            database_setup.add_dropped(conn, (manager.IndexToNode(node)+1,))

    for vehicle_id in range(data['num_vehicles']):

        index = routing.Start(vehicle_id)

        order_number = 0
        while not routing.IsEnd(index):

            processed_demand_index = manager.IndexToNode(index)

            demand_index = location_dict[processed_demand_index] if processed_demand_index in location_dict else processed_demand_index

            # route_distance += routing.GetArcCostForVehicle(
            #     previous_index, index, vehicle_id)

            previous_index = index
            index = solution.Value(routing.NextVar(index))

            from_node = manager.IndexToNode(previous_index)
            to_node = manager.IndexToNode(index)
            route_distance = data['distance_matrix'][from_node][to_node]
            route_duration = data['duration_matrix'][from_node][to_node]

            assignment = (processed_demand_index+1, vehicle_id+1,
                          order_number, route_distance, route_duration)

            database_setup.add_assignment(conn, assignment)

            order_number += 1


def solve():
    """Solve the CVRP problem."""

    # data = process_data.create_data_model()

    # data['distance_matrix'] = create_matrices(data)[0]
    # data['duration_matrix'] = create_matrices(data)[1]

    # distance_matrix_file = open(
    #     "/Users/tommyrogers/Desktop/Hobie_Dashboard/django-datta-able/paths/distance_matrix.pkl", "rb")
    # duration_matrix_file = open(
    #     "/Users/tommyrogers/Desktop/Hobie_Dashboard/django-datta-able/paths/duration_matrix.pkl", "rb")

    # data['distance_matrix'] = pickle.load(distance_matrix_file)

    # data['duration_matrix'] = pickle.load(duration_matrix_file)

    data = produce_matricies.main()

    # data['duration_matrix'] = pickle.load(duration_matrix_file)

    # if max(data['demands']) > max(data['vehicle_capacities']):
    #     data, location_dict = handle_split_loads(data)
    # else:
    #     location_dict = {}

    data, location_dict = handle_split_loads(data)

    database = db_name

    conn = database_setup.create_connection(database)

    cur = conn.cursor()

    cur.execute("DELETE FROM processed_demands")

    add_all_processed_demands(conn, data, location_dict)

    data = calculate_penalties(data)

    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    routing = pywrapcp.RoutingModel(manager)

    def cost_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return (data['distance_matrix'][from_node][to_node] + DURATION_TO_DISTANCE*data['duration_matrix'][from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(cost_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    for node in range(len(data['distance_matrix'])):
        routing.AddDisjunction(
            [manager.NodeToIndex(node)], math.ceil(data['penalties'][node]))

    # Setting heuristics
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 5

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        # print_solution(data, manager, routing, solution, location_dict)

        send_solution_to_db(data, manager, routing,
                            solution, location_dict, conn)


if __name__ == '__main__':
    solve()
