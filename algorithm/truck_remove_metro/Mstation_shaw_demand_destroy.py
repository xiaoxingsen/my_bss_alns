import random
import math

def destroy(solution, destroy_rate_low, destroy_rate_upper, vrp_data):
    # 确定普通站点的集合
    normal_stations = {site for route in solution.truck_route for site in route[0] if site in vrp_data.metro_sites}
    normal_stations.discard(0)  # 排除仓库点

    # 根据给定的破坏率范围确定要移除的站点数量
    destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
    num_stations_to_remove = max(1, math.ceil(len(normal_stations) * destroy_rate))

    # 随机选择一个普通站点作为起始破坏点
    initial_removal = random.choice(list(normal_stations))
    removal = [initial_removal]

    # 初始化关联性字典
    similarity = {}
    phi_location = 0 # 地理位置权重
    phi_demand = 1   # 需求权重
    phi_time_window = 0  # 时间窗权重

    # 计算与初始移除站点的关联性
    for node in normal_stations:
        if node != initial_removal:
            distance = vrp_data.cargo_site_dis.get((initial_removal, node), float('inf'))
            demand_diff = abs(vrp_data.cargo_site_dict[initial_removal].demand - vrp_data.cargo_site_dict[node].demand)
            time_window_diff = abs(vrp_data.cargo_site_dict[initial_removal].ready_time - vrp_data.cargo_site_dict[node].ready_time)

            # 综合计算加权相关性
            similarity[node] = (
                phi_location * distance +
                phi_demand * demand_diff +
                phi_time_window * time_window_diff
            )

    # 按相关性升序排序选择要移除的站点
    sorted_stations = sorted(similarity, key=similarity.get)

    while len(removal) < num_stations_to_remove and sorted_stations:
        next_removal = sorted_stations.pop(0)  # 选择关联性最强的站点
        if next_removal not in removal:
            removal.append(next_removal)

    new_truck_routes = []

    # 更新卡车路径，去掉移除的站点
    for route in solution.truck_route:
        path, arrive_times, leave_times, workloads, load_history = route
        new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history = [], [], [], [], []

        for idx, site in enumerate(path):
            if site not in removal:
                new_path.append(site)
                new_arrive_times.append(arrive_times[idx])
                new_leave_times.append(leave_times[idx])
                new_workloads.append(workloads[idx])
                new_load_history.append(load_history[idx])

        new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
        new_truck_routes.append(new_route_info)

    return new_truck_routes, removal
