import random
import copy

def repair(solution, removed_truck_routes,removed_stations,removed_metro_routes, metro_routes_to_repair,vrp_data ):
    """
    This function repairs the truck route by randomly inserting previously removed stations back into the truck routes.
    :param solution: The current solution from which stations were removed
    :param removed_truck_routes: Current truck routes after destruction
    :param removed_stations: List of stations that were removed and need to be reinserted
    :param vrp_data: VRPData object containing all necessary data like distances, demands, etc.
    :return: Repaired solution with removed stations randomly reinserted into the truck routes
    """
    # Use the truck routes after destruction as the starting point for repairs
    repaired_routes = copy.deepcopy(removed_truck_routes)

    # Shuffle the list of removed stations to randomize insertion order
    random.shuffle(removed_stations)

    # Attempt to reinsert each removed station into a random position in one of the existing truck routes
    for station in removed_stations:
        # Choose a random route to insert the station
        route_index = random.randint(0, len(repaired_routes) - 1)
        route = repaired_routes[route_index]

        # Choose a random position within the chosen route to insert the station
        # Ensuring not to disrupt the starting position at the depot (index 0)
        position_index = random.randint(1, len(route[0]) )  # route[0] is the path list of the route

        # Insert station into the path at the chosen position
        path, arrive_times, leave_times, workloads, load_history = route
        path.insert(position_index, station)

        # Re-calculate route details to maintain feasibility
        # Simple placeholders for updated route details
        arrive_times.insert(position_index, None)  # Placeholder for real calculation
        leave_times.insert(position_index, None)   # Placeholder for real calculation
        workloads.insert(position_index, None)     # Placeholder for real calculation
        load_history.insert(position_index, None)  # Placeholder for real calculation

        # Replace the updated route in the repaired routes list
        repaired_routes[route_index] = (path, arrive_times, leave_times, workloads, load_history)

    # Replace the truck routes in the solution with the repaired routes
    solution.truck_route = repaired_routes

    return solution
