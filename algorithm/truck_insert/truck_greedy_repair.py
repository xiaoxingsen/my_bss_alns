import random
import copy
def repair(solution, removed_truck_routes,removed_stations,removed_metro_routes, metro_routes_to_repair,vrp_data ):
    """
    A greedy repair operator for truck routes that tries to insert removed stations back into the truck routes
    at the position that minimizes the increase in travel distance.
    :param solution: The current solution object before repair.
    :param removed_truck_routes: The current truck routes after some stations have been removed.
    :param removed_stations: The list of stations that were removed and need to be reinserted.
    :param vrp_data: Data class instance containing distances and other problem-specific data.
    :return: Solution after repair.
    """
    # Copy the removed routes to modify
    new_truck_routes = copy.deepcopy(removed_truck_routes)

    # Attempt to reinsert each removed station
    for station in removed_stations:
        best_cost_increase = float('inf')
        best_route_index = None
        best_insert_position = None

        # Iterate over all routes to find the best insertion point
        for index, route in enumerate(new_truck_routes):
            path, arrive_times, leave_times, workloads, load_history = route
            for i in range(1, len(path)):  # Evaluate insertion between each pair of consecutive nodes
                # Calculate the cost of inserting the station between path[i-1] and path[i]
                current_cost = vrp_data.cargo_site_dis[path[i-1], path[i]]
                new_cost = (vrp_data.cargo_site_dis[path[i-1], station] +
                            vrp_data.cargo_site_dis[station, path[i]])
                cost_increase = new_cost - current_cost

                # Check if this position offers a lower cost increase than any previously considered option
                if cost_increase < best_cost_increase:
                    best_cost_increase = cost_increase
                    best_route_index = index
                    best_insert_position = i

        # Insert the station at the best found position
        if best_route_index is not None:
            best_route = new_truck_routes[best_route_index]
            best_route[0].insert(best_insert_position, station)
            # Insert placeholders
            best_route[1].insert(best_insert_position, None)  # arrive_times
            best_route[2].insert(best_insert_position, None)  # leave_times
            best_route[3].insert(best_insert_position, None)  # workloads
            best_route[4].insert(best_insert_position, None)  # load_history
            # You need to update arrive_times, leave_times, workloads, load_history as needed here based on your model

    # Update the solution object with the newly repaired routes
    solution.truck_route = new_truck_routes
    return solution

