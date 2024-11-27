import random
import math

def destroy(solution, destroy_rate_low, destroy_rate_upper, vrp_data):
    # 定义字典存储每个站点的距离成本
    distance_cost = {}

    # 遍历每条卡车路径
    for route in solution.truck_route:
        path, _, _, _, _ = route

        # 只考虑普通站点
        path = [site for site in path if site in vrp_data.normal_sites]

        # 遍历路径中的站点计算增加的距离
        for i in range(1, len(path)):
            current_site = path[i]
            previous_site = path[i - 1]

            if i < len(path) - 1:
                next_site = path[i + 1]
            else:
                next_site = 0  # 如果是路径中的最后一个站点，则考虑返回仓库的距离

            # 计算站点由于当前位置增加的距离
            distance_increase = (
                vrp_data.cargo_site_dis.get((previous_site, current_site), float('inf')) +
                vrp_data.cargo_site_dis.get((current_site, next_site), float('inf'))
            )

            distance_cost[current_site] = distance_increase

    # 按增加的距离降序排序站点
    sorted_stations = sorted(distance_cost, key=distance_cost.get, reverse=True)

    # 确定要移除的站点数量
    destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
    num_stations_to_remove = max(1, math.ceil(len(sorted_stations) * destroy_rate))

    # 移除距离成本最高的站点
    stations_to_remove = sorted_stations[:num_stations_to_remove]

    new_truck_routes = []

    # 更新卡车路径，移除选定的站点
    for route in solution.truck_route:
        path, arrive_times, leave_times, workloads, load_history = route
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

        new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
        new_truck_routes.append(new_route_info)

    return new_truck_routes, stations_to_remove
