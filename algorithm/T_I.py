import random
import copy

class truck_greedy_repair:
    def repair(self,solution, removed_truck_routes, removed_stations, vrp_data):
        # 生成新的卡车路径列表
        new_truck_routes = []

        for new_station in removed_stations:
            best_insertion_cost = float('inf')
            best_position = None
            for routeidx, route in enumerate(removed_truck_routes):
                path, arrive_times, leave_times, workloads, load_history = route
                # 尝试在每个可能的位置插入新站点
                for i in range(1, len(path) + 1):  # 从1开始，以确保不会在仓库（0）处插入
                    if i != len(path):
                        previous_site = path[i - 1]
                        next_site = path[i]

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])
                    else:
                        previous_site = path[i - 1]
                        next_site = 0

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])

                    # 更新最佳插入位置
                    if insertion_cost < best_insertion_cost:
                        best_insertion_cost = insertion_cost
                        best_position = i  # 记录插入位置
                        best_route = routeidx

                    # 生成新的路径，包含插入的新站点
            if best_position is not None:
                # 将新站点插入到最佳位置
                new_path = (path[:best_position] + [new_station] + path[best_position:])
                new_arrive_times = arrive_times[:]  # 根据需求添加时间逻辑
                new_leave_times = leave_times[:]  # 根据需求添加时间逻辑
                new_workloads = workloads[:]  # 根据需求添加工作量逻辑
                new_load_history = load_history[:]  # 根据需求添加负载历史逻辑

                # 生成新的路径信息
                new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
                new_truck_routes.append(new_route_info)

        # 如果未插入任何新站点，则保留原路径
        if not any(new_station in path for new_station in removed_stations):
            new_truck_routes.append(route)

            return new_truck_routes

        # 遍历每条卡车路径
        for route in removed_truck_routes:
            path, arrive_times, leave_times, workloads, load_history = route

            for new_station in removed_stations:
                best_insertion_cost = float('inf')
                best_position = None

                # 尝试在每个可能的位置插入新站点
                for i in range(1, len(path) + 1):  # 从1开始，以确保不会在仓库（0）处插入
                    if i != len(path):
                        previous_site = path[i - 1]
                        next_site = path[i]

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])
                    else:
                        previous_site = path[i - 1]
                        next_site = 0

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])

                    # 更新最佳插入位置
                    if insertion_cost < best_insertion_cost:
                        best_insertion_cost = insertion_cost
                        best_position = i  # 记录插入位置

                # 生成新的路径，包含插入的新站点
                if best_position is not None:
                    # 将新站点插入到最佳位置
                    new_path = (path[:best_position] + [new_station] + path[best_position:])
                    new_arrive_times = arrive_times[:]  # 根据需求添加时间逻辑
                    new_leave_times = leave_times[:]  # 根据需求添加时间逻辑
                    new_workloads = workloads[:]  # 根据需求添加工作量逻辑
                    new_load_history = load_history[:]  # 根据需求添加负载历史逻辑

                    # 生成新的路径信息
                    new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
                    new_truck_routes.append(new_route_info)

            # 如果未插入任何新站点，则保留原路径
            if not any(new_station in path for new_station in removed_stations):
                new_truck_routes.append(route)

        return new_truck_routes

class truck_intermodal_repair:
    def repair(self,solution, removed_truck_routes, removed_stations, vrp_data):
        # 生成新的卡车路径列表
        new_truck_routes = []

        for new_station in removed_stations:
            best_insertion_cost = float('inf')
            best_position = None
            for routeidx, route in enumerate(removed_truck_routes):
                path, arrive_times, leave_times, workloads, load_history = route
                # 尝试在每个可能的位置插入新站点
                for i in range(1, len(path) + 1):  # 从1开始，以确保不会在仓库（0）处插入
                    if i != len(path):
                        previous_site = path[i - 1]
                        next_site = path[i]

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])
                    else:
                        previous_site = path[i - 1]
                        next_site = 0

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])

                    # 更新最佳插入位置
                    if insertion_cost < best_insertion_cost:
                        best_insertion_cost = insertion_cost
                        best_position = i  # 记录插入位置
                        best_route = routeidx

                    # 生成新的路径，包含插入的新站点
            if best_position is not None:
                # 将新站点插入到最佳位置
                new_path = (path[:best_position] + [new_station] + path[best_position:])
                new_arrive_times = arrive_times[:]  # 根据需求添加时间逻辑
                new_leave_times = leave_times[:]  # 根据需求添加时间逻辑
                new_workloads = workloads[:]  # 根据需求添加工作量逻辑
                new_load_history = load_history[:]  # 根据需求添加负载历史逻辑

                # 生成新的路径信息
                new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
                new_truck_routes.append(new_route_info)

        # 如果未插入任何新站点，则保留原路径
        if not any(new_station in path for new_station in removed_stations):
            new_truck_routes.append(route)

            return new_truck_routes

        # 遍历每条卡车路径
        for route in removed_truck_routes:
            path, arrive_times, leave_times, workloads, load_history = route

            for new_station in removed_stations:
                best_insertion_cost = float('inf')
                best_position = None

                # 尝试在每个可能的位置插入新站点
                for i in range(1, len(path) + 1):  # 从1开始，以确保不会在仓库（0）处插入
                    if i != len(path):
                        previous_site = path[i - 1]
                        next_site = path[i]

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])
                    else:
                        previous_site = path[i - 1]
                        next_site = 0

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])

                    # 更新最佳插入位置
                    if insertion_cost < best_insertion_cost:
                        best_insertion_cost = insertion_cost
                        best_position = i  # 记录插入位置

                # 生成新的路径，包含插入的新站点
                if best_position is not None:
                    # 将新站点插入到最佳位置
                    new_path = (path[:best_position] + [new_station] + path[best_position:])
                    new_arrive_times = arrive_times[:]  # 根据需求添加时间逻辑
                    new_leave_times = leave_times[:]  # 根据需求添加时间逻辑
                    new_workloads = workloads[:]  # 根据需求添加工作量逻辑
                    new_load_history = load_history[:]  # 根据需求添加负载历史逻辑

                    # 生成新的路径信息
                    new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
                    new_truck_routes.append(new_route_info)

            # 如果未插入任何新站点，则保留原路径
            if not any(new_station in path for new_station in removed_stations):
                new_truck_routes.append(route)

        return new_truck_routes

class truck_random_repair:
    def repair(self,solution, removed_truck_routes, removed_stations, vrp_data):
        # 生成新的卡车路径列表
        new_truck_routes = []

        for new_station in removed_stations:
            best_insertion_cost = float('inf')
            best_position = None
            for routeidx, route in enumerate(removed_truck_routes):
                path, arrive_times, leave_times, workloads, load_history = route
                # 尝试在每个可能的位置插入新站点
                for i in range(1, len(path) + 1):  # 从1开始，以确保不会在仓库（0）处插入
                    if i != len(path):
                        previous_site = path[i - 1]
                        next_site = path[i]

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])
                    else:
                        previous_site = path[i - 1]
                        next_site = 0

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])

                    # 更新最佳插入位置
                    if insertion_cost < best_insertion_cost:
                        best_insertion_cost = insertion_cost
                        best_position = i  # 记录插入位置
                        best_route = routeidx

                    # 生成新的路径，包含插入的新站点
            if best_position is not None:
                # 将新站点插入到最佳位置
                new_path = (path[:best_position] + [new_station] + path[best_position:])
                new_arrive_times = arrive_times[:]  # 根据需求添加时间逻辑
                new_leave_times = leave_times[:]  # 根据需求添加时间逻辑
                new_workloads = workloads[:]  # 根据需求添加工作量逻辑
                new_load_history = load_history[:]  # 根据需求添加负载历史逻辑

                # 生成新的路径信息
                new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
                new_truck_routes.append(new_route_info)

        # 如果未插入任何新站点，则保留原路径
        if not any(new_station in path for new_station in removed_stations):
            new_truck_routes.append(route)

            return new_truck_routes

        # 遍历每条卡车路径
        for route in removed_truck_routes:
            path, arrive_times, leave_times, workloads, load_history = route

            for new_station in removed_stations:
                best_insertion_cost = float('inf')
                best_position = None

                # 尝试在每个可能的位置插入新站点
                for i in range(1, len(path) + 1):  # 从1开始，以确保不会在仓库（0）处插入
                    if i != len(path):
                        previous_site = path[i - 1]
                        next_site = path[i]

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])
                    else:
                        previous_site = path[i - 1]
                        next_site = 0

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])

                    # 更新最佳插入位置
                    if insertion_cost < best_insertion_cost:
                        best_insertion_cost = insertion_cost
                        best_position = i  # 记录插入位置

                # 生成新的路径，包含插入的新站点
                if best_position is not None:
                    # 将新站点插入到最佳位置
                    new_path = (path[:best_position] + [new_station] + path[best_position:])
                    new_arrive_times = arrive_times[:]  # 根据需求添加时间逻辑
                    new_leave_times = leave_times[:]  # 根据需求添加时间逻辑
                    new_workloads = workloads[:]  # 根据需求添加工作量逻辑
                    new_load_history = load_history[:]  # 根据需求添加负载历史逻辑

                    # 生成新的路径信息
                    new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
                    new_truck_routes.append(new_route_info)

            # 如果未插入任何新站点，则保留原路径
            if not any(new_station in path for new_station in removed_stations):
                new_truck_routes.append(route)

        return new_truck_routes

class truck_regret_repair:
    def repair(self,solution, removed_truck_routes, removed_stations, vrp_data):
        # 生成新的卡车路径列表
        new_truck_routes = []

        for new_station in removed_stations:
            best_insertion_cost = float('inf')
            best_position = None
            for routeidx, route in enumerate(removed_truck_routes):
                path, arrive_times, leave_times, workloads, load_history = route
                # 尝试在每个可能的位置插入新站点
                for i in range(1, len(path) + 1):  # 从1开始，以确保不会在仓库（0）处插入
                    if i != len(path):
                        previous_site = path[i - 1]
                        next_site = path[i]

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])
                    else:
                        previous_site = path[i - 1]
                        next_site = 0

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])

                    # 更新最佳插入位置
                    if insertion_cost < best_insertion_cost:
                        best_insertion_cost = insertion_cost
                        best_position = i  # 记录插入位置
                        best_route = routeidx

                    # 生成新的路径，包含插入的新站点
            if best_position is not None:
                # 将新站点插入到最佳位置
                new_path = (path[:best_position] + [new_station] + path[best_position:])
                new_arrive_times = arrive_times[:]  # 根据需求添加时间逻辑
                new_leave_times = leave_times[:]  # 根据需求添加时间逻辑
                new_workloads = workloads[:]  # 根据需求添加工作量逻辑
                new_load_history = load_history[:]  # 根据需求添加负载历史逻辑

                # 生成新的路径信息
                new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
                new_truck_routes.append(new_route_info)

        # 如果未插入任何新站点，则保留原路径
        if not any(new_station in path for new_station in removed_stations):
            new_truck_routes.append(route)

            return new_truck_routes

        # 遍历每条卡车路径
        for route in removed_truck_routes:
            path, arrive_times, leave_times, workloads, load_history = route

            for new_station in removed_stations:
                best_insertion_cost = float('inf')
                best_position = None

                # 尝试在每个可能的位置插入新站点
                for i in range(1, len(path) + 1):  # 从1开始，以确保不会在仓库（0）处插入
                    if i != len(path):
                        previous_site = path[i - 1]
                        next_site = path[i]

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])
                    else:
                        previous_site = path[i - 1]
                        next_site = 0

                        # 计算当前的增加成本
                        insertion_cost = (vrp_data.cargo_site_dis[previous_site, new_station] +
                                          vrp_data.cargo_site_dis[new_station, next_site] -
                                          vrp_data.cargo_site_dis[previous_site, next_site])

                    # 更新最佳插入位置
                    if insertion_cost < best_insertion_cost:
                        best_insertion_cost = insertion_cost
                        best_position = i  # 记录插入位置

                # 生成新的路径，包含插入的新站点
                if best_position is not None:
                    # 将新站点插入到最佳位置
                    new_path = (path[:best_position] + [new_station] + path[best_position:])
                    new_arrive_times = arrive_times[:]  # 根据需求添加时间逻辑
                    new_leave_times = leave_times[:]  # 根据需求添加时间逻辑
                    new_workloads = workloads[:]  # 根据需求添加工作量逻辑
                    new_load_history = load_history[:]  # 根据需求添加负载历史逻辑

                    # 生成新的路径信息
                    new_route_info = (new_path, new_arrive_times, new_leave_times, new_workloads, new_load_history)
                    new_truck_routes.append(new_route_info)

            # 如果未插入任何新站点，则保留原路径
            if not any(new_station in path for new_station in removed_stations):
                new_truck_routes.append(route)

        return new_truck_routes