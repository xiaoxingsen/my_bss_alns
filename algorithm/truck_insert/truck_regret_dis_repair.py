"""
regret: k step
2 kind: regret-distans  regret-cost
"""
import copy
import numpy as np

def repair(solution, removed_truck_routes,removed_stations,removed_metro_routes, metro_routes_to_repair,vrp_data ):
    """
    Greedily reinserts removed stations into truck routes with a focus on 'regret' over multiple future insertion
    opportunities. This method calculates the regret value of not inserting a station at the best spot compared to
    the second best, third best, etc., and chooses the station with the highest regret value to insert first.
    :param solution: Current solution before the repair.
    :param removed_truck_routes: Truck routes after stations have been removed.
    :param removed_stations: Stations that need to be reinserted.
    :param vrp_data: Data containing information about distances and demands.
    :return: Updated solution with stations reinserted.
    """
    # DeepCopy the truck routes to modify
    new_truck_routes = copy.deepcopy(removed_truck_routes)

    # Regret-2 insertion calculation
    while removed_stations:
        max_regret = -np.inf
        best_station = None
        best_route_index = None
        best_insert_position = None

        # Evaluate each station for insertion
        for station in removed_stations:
            station_regret = 0
            best_cost_difference = np.inf
            second_best_cost_difference = np.inf
            best_position = None
            best_route = None

            # Check each route for the best and second-best insertion point
            for idx, route in enumerate(new_truck_routes):
                path, _, _, _, _ = route
                for i in range(1, len(path)):
                    # Calculate cost increase if inserted here
                    cost_before = vrp_data.cargo_site_dis[path[i-1], path[i]]
                    cost_after_insert = (vrp_data.cargo_site_dis[path[i-1], station] +
                                         vrp_data.cargo_site_dis[station, path[i]])
                    cost_difference = cost_after_insert - cost_before

                    # Determine if this cost difference is better than the best or second-best found so far
                    if cost_difference < best_cost_difference:
                        second_best_cost_difference = best_cost_difference
                        best_cost_difference = cost_difference
                        best_position = i
                        best_route = idx
                    elif cost_difference < second_best_cost_difference:
                        second_best_cost_difference = cost_difference

            # Calculate regret for this station
            current_regret = second_best_cost_difference - best_cost_difference
            if current_regret > station_regret:
                station_regret = current_regret
                if station_regret > max_regret:
                    max_regret = station_regret
                    best_station = station
                    best_insert_position = best_position
                    best_route_index = best_route

        # Perform the insertion of the station with the highest regret
        if best_station:
            route = new_truck_routes[best_route_index]
            route[0].insert(best_insert_position, best_station)
            # Placeholder for actual time and workload calculation
            route[1].insert(best_insert_position, None)  # Update arrive_times later
            route[2].insert(best_insert_position, None)  # Update leave_times later
            route[3].insert(best_insert_position, None)  # Update workloads later
            route[4].insert(best_insert_position, None)  # Update load_history later

            removed_stations.remove(best_station)

    # Update the solution object with the newly repaired routes
    solution.truck_route = new_truck_routes
    return solution
