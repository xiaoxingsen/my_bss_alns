import random
import copy
def repair(solution, removed_truck_routes,removed_stations,removed_metro_routes, metro_routes_to_repair,vrp_data ):
    has_metro_route = bool(solution.metro_routes)
    metro_endpoints = {k[1]: k[0] for k in solution.metro_routes}
    metro_startpoints = {k[0]: k[1] for k in solution.metro_routes}

    # Use the existing routes if no metro routes are modified
    working_routes = copy.deepcopy(removed_truck_routes if removed_truck_routes else solution.truck_route)

    for station in removed_stations:
        station_demand = vrp_data.cargo_site_dict[station].demand
        inserted = False

        for route in working_routes:
            path, arrive_times, leave_times, workloads, load_history = route

            if has_metro_route:
                for i, site in enumerate(path):
                    position = None
                    if station_demand > 0 and site in metro_endpoints:
                        position = i + 1
                    elif station_demand < 0 and site in metro_startpoints:
                        position = i

                    if position is not None:
                        path.insert(position, station)
                        arrive_times.insert(position, None)
                        leave_times.insert(position, None)
                        workloads.insert(position, None)
                        load_history.insert(position, None)
                        inserted = True
                        break
            if inserted:
                break

        if not inserted:
            # Find the nearest metro station if no suitable metro route endpoint or startpoint is found
            best_route_idx, best_position = None, None
            min_distance = float('inf')

            for route_idx, route in enumerate(working_routes):
                path, _, _, _, _ = route
                for i, site in enumerate(path):
                    if site in vrp_data.metro_sites:
                        distance = vrp_data.cargo_site_dis.get((station, site), float('inf'))
                        if distance < min_distance:
                            min_distance = distance
                            best_route_idx, best_position = route_idx, i + 1

            if best_route_idx is not None:
                route = working_routes[best_route_idx]
                path, arrive_times, leave_times, workloads, load_history = route
                path.insert(best_position, station)
                arrive_times.insert(best_position, None)
                leave_times.insert(best_position, None)
                workloads.insert(best_position, None)
                load_history.insert(best_position, None)

    solution.truck_route = working_routes
    return solution

