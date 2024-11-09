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
    # 统计当前所有卡车路径中的所有站点
    all_stations = set()
    for route in solution.turck_route:
        path, _, _, _, _ = route
        all_stations.update(path)

    all_stations.discard(0)
    # 随机选择要移除的站点数量
    destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
    num_stations_to_remove = max(1, math.ceil(len(all_stations) * destroy_rate))


    # 随机选择要移除的站点
    stations_to_remove = random.sample(all_stations, num_stations_to_remove)

    new_truck_routes = []

    # 遍历每条卡车路径，去掉对应的站点及相关信息
    for route in solution.turck_route:
        path, arrive_times, leave_times, workloads, load_history = route

        # 生成新路径，保留未被移除的站点及其相关信息
        new_path = []
        new_arrive_times = []
        new_leave_times = []
        new_workloads = []
        new_load_history = []

        for idx, site in enumerate(path):
            if site not in stations_to_remove:
                new_path.append(site)
                new_arrive_times.append(arrive_times[idx])
                new_leave_times.append(leave_times[idx])
                new_workloads.append(workloads[idx])
                new_load_history.append(load_history[idx])

        # 生成新的路径信息
        new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
        new_truck_routes.append(new_route_info)

    return new_truck_routes, stations_to_remove