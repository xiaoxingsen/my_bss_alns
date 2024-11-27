import random
import copy

def repair(solution, removed_truck_routes, removed_stations, removed_metro_routes, metro_routes_to_repair, vrp_data):
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
        metro_pairs = list(vrp_data.metro_metro_dis.keys())  # List of all potential metro pairs
        random.shuffle(metro_pairs)  # Randomize the order of pairs

        for station_pair in metro_pairs:
            if repairs_done >= len(removed_metro_routes):
                break

            from_station, to_station = station_pair
            reverse_pair = (to_station, from_station)

            # Ensure the pair is not part of the removed routes in either direction
            if station_pair not in removed_metro_routes and reverse_pair not in removed_metro_routes:
                # Check for conflicts with current routes
                if from_station not in departures_used and to_station not in arrivals_used:
                    departures_used.add(from_station)
                    arrivals_used.add(to_station)
                elif to_station not in departures_used and from_station not in arrivals_used:
                    from_station, to_station = to_station, from_station
                    departures_used.add(from_station)
                    arrivals_used.add(to_station)
                else:
                    continue  # Skip if both configurations are conflicting

                # Generate random schedule and cargo weight
                schedule = random.randint(1, 10)
                cargo_weight = random.randint(10, 100)
                solution.metro_routes[(from_station, to_station)] = (schedule, cargo_weight)
                repairs_done += 1


    if removed_stations is not None:
        # 尝试为每个被移除的地铁站找到新的连接
        # Attempt to reinsert removed stations
        potential_connections = []
        for removed_station in removed_stations:
            for station in vrp_data.metro_sites:
                if station != removed_station:
                    if (station not in departures_used and removed_station not in arrivals_used) or \
                            (station not in arrivals_used and removed_station not in departures_used):
                        # Store potential connections without considering distance
                        potential_connections.append((removed_station, station))

        # Shuffle the list to ensure random selection
        random.shuffle(potential_connections)
        # Try to connect removed stations with random other stations
        for (removed_station, station) in potential_connections:
            if (removed_station not in departures_used and station not in arrivals_used):
                direction = (removed_station, station)
            elif (removed_station not in arrivals_used and station not in departures_used):
                direction = (station, removed_station)
            else:
                continue  # Skip if both configurations are conflicting

            # If a valid direction is found, update the route
            departures_used.add(direction[0])
            arrivals_used.add(direction[1])
            schedule = random.randint(1, 10)  # Random schedule generation
            cargo_weight = random.randint(10, 100)  # Random cargo weight generation
            solution.metro_routes[direction] = (schedule, cargo_weight)
            break  # Stop after finding the first valid connection

    return solution
