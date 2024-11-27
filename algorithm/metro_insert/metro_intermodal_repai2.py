import random
import copy

def update_metro_routes(solution, potential_pairs, departures_used, arrivals_used, vrp_data, max_repairs):
    repairs_done = 0
    for (station_pair, distance) in potential_pairs:
        if repairs_done >= max_repairs:
            break
        from_station, to_station = station_pair
        reverse_pair = (to_station, from_station)

        # 检查是否与现有路线冲突
        if station_pair not in solution.metro_routes and reverse_pair not in solution.metro_routes:
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
    return solution

def repair(solution, removed_truck_routes, removed_stations, removed_metro_routes, metro_routes_to_repair, vrp_data):
    new_metro_routes = copy.deepcopy(solution.metro_routes)  # Make a copy of the existing metro routes
    departures_used = set(new_metro_routes.keys())
    arrivals_used = set([v[1] for v in new_metro_routes.keys()])

    # 获取所有地铁站点
    truck_metro_stations = {site for route in solution.truck_route for site in route[0] if site in vrp_data.metro_sites}

    # 处理地铁线路修复或移除站点的重建
    if metro_routes_to_repair is not None or removed_stations is not None:
        potential_pairs = sorted(vrp_data.metro_metro_dis.items(), key=lambda x: x[1])
        max_repairs = len(removed_metro_routes) if metro_routes_to_repair else len(removed_stations)
        solution = update_metro_routes(solution, potential_pairs, departures_used, arrivals_used, vrp_data, max_repairs)

    return solution

