import random
import copy
import math

def destroy(solution, destroy_rate_low, destroy_rate_upper, vrp_data):
    # define the distance cost dict to store the key and value
    distance_cost = {}

    # 遍历每条卡车路径
    for route in solution.turck_route:
        path, arrive_times, leave_times, workloads, load_history = route

        # 遍历路径中的非仓库站点
        for i in range(1, len(path)):  # 包含最后一个站点
            current_site = path[i]
            previous_site = path[i - 1]

            # 计算增加的距离
            if i < len(path) - 1:  # 不是最后一个站点
                next_site = path[i + 1]
                distance_increase = (solution.vrp_data.cargo_site_dis[previous_site, current_site] +
                                     solution.vrp_data.cargo_site_dis[current_site, next_site])
            else:  # 是最后一个站点，计算与仓库的距离
                distance_increase = (solution.vrp_data.cargo_site_dis[previous_site, current_site] +
                                     solution.vrp_data.cargo_site_dis[current_site, 0])  # 回到仓库

            distance_cost[current_site] = distance_increase

    # 根据增加距离降序排序
    sorted_stations = sorted(distance_cost, key=distance_cost.get, reverse=True)

    # 选择要移除的站点数量
    destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
    num_stations_to_remove = max(1, math.ceil(len(sorted_stations) * destroy_rate))

    # 移除增加距离最多的站点
    stations_to_remove = [site for site in sorted_stations[:num_stations_to_remove] if site != 0]

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


