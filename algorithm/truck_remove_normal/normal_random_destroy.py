import random
import copy
import math

def destroy(solution, destroy_rate_low, destroy_rate_upper, vrp_data):
    """
    This is the function to randomly remove some station in truck route from the feasible solution
    :param solution:
    :param destroy_rate:
    :param vrp_data:
    :return: a removed route  and a removed station list
    """
    # Get the set of all non-metro stations currently used in truck routes
    normal_stations = set()
    for route in solution.truck_route:
        path, _, _, _, _ = route
        normal_stations.update([site for site in path if site in vrp_data.normal_sites])

    # Ensure the depot (site 0) is not considered for removal
    normal_stations.discard(0)

    # Determine the number of stations to remove based on the random destruction rate
    destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
    num_stations_to_remove = max(1, math.ceil(len(normal_stations) * destroy_rate))

    # Randomly select the stations to remove
    stations_to_remove = random.sample(normal_stations, num_stations_to_remove)

    # Create new truck routes by removing the selected stations and their associated data
    new_truck_routes = []
    for route in solution.truck_route:
        path, arrive_times, leave_times, workloads, load_history = route
        new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history = [], [], [], [], []

        for idx, site in enumerate(path):
            if site not in stations_to_remove:
                new_path.append(site)
                new_arrive_times.append(arrive_times[idx])
                new_leave_times.append(leave_times[idx])
                new_workloads.append(workloads[idx])
                new_load_history.append(load_history[idx])

        new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
        new_truck_routes.append(new_route_info)

    return new_truck_routes, stations_to_remove