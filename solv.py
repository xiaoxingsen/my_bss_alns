from config import *
from help_function import greedy_get_a_possible_solution
import copy
from copy import deepcopy


class Solution:
    def __init__(self, vrp_data_ins, turck_route=(), metro_routes=None, score=None,skip_auth=False):
        self.vrp_data = vrp_data_ins

        if not turck_route:
            self.truck_route,self.metro_routes = greedy_get_a_possible_solution(self.vrp_data)
        else:
            self.truck_route = turck_route
            self.metro_routes = metro_routes
        self.obj = score if score else self.cal_score()

    def clone(self):
        """
        创建并返回该实例的深度复制
        """
        return deepcopy(self)

    def copy_with_init(self):
        """
        创建一个新的 Solution 实例，通过旧实例的值初始化，同时运行初始化过程
        """
        # 深度复制属性值
        new_turck_route = deepcopy(self.truck_route)
        new_metro_routes = deepcopy(self.metro_routes)
        new_score = self.obj

        # 创建一个新实例并传入复制的值（初始化逻辑会自动执行）
        new_instance = Solution(
            vrp_data_ins=self.vrp_data,
            turck_route=new_turck_route,
            metro_routes=new_metro_routes,
            score=new_score,
            skip_auth=False  # 使新实例重新进行验证
        )

        return new_instance

    def is_feasible(self):
        if not self.route_info_auth_ok(self.truck_route, self.metro_routes):
            return False

        if not self.collabor_ok(self.truck_route, self.metro_routes):
            return False

        if not self.demand_inventory_ok(self.truck_route, self.metro_routes):
            return False

        return True

    def cal_score(self):
        Cf = self.vrp_data.fixed_cost  # 每辆卡车的固定成本系数
        Cc1 = self.vrp_data.handling_cost_per_unit  # 每单位搬运货物的成本
        Cc2 = self.vrp_data.travel_cost_per_unit_distance  # 每单位距离的旅行时间成本
        Cm1 = self.vrp_data.metro_transport_cost_per_unit  # 每单位地铁运输量的成本

        # 1. 计算卡车固定成本
        active_truck_routes = [route for route in self.truck_route if not (len(route[0]) == 1 and route[0][0] == 0)]
        truck_fixed_cost = Cf * len(active_truck_routes)

        # 2. 计算卡车的搬运货物成本和旅行时间成本
        handling_cost = 0
        travel_cost = 0
        for route in active_truck_routes:
            path, arrive_times, leave_times, workloads, load_history = route

            # 计算搬运货物成本
            handling_cost += sum(Cc1 * abs(workload) for workload in workloads[1:])

            # 计算旅行时间成本（路径总距离）
            total_distance = 0
            for i in range(1, len(path)):
                site_a = path[i - 1]
                site_b = path[i]
                total_distance += self.vrp_data.cargo_site_dis.get((site_a, site_b), 0)
            # 添加从最后一个站点回到仓库的距离
            last_site = path[-1]
            total_distance += self.vrp_data.cargo_site_dis.get((last_site, 0), 0)

            travel_cost += Cc2 * total_distance

        # 3. 计算地铁搬迁成本
        metro_cost = sum(Cm1 * cargo_weight for _, (schedule, cargo_weight) in self.metro_routes.items())

        # 总成本为所有成本的和
        total_cost = truck_fixed_cost + handling_cost + travel_cost + metro_cost
        return total_cost

    def demand_inventory_ok(self, turck_route, metro_routes):
        # 初始化字典来跟踪每个站点的收到和送出货物量
        received_goods = {site: 0 for site in self.vrp_data.all_sites}
        sent_goods = {site: 0 for site in self.vrp_data.all_sites}

        # 统计卡车路径上的收到和送出货物量
        for path, _, _, workloads, _ in turck_route:

            # 如果路径只包含仓库点，跳过检查
            if len(path) == 1 and path[0] == 0:
                continue

            for idx, site in enumerate(path):
                if idx == 0:
                    continue  # 跳过仓库
                if workloads[idx] > 0:  # 负值表示收到货物，正值表示送出货物
                    received_goods[site] -= workloads[idx]
                else:
                    sent_goods[site] += workloads[idx]  # 将负值转为正值表示送出

        # 统计地铁路径上的收到和送出货物量
        for (from_station, to_station), (_, cargo_weight) in metro_routes.items():
            sent_goods[from_station] += cargo_weight
            received_goods[to_station] += cargo_weight

        # 检查需求条件
        for site, cargo_site in self.vrp_data.cargo_site_dict.items():
            net_goods = received_goods[site] - sent_goods[site]  #  收到的 - 送出的
            if cargo_site.cargo_weight > 0:  # 欠缺站点
                if net_goods < cargo_site.cargo_weight:
                    print(f"需求检查失败：欠缺站点 {site} 的净货物量不足，需求为 {cargo_site.cargo_weight}，实际为 {net_goods}")
                    return False
            elif cargo_site.cargo_weight < 0:  # 多余站点
                if net_goods > cargo_site.cargo_weight:
                    print(f"需求检查失败：多余站点 {site} 的净货物量超出需求，需求为 {cargo_site.cargo_weight}，实际为 {net_goods}")
                    return False

        # 检查库存条件
        for site, cargo_site in self.vrp_data.cargo_site_dict.items():
            final_inventory = cargo_site.initial_inventory + received_goods[site] - sent_goods[site]
            if final_inventory < 0:
                print(f"库存检查失败：站点 {site} 的最终库存为负，实际为 {final_inventory}")
                return False
            if final_inventory > cargo_site.capacity:
                print(f"库存检查失败：站点 {site} 的最终库存超过最大限制，实际为 {final_inventory}，限制为 {cargo_site.max_inventory}")
                return False

        # 如果所有检查都通过，返回 True
        return True
    def collabor_ok(self, turck_route, metro_routes):
        # 遍历地铁路径中的每个出发站和到达站
        for (from_station, to_station), (schedule, cargo_weight) in metro_routes.items():
            # 获取地铁的出发时间
            departure_key = (from_station, to_station, schedule)
            if departure_key not in self.vrp_data.departure_times_dict:
                print(f"协同检查失败：地铁班次 {schedule} 从 {from_station} 到 {to_station} 的出发时间缺失")
                return False
            departure_time = self.vrp_data.departure_times_dict[departure_key]

            # 计算地铁的到达时间
            travel_time = self.vrp_data.metro_travel_time.get((from_station, to_station))
            if travel_time is None:
                print(f"协同检查失败：地铁站点之间的旅行时间缺失")
                return False
            arrival_time = departure_time + travel_time

            # 检查卡车路径中的协同条件
            if not self.check_truck_arrival(turck_route, from_station, departure_time, is_departure=True):
                print(f"协同检查失败：卡车未在出发站点 {from_station} 的地铁出发时间 {departure_time} 的半小时内到达")
                return False

            if not self.check_truck_arrival(turck_route, to_station, arrival_time, is_departure=False):
                print(f"协同检查失败：卡车未在到达站点 {to_station} 的地铁到达时间 {arrival_time} 的半小时内到达")
                return False

        # 如果所有检查都通过，返回 True
        return True

    def check_truck_arrival(self, turck_route, station, time, is_departure):
        """
        检查卡车是否满足协同要求。
        如果是地铁出发站点，确保卡车在出发时间的半小时内到达；
        如果是地铁到达站点，确保卡车在到达时间的半小时后到达。
        """
        time_window_start = time - 0.5 if is_departure else time + 0.5
        time_window_end = time if is_departure else time + 1

        for path, arrive_times, _, _, _ in turck_route:
            # 如果路径只包含仓库点，跳过检查
            if len(path) == 1 and path[0] == 0:
                continue

            if station in path:
                idx = path.index(station)
                truck_arrival_time = arrive_times[idx]

                # 检查是否在协同时间窗内
                if time_window_start <= truck_arrival_time <= time_window_end:
                    return True

        # 如果未找到满足条件的卡车到达时间，返回 False
        return False

    def route_info_auth_ok(self, turck_route, metro_routes):
        # 遍历每条路径
        for route in turck_route:
            path, arrive_times, leave_times, workloads, load_history = route

            # 如果路径只包含仓库点，跳过检查
            if len(path) == 1 and path[0] == 0:
                continue

            # 检查载重量是否超载
            for load in load_history:
                if load > self.vrp_data.vehicle_capacity:
                    return False

            # 检查时间窗约束
            for idx, site in enumerate(path):
                if site != 0:  # 跳过仓库站点检查
                    cargo_site = self.vrp_data.cargo_site_dict[site]
                    arrival_time = arrive_times[idx]
                    leave_time = leave_times[idx]

                    # 检查到达时间是否在时间窗内
                    if not (cargo_site.start_time <= arrival_time <= cargo_site.end_time):
                        return False

                    # 检查离开时间是否在时间窗内
                    if leave_time > cargo_site.end_time:
                        return False

        # 检查地铁路径的正确性
        departure_count = {}  # 用于统计每个站点作为出发站点的次数
        arrival_count = {}  # 用于统计每个站点作为到达站点的次数
        for (from_station, to_station), (schedule, cargo_weight) in metro_routes.items():
            # 获取地铁班次的出发时间
            departure_key = (from_station, to_station, schedule)
            if departure_key not in self.vrp_data.departure_times_dict:
                return False

            departure_time = self.vrp_data.departure_times_dict[departure_key]

            # 检查出发站点的时间窗
            from_site = self.vrp_data.cargo_site_dict[from_station]
            if not (from_site.start_time <= departure_time <= from_site.end_time):
                print(f"地铁检查未通过：站点 {from_station} 到 {to_station} 的班次 {schedule} 不存在")
                return False

            # 计算到达时间
            distance = self.vrp_data.metro_travel_time[(from_station, to_station)]
            metro_speed = self.vrp_data.metro_speed  # 假设地铁速度存储在 vrp_data 中
            arrival_time = departure_time + distance / metro_speed

            # 检查到达站点的时间窗
            to_site = self.vrp_data.cargo_site_dict[to_station]
            if not (to_site.start_time <= arrival_time <= to_site.end_time):
                return False

            # 记录出发和到达次数
            departure_count[from_station] = departure_count.get(from_station, 0) + 1
            arrival_count[to_station] = arrival_count.get(to_station, 0) + 1

            # 检查每个站点的出发和到达服务次数
            if departure_count[from_station] > 1:
                return False
            if arrival_count[to_station] > 1:
                return False

        # 如果所有检查都通过，返回 True
        return True

