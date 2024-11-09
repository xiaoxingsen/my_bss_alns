import random
import math
"""
show may include time,distance,demand
"""


def destroy(solution, destroy_rate_low, destroy_rate_upper, vrp_data):
    # 计算需要移除的节点数量
    # 统计当前所有卡车路径中的所有站点
    all_stations = set()
    for route in solution.turck_route:
        path, _, _, _, _ = route
        all_stations.update(path)

    all_stations.discard(0)
    # 随机选择要移除的站点数量
    destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
    num_stations_to_remove = max(1, math.ceil(len(all_stations) * destroy_rate))

    # 统计所有非仓库的站点
    all_stations = set()
    for route in solution.turck_route:
        path, _, _, _, _ = route
        all_stations.update(path)

    all_stations.discard(0)  # 移除仓库站点（假设仓库标识为0）

    # 随机选择第一个移除的站点
    initial_removal = random.choice(list(all_stations))
    removal = [initial_removal]

    # 关联性字典
    similarity = {}

    # 权重定义（可以根据需要调整）
    phi_location = 0  # 地理位置权重
    phi_demand = 1  # 需求权重
    phi_time_window = 0  # 时间窗权重

    # 计算与初始移除站点的关联性
    for route in solution.turck_route:
        path, _, _, _, _ = route
        for node in path[1:]:
            if node in all_stations and node != initial_removal:
                # 计算关联性
                distance = vrp_data.cargo_site_dis[initial_removal, node]
                demand_diff = abs(
                    vrp_data.cargo_site_dict[initial_removal].demand - vrp_data.cargo_site_dict[node].demand)
                time_window_diff = abs(
                    vrp_data.cargo_site_dict[initial_removal].ready_time - vrp_data.cargo_site_dict[node].ready_time)

                # 综合计算加权相关性
                similarity[node] = (
                        phi_location * distance +
                        phi_demand * demand_diff +
                        phi_time_window * time_window_diff
                )

    # 根据加权相关性升序排序
    sorted_customers = sorted(similarity, key=similarity.get)

    # 移除与初始节点关联性最强的节点，直到达到gamma个节点
    while len(removal) < num_stations_to_remove:
        for customer in sorted_customers:
            if customer not in removal:
                removal.append(customer)
                # 更新当前节点为已移除节点，并重新计算关联性
                current_node = customer
                # 重新计算与新移除节点的关联性
                similarity = {}
                for route in solution.turck_route:
                    path, _, _, _, _ = route
                    for node in path[1:]:
                        if node in all_stations and node not in removal:
                            distance = vrp_data.cargo_site_dis[current_node, node]
                            demand_diff = abs(
                                vrp_data.cargo_site_dict[current_node].demand - vrp_data.cargo_site_dict[node].demand)
                            time_window_diff = abs(
                                vrp_data.cargo_site_dict[current_node].ready_time - vrp_data.cargo_site_dict[
                                    node].ready_time)

                            # 综合计算加权相关性
                            similarity[node] = (
                                    phi_location * distance +
                                    phi_demand * demand_diff +
                                    phi_time_window * time_window_diff
                            )

                # 更新排序
                sorted_customers = sorted(similarity, key=similarity.get)
                break  # 结束当前循环以开始下一个移除过程

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
            if site not in removal:
                new_path.append(site)
                new_arrive_times.append(arrive_times[idx])
                new_leave_times.append(leave_times[idx])
                new_workloads.append(workloads[idx])
                new_load_history.append(load_history[idx])

        # 生成新的路径信息
        new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
        new_truck_routes.append(new_route_info)

    return new_truck_routes, removal