import random
import copy

def destroy(solution, destroy_rate_low, destroy_rate_upper, vrp_data):
    """
    Metro line total destruction operator: Randomly selects a set of metro stations and destroys all metro routes associated with these stations.
    :param solution: Current solution object containing metro routes.
    :param destroy_rate_low: Lower bound of the destruction rate.
    :param destroy_rate_upper: Upper bound of the destruction rate.
    :param vrp_data: VRP data object containing metro station details.
    :return: new_metro_routes (dict), routes_to_remove (list of tuples).
    """
    # Gather all unique metro stations involved in any route
    all_stations = set()
    for (from_station, to_station), _ in solution.metro_routes.items():
        all_stations.update([from_station, to_station])

    # Determine the number of stations to remove based on the destruction rate
    destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
    num_stations_to_remove = max(1, int(len(all_stations) * destroy_rate))

    # Randomly select stations to remove
    stations_to_remove = random.sample(all_stations, num_stations_to_remove)

    # Create a new dictionary of metro routes excluding the selected stations
    new_metro_routes = {}
    routes_to_remove = []

    for (from_station, to_station), route_info in solution.metro_routes.items():
        if from_station in stations_to_remove or to_station in stations_to_remove:
            routes_to_remove.append((from_station, to_station))
        else:
            new_metro_routes[(from_station, to_station)] = route_info

    return new_metro_routes, routes_to_remove
