def repair(solution, removed_truck_routes,removed_stations,removed_metro_routes, metro_routes_to_repair,vrp_data ):
    """
    This function does nothing repair
    :param solution:
    :param removed_truck_routes:
    :param removed_stations:
    :param removed_metro_routes:
    :param metro_routes_to_repair:
    :param vrp_data:
    :return:
    """
    solution.truck_route = removed_truck_routes
    solution.metro_routes = removed_metro_routes
    return solution