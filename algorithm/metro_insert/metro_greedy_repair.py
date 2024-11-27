import random
import copy

def repair(solution, removed_truck_routes, removed_stations, removed_metro_routes, metro_routes_to_repair, vrp_data):
    """
    Greedy repair operator for metro routes.
    地铁破坏后，metro_routes_to_repair 不为 None   removed_stations 为 None
    卡车破坏后，metro_routes_to_repair 为 None   removed_stations 不为 None
    :param solution:
    :param removed_truck_routes:
    :param removed_stations:
    :param removed_metro_routes:
    :param metro_routes_to_repair:
    :param vrp_data:
    :return:
    """
    # 初始化修复后的地铁路线字典
    new_metro_routes = copy.deepcopy(removed_metro_routes)
    # 初始化站点使用记录
    departures_used = set()
    arrivals_used = set()

    # 更新现有的使用记录
    for (from_station, to_station), _ in removed_metro_routes.items():
        departures_used.add(from_station)
        arrivals_used.add(to_station)

    if metro_routes_to_repair is not None:
        # 修复地铁线路
        repairs_done = 0
        # 选择新的地铁线路
        potential_pairs = sorted(vrp_data.metro_metro_dis.items(), key=lambda x: x[1])
        for (station_pair, distance) in potential_pairs:
            if repairs_done >= len(removed_metro_routes):
                break
            from_station, to_station = station_pair
            reverse_pair = (to_station, from_station)

            if station_pair not in removed_metro_routes and reverse_pair not in removed_metro_routes:
                # 检查是否与现有路线冲突
                if from_station not in departures_used and to_station not in arrivals_used:
                    departures_used.add(from_station)
                    arrivals_used.add(to_station)
                elif to_station not in departures_used and from_station not in arrivals_used:
                    from_station, to_station = to_station, from_station
                    departures_used.add(from_station)
                    arrivals_used.add(to_station)
                else:
                    continue  # 如果两种配置都冲突，跳过当前对

                # 生成班次和货物重量 先随机生成
                schedule = random.randint(1, 10)
                cargo_weight = random.randint(1, 10)
                solution.metro_routes[(from_station, to_station)] = (schedule, cargo_weight)
                repairs_done += 1

    if removed_stations is not None:
        # 尝试为每个被移除的地铁站找到新的连接
        # Attempt to reinsert removed stations
        for removed_station in removed_stations:
            closest_station = None
            min_distance = float('inf')

            # Find the closest station that doesn't create a conflict
            for station in vrp_data.metro_cargo_site_dict:
                if station != removed_station:
                    distance = vrp_data.metro_metro_dis.get((removed_station, station), float('inf'))
                    if distance < min_distance:
                        # Check for potential directional conflicts
                        if station not in departures_used and removed_station not in arrivals_used:
                            closest_station = station
                            min_distance = distance
                            direction = (removed_station, station)
                        elif station not in arrivals_used and removed_station not in departures_used:
                            closest_station = station
                            min_distance = distance
                            direction = (station, removed_station)

            if closest_station:
                # Add the new metro route in the correct direction
                departures_used.add(direction[0])
                arrivals_used.add(direction[1])
                schedule = random.randint(1, 10)  # Example schedule generation
                cargo_weight = random.randint(10, 100)  # Example cargo weight generation
                solution.metro_routes[direction] = (schedule, cargo_weight)

    return solution
