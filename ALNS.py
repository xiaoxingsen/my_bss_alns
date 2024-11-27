from config import *
import ALNSParams as Params
from help_function import QuestionDataHandle, VRPData, createDict, updateDict
from solv import Solution
import help_function
import pprint  # 引入 pprint 模块，便于格式化输出
from algorithm.metro_insert import metro_greedy_repair, metro_intermodal_repair, metro_regret_repair, \
    metro_random_repair,metro_no_repair
from algorithm.metro_remove import metro_random_destroy, metro_shaw_destroy, metro_zone_destroy, \
    metro_worst_distance_destroy,metro_no_destroy
from algorithm.truck_insert import truck_intermodal_repair, truck_random_repair, truck_greedy_repair, \
    truck_regret_dis_repair
from algorithm.truck_remove_normal import normal_random_destroy, normal_shaw_location_destroy, normal_shaw_demand_destroy,normal_shaw_timewindow_destroy,normal_zone_destroy, \
    normal_worst_distance_destroy
from algorithm.truck_remove_metro import Mstation_random_destroy,Mstation_zone_destroy,Mstation_shaw_demand_destroy,Mstation_shaw_location_destroy,Mstation_shaw_timewindow_destroy,Mstation_worst_distance_destroy
import numpy as np
import random
import time
import copy
import math
import logging

class Alns:
    def __init__(self, deposite_list, cargo_site_dict, metro_cargo_site_dict, normal_cargo_site_dict,
                 departure_times_df, ):
        self.params = Params.parameter()
        self.end_temp = self.params.init_temp * self.params.t  # end temperature

        self.metro_destroyList = [metro_random_destroy,
                                  metro_worst_distance_destroy,metro_no_destroy]
        self.truck_destroyList = [normal_random_destroy, normal_shaw_location_destroy, normal_shaw_demand_destroy,normal_shaw_timewindow_destroy,normal_zone_destroy,normal_worst_distance_destroy]
        self.truck_repairList = [truck_intermodal_repair, truck_random_repair, truck_greedy_repair, truck_regret_dis_repair]
        self.metro_repairList = [metro_greedy_repair, metro_intermodal_repair, metro_regret_repair, metro_random_repair,metro_no_repair]
        self.truck_Mstation_destroyList  = [Mstation_random_destroy,Mstation_zone_destroy,Mstation_shaw_demand_destroy,Mstation_shaw_location_destroy,Mstation_shaw_timewindow_destroy,Mstation_worst_distance_destroy]
        self.truck_Mstation_repairList = self.truck_repairList + self.metro_repairList

        self.weight_metro_destroy = np.array([1 for _ in range(len(self.metro_destroyList))],
                                             dtype=float)  # 每个destroy算子的权重
        self.weight_metro_repair = np.array([1 for _ in range(len(self.metro_repairList))],
                                            dtype=float)  # 每个repair算子的权重
        self.weight_truck_destroy = np.array([1 for _ in range(len(self.truck_destroyList))],
                                             dtype=float)  # 每个destroy算子的权重
        self.weight_truck_repair = np.array([1 for _ in range(len(self.truck_repairList))],
                                            dtype=float)  # 每个repair算子的权重
        self.weight_truck_Mstation_destroy = np.array([1 for _ in range(len(self.truck_Mstation_destroyList))],
                                             dtype=float)  # 每个destroy算子的权重
        self.weight_truck_Mstation_repair = np.array([1 for _ in range(len(self.truck_Mstation_repairList))],
                                            dtype=float)  # 每个repair算子的权重
        self.metro_operator_time = createDict(self.metro_destroyList + self.metro_repairList)  # 记录每个算子选中次数
        self.metro_operator_score = createDict(self.metro_destroyList + self.metro_repairList)  # 记录每个算子的得分
        self.truck_operator_time = createDict(self.truck_destroyList + self.truck_repairList)  # 记录每个算子选中次数
        self.truck_operator_score = createDict(self.truck_destroyList + self.truck_repairList)  # 记录每个算子的得分
        self.truck_Mstation_operator_time = createDict(self.truck_Mstation_destroyList + self.truck_Mstation_repairList)
        self.truck_Mstation_operator_score = createDict(self.truck_Mstation_destroyList + self.truck_Mstation_repairList)

        self.vrp_data = VRPData(deposite_list, cargo_site_dict, metro_cargo_site_dict, normal_cargo_site_dict,
                                departure_times_df, )
        # self.solution = Solution(self.vrp_data)
        # self.best_solution = self.solution.clone()

        # other param
        self.destroy_ratio_low = self.params.drate_low
        self.destroy_ratio_upper = self.params.drate_upper

        # metrics
        self.run_time = None
        self.bestVal = None
        self.bestVal_iter = None
        self.currentVal_iter = None

        # get initial solution
        self.init_sol = Solution(self.vrp_data)

        # solution
        self.best_sol = None

        # iteration time
        self.iter_time = None

        self.time_limit = self.params.time_limit

        self.print_log = True

    def updateWeight(self, operator, used: bool, model: str):
        """
        update operator's weight
        :param operator: the chosen operator
        :param used: equals True if the operator has been used
        :param model: Select to update the weight of that operator
        :return: None
        """
        if model == 'metro':
            if operator in self.metro_destroyList:
                ind = self.metro_destroyList.index(operator)
                if used is False:
                    self.weight_metro_destroy[ind] = self.weight_metro_destroy[ind] * (1 - self.params.r)
                else:
                    self.weight_metro_destroy[ind] = self.weight_metro_destroy[ind] * (1 - self.params.r) + \
                                               self.params.r * self.metro_operator_score[operator] / self.metro_operator_time[
                                                   operator]
        else:
            if operator in self.truck_destroyList:
                ind = self.truck_destroyList.index(operator)
                if used is False:
                    self.weight_truck_destroy[ind] = self.weight_truck_destroy[ind] * (1 - self.params.r)
                else:
                    self.weight_truck_destroy[ind] = self.weight_truck_destroy[ind] * (1 - self.params.r) + \
                                               self.params.r * self.truck_operator_score[operator] / self.truck_operator_time[
                                                   operator]


    def run(self):
        """
        process of the alns search
        :param self:
        :return:
        """
        global_sol = self.init_sol.clone()
        current_sol = self.init_sol.clone()
        # global_sol = copy.deepcopy(self.init_sol)  # global best  # 当前已知的全局最佳解
        # current_sol = copy.deepcopy(self.init_sol)  # 当前迭代的解

        bestVal_list = []
        # currentVal = []
        bestVal_iter = []
        currentVal_iter = []

        bestVal_list.append(global_sol.obj)
        # currentVal.append(current_sol.total_cost)
        bestVal, currentVal = global_sol.obj, current_sol.obj
        noImprove = 0  # number of iterations that not improve  计数多少次迭代没有找到更优解

        start = time.time()
        temp = self.params.init_temp  # initial temperature  模拟退火的初始温度
        iter_num = 0  # iteration times  当前的迭代次数
        time_1 = 0
        time_2 = 0
        time_3 = 0

        while iter_num < self.params.iter_time and time.time() - start < self.time_limit:

            # logging.info(f'{iter_num}')
            # weight list of destroy operators
            p_truck_destroy = self.weight_truck_destroy / sum(self.weight_truck_destroy)
            # weight list of repair operators
            p_truck_repair = self.weight_truck_repair / sum(self.weight_truck_repair)

            p_metro_destroy = self.weight_metro_destroy / sum(self.weight_metro_destroy)

            p_metro_repair = self.weight_metro_repair / sum(self.weight_metro_repair)


            if iter_num % self.params.N_metro == 0:
                # this is for metro_route operation

                start_1 = time.time()
                Destroy = np.random.choice(self.metro_destroyList, p=p_metro_destroy)
                Repair = np.random.choice(self.metro_repairList, p=p_metro_repair)
                sol_before_destroy = current_sol.clone()
                removed_metro_routes, metro_routes_to_repair= Destroy.destroy(solution=sol_before_destroy,
                                                                         destroy_rate_low=self.destroy_ratio_low,
                                                                         destroy_rate_upper=self.destroy_ratio_upper,
                                                                         vrp_data = self.vrp_data)
                tmp_sol = Repair.repair(solution=sol_before_destroy,
                                        removed_truck_routes = sol_before_destroy.truck_route,
                                        removed_stations= None,
                                        removed_metro_routes = removed_metro_routes,
                                        metro_routes_to_repair = metro_routes_to_repair,
                                        vrp_data = self.vrp_data)
                end_1 = time.time()
                # print(end_1-start_1)
                time_1 += end_1 - start_1  # operator operation time
                self.metro_operator_time = updateDict(self.metro_operator_time, Destroy, Repair, 1)

                tmpVal = tmp_sol.obj
                # simulated annealing acceptance
                acc_p = math.exp((tmpVal - current_sol.obj) / temp) if temp > 0.05 else 0

                # better than global best  优于全局最佳值
                if tmpVal > global_sol.obj:
                    global_sol = tmp_sol
                    current_sol = copy.deepcopy(tmp_sol)
                    bestVal_list.append(tmpVal)
                    bestVal, currentVal = tmp_sol.obj, tmp_sol.obj
                    self.metro_operator_score = updateDict(self.metro_operator_score, Destroy, Repair,
                                                           self.params.theta1)
                    noImprove = 0

                # better than current sol  优于当前解 current_sol，但未达到全局最优
                elif tmpVal > current_sol.obj:
                    current_sol = tmp_sol
                    currentVal = tmp_sol.obj
                    self.metro_operator_score = updateDict(self.metro_operator_score, Destroy, Repair,
                                                           self.params.theta2)

                # accord with the accept rule  依照模拟退火准则接受
                elif acc_p > random.random():
                    current_sol = copy.deepcopy(tmp_sol)
                    currentVal = tmp_sol.obj
                    self.metro_operator_score = updateDict(self.metro_operator_score, Destroy, Repair,
                                                           self.params.theta3)
                    noImprove += 1

                # deposit  不满足任何条件的情况（不接受新解）
                else:
                    self.metro_operator_score = updateDict(self.metro_operator_score, Destroy, Repair,
                                                           self.params.theta4)
                    noImprove += 1

            elif iter_num % self.params.N_truck_Mstation == 0:

                # this is for truck_route metro operation
                start_2 = time.time()
                Destroy = np.random.choice(self.truck_Mstation_destroyList, p=p_metro_destroy)
                Repair = np.random.choice(self.truck_Mstation_repairList, p=p_metro_repair)
                sol_before_destroy = current_sol.clone()
                removed_truck_routes, removed_stations = Destroy.destroy(solution=sol_before_destroy,
                                                                         destroy_rate_low=self.destroy_ratio_low,
                                                                         destroy_rate_upper=self.destroy_ratio_upper,
                                                                         vrp_data = self.vrp_data)

                tmp_sol = Repair.repair(solution=sol_before_destroy,
                                        removed_truck_routes = removed_truck_routes,
                                        removed_stations=removed_stations,
                                        removed_metro_routes = sol_before_destroy.metro_routes,
                                        metro_routes_to_repair = None,
                                        vrp_data = self.vrp_data)
                end_2 = time.time()
                # print(end_1-start_1)
                time_2 += end_2 - start_2  # operator operation time
                self.truck_Mstation_operator_time = updateDict(self.truck_Mstation_operator_time, Destroy, Repair, 1)

                tmpVal = tmp_sol.obj
                # simulated annealing acceptance
                acc_p = math.exp((tmpVal - current_sol.obj) / temp) if temp > 0.05 else 0

                # better than global best  优于全局最佳值
                if tmpVal > global_sol.obj:
                    global_sol = tmp_sol
                    current_sol = copy.deepcopy(tmp_sol)
                    bestVal_list.append(tmpVal)
                    bestVal, currentVal = tmp_sol.obj, tmp_sol.obj
                    self.truck_Mstation_operator_score = updateDict(self.truck_Mstation_operator_score, Destroy, Repair,
                                                           self.params.theta1)
                    noImprove = 0

                # better than current sol  优于当前解 current_sol，但未达到全局最优
                elif tmpVal > current_sol.obj:
                    current_sol = tmp_sol
                    currentVal = tmp_sol.obj
                    self.truck_Mstation_operator_score = updateDict(self.truck_Mstation_operator_score, Destroy, Repair,
                                                           self.params.theta2)

                # accord with the accept rule  依照模拟退火准则接受
                elif acc_p > random.random():
                    current_sol = copy.deepcopy(tmp_sol)
                    currentVal = tmp_sol.obj
                    self.truck_Mstation_operator_score = updateDict(self.truck_Mstation_operator_score, Destroy, Repair,
                                                           self.params.theta3)
                    noImprove += 1

                # deposit  不满足任何条件的情况（不接受新解）
                else:
                    self.truck_Mstation_operator_score = updateDict(self.truck_Mstation_operator_score, Destroy, Repair,
                                                           self.params.theta4)
                    noImprove += 1


            else:

                # this is for truck_route normal operation
                start_3 = time.time()
                Destroy = np.random.choice(self.truck_destroyList, p=p_truck_destroy)
                Repair = np.random.choice(self.truck_repairList, p=p_truck_repair)
                sol_before_destroy = current_sol.clone()
                while max_try_times:
                    removed_truck_routes, removed_stations = Destroy.destroy(solution=sol_before_destroy,
                                                                         destroy_rate_low=self.destroy_ratio_low,
                                                                         destroy_rate_upper=self.destroy_ratio_upper,
                                                                         vrp_data = self.vrp_data)
                    tmp_sol = Repair.repair(solution=sol_before_destroy,
                                        removed_truck_routes = removed_truck_routes,
                                        removed_stations=removed_stations,
                                        removed_metro_routes = sol_before_destroy.metro_routes,
                                        metro_routes_to_repair = None,
                                        vrp_data = self.vrp_data)


                    tmp_sol = self.update_solution(tmp_sol, self.vrp_data)

                    if tmp_sol.is_feasible():
                        break
                end_3 = time.time()
                # print(end_1-start_1)
                time_3 += end_3 - start_3  # operator operation time
                self.truck_operator_time = updateDict(self.truck_operator_time, Destroy, Repair, 1)

                tmpVal = tmp_sol.obj
                # simulated annealing acceptance
                acc_p = math.exp((tmpVal - current_sol.obj) / temp) if temp > 0.05 else 0

                # better than global best  优于全局最佳值
                if tmpVal > global_sol.obj:
                    global_sol = tmp_sol
                    current_sol = copy.deepcopy(tmp_sol)
                    bestVal_list.append(tmpVal)
                    bestVal, currentVal = tmp_sol.obj, tmp_sol.obj
                    self.truck_operator_score = updateDict(self.truck_operator_score, Destroy, Repair,
                                                           self.params.theta1)
                    noImprove = 0

                # better than current sol  优于当前解 current_sol，但未达到全局最优
                elif tmpVal > current_sol.obj:
                    current_sol = tmp_sol
                    currentVal = tmp_sol.obj
                    self.truck_operator_score = updateDict(self.truck_operator_score, Destroy, Repair,
                                                           self.params.theta2)

                # accord with the accept rule  依照模拟退火准则接受
                elif acc_p > random.random():
                    current_sol = copy.deepcopy(tmp_sol)
                    currentVal = tmp_sol.obj
                    self.truck_operator_score = updateDict(self.truck_operator_score, Destroy, Repair,
                                                           self.params.theta3)
                    noImprove += 1

                # deposit  不满足任何条件的情况（不接受新解）
                else:
                    self.truck_operator_score = updateDict(self.truck_operator_score, Destroy, Repair,
                                                           self.params.theta4)
                    noImprove += 1

            # end the removal and insertion operation, try to update the weights
            if iter_num % self.params.fre_metro == 0:
                # update the weights of the metro
                for operator in self.metro_operator_time:
                    if self.metro_operator_time[operator] == 0:
                        self.updateWeight(operator=operator, used=False, model='metro')  # never used
                    else:
                        self.updateWeight(operator=operator, used=True, model='metro')  # used

                bestVal_iter.append(bestVal)
                currentVal_iter.append(currentVal)

            if iter_num % self.params.fre_truck == 0:
                # update the weights of the truck
                for operator in self.truck_operator_time:
                    if self.truck_operator_time[operator] == 0:
                        self.updateWeight(operator=operator, used=False, model='truck')  # never used
                    else:
                        self.updateWeight(operator=operator, used=True, model='truck')  # used

                bestVal_iter.append(bestVal)
                currentVal_iter.append(currentVal)

            temp = temp * self.params.c
            iter_num += 1


            if iter_num % 20 == 0 and self.print_log:
                print('iter_num:', iter_num)
                print('bestVal:', bestVal)
                print('currentVal:', currentVal)
                print('temp:', temp)
                print('noImprove:', noImprove)
                print('time_1:', time_1)
                print('time_2:', time_2)
                print('time_3:', time_3)
                print('--------------------------------------')
            if iter_num % 100 == 0 and self.print_log:
                print('repositioning cost: {}'.format(sum(current_sol.costs)))
                print('no repositioning cost: {}'.format(current_sol.unvisited_sum))
                print('current routes: {}'.format(current_sol.routes))
                print('current costs: {}'.format(current_sol.costs))
                print('current instructs: {}'.format(current_sol.instructs))

        self.iter_time = iter_num
        end = time.time()
        self.run_time = end - start

        # update solution and metrics
        self.best_sol = global_sol
        self.bestVal_iter = bestVal_iter
        self.currentVal_iter = currentVal_iter

        # 输出运行时间和各算子使用次数
        print('time span:%.2f\n' % self.run_time)
        # print('最优值：', globalSol.totalCost)
        print('bestVal:', bestVal)
        # print('currentVal:', currentVal)
        # print('最优解：', globalSol)
        for key, value in self.metro_operator_time.items():
            print('{}:{}'.format(key.__name__, value))
        for key, value in self.truck_operator_time.items():
            print('{}:{}'.format(key.__name__, value))

    def update_solution(self,solution, vrp_data):
        """
            更新解决方案中的各项指标，包括卡车作业量、地铁运输量、地铁班次和卡车到达时间。
            :param solution: 当前解决方案
            :param vrp_data: 问题数据，包含所有必需的距离和时间信息
            """
        # 找出卡车路径下的所有地铁站点
        truck_metro_stations = set()
        for route in solution.truck_route:
            path, _, _, _, _ = route
            for site in path:
                if site in vrp_data.metro_sites:  # 如果站点是地铁站点
                    truck_metro_stations.add(site)

        # 确定同时作为出发站和到达站的地铁站点
        metro_as_both = set()
        departures = {k[0] for k in solution.metro_routes.keys()}
        arrivals = {k[1] for k in solution.metro_routes.keys()}
        for station in truck_metro_stations:
            if station in departures and station in arrivals:
                metro_as_both.add(station)
        # 找出所有有地铁线路连接的地铁站点
        all_connected_metro_stations = departures.union(arrivals)

        item = 0

        while item > 10:
            # 创建需求字典的副本以实时调整需求
            site_demand = copy.deepcopy(vrp_data.site_demand)
            site_inventory = copy.deepcopy(vrp_data.site_inventory)
            # 获取地铁路线的列表并随机打乱
            metro_route_items = list(solution.metro_routes.items())
            random.shuffle(metro_route_items)
            # 随机顺序更新地铁路线
            for key, (schedule, _) in metro_route_items:
                from_station, to_station = key
                # 获取出发站和到达站的当前需求
                from_demand = site_demand[from_station]
                to_demand = site_demand[to_station]

                # 准备选择运输量的候选列表
                candidates = [abs(from_demand), abs(to_demand)]
                if from_demand < 0:
                    from_inventory = vrp_data.cargo_site_dict[from_station].inventory
                    candidates.append(from_inventory)
                if to_demand < 0:
                    to_inventory = vrp_data.cargo_site_dict[to_station].inventory
                    candidates.append(to_inventory)

                # 从候选列表中随机选择一个值作为新的运输量
                if candidates:  # 确保列表非空
                    new_cargo_weight = random.choice(candidates)

                    # 更新站点需求
                    site_demand[from_station] += new_cargo_weight  # 出发站的需求增加运输量
                    site_demand[to_station] -= new_cargo_weight  # 到达站的需求减去运输量
                    site_inventory[from_station] -= new_cargo_weight  # 出发站的库存减去运输量
                    site_inventory[to_station] += new_cargo_weight  # 到达站的库存增加运输量
                    # 更新解决方案
                    solution.metro_routes[key] = (schedule, new_cargo_weight)

            # 更新卡车路径的作业量和装载量
            # 遍历每条卡车路径
            for route in solution.truck_route:
                cost, instruct = self.dp_route_workload(route,site_demand,site_inventory, capacity)
                # 更新路线中的作业量和装载历史
                route[3] = new_workloads
                route[4] = new_load_history

            item += 1



        # 更新卡车路径
        for route in solution.truck_route:
            path, arrive_times, leave_times, workloads, load_history = route
            for i in range(1, len(path)):
                # 更新到达时间和离开时间
                if i == 1:  # 出发点
                    arrive_times[i] = vrp_data.start_time  # 假设所有卡车在某个统一时间出发
                else:
                    travel_time = vrp_data.cargo_site_dis[path[i - 1], path[i]] / vrp_data.truck_speed
                    arrive_times[i] = leave_times[i - 1] + travel_time

                # 模拟作业时间处理
                processing_time = vrp_data.processing_times[path[i]]
                leave_times[i] = arrive_times[i] + processing_time

                # 更新作业量
                workloads[i] = vrp_data.demands[path[i]]  # 假设作业量是需求量

                # 更新载货历史（假设卡车从仓库装满货物出发）
                if i == 1:
                    load_history[i] = vrp_data.truck_capacity
                else:
                    load_history[i] = max(0, load_history[i - 1] - workloads[i - 1])



        return solution

    def time_feasible_route(self,path):
        assert len(path) >= 1, f'route {path} is too short to be feasible.'
        if len(path) == 1:  # the starting point
            return True
        else:
            total_travle_time = sum([self.vrp_data.truck_travel_time[(path[i], path[i+1])] for i in range(len(path)-1) ])
            return total_travle_time <= T_end
    # gpt 版本  我的有错误的话  用gpt的改
    # def truck_loading_dp(path, site_demand, site_inventory, qc, capacity):
    #     n = len(path)
    #     # dp[i][j]: 到达第i个站点，卡车内货物量为j时的最小总装卸货量
    #     dp = [[float('inf')] * (qc + 1) for _ in range(n)]
    #
    #     # 从仓库出发时允许任何装载量，装卸货量为0
    #     for j in range(qc + 1):
    #         dp[0][j] = 0
    #
    #     # 跟踪装卸操作，记录在每个站点最佳装卸货量
    #     operations = [[None] * (qc + 1) for _ in range(n)]
    #
    #     # 动态规划处理每个站点
    #     for i in range(1, n):
    #         site = path[i]
    #         demand = site_demand[site]
    #         current_inventory = site_inventory[site]
    #
    #         for j in range(qc + 1):  # 当前站点可能的装载量
    #             for k in range(max(0, j - current_inventory), min(qc, j + capacity) + 1):  # 上一个站点可能的装载量
    #                 load_or_unload = j - k  # 正为装货，负为卸货
    #                 unload = max(load_or_unload, 0)
    #                 load = max(-load_or_unload, 0)
    #
    #                 # 确保不超过站点需求和库存限制
    #                 if load <= current_inventory and -unload <= demand:
    #                     # 累积装卸货操作量
    #                     if dp[i - 1][k] + abs(load_or_unload) < dp[i][j]:
    #                         dp[i][j] = dp[i - 1][k] + abs(load_or_unload)
    #                         operations[i][j] = load_or_unload
    #
    #     # 找到成本最小的最后状态
    #     min_cost = min(dp[n - 1])
    #     current_load = dp[n - 1].index(min_cost)
    #
    #     # 回溯找到每个站点的操作
    #     result_operations = [None] * n
    #     for i in range(n - 1, 0, -1):
    #         result_operations[i] = operations[i][current_load]
    #         current_load -= operations[i][current_load]
    #
    #     return result_operations, min_cost
    def dp_route_workload(self,route,site_demand,site_inventory, cursite_max_inventory):
        # 更新卡车路径的作业量和装载量
        # 遍历每条卡车路径
        p, _, _, workloads, load_history = route
        # 检查路径 r 是否在剩余时间 t_left 下可行。
        if not self.time_feasible_route(p):
            cost = -1
            instruct = [None for _ in range(len(p))]
        else:
            minus_M = -1000  # unvisited  # 标记未访问
            false_flag = -10000  # infeasible  # 标记不可行路径
            path = list(p)
            station_num = len(path)
            level_num = qc + 1   # number of levels of load on van  # 车辆的负载级数
            # eward_arr 和 trace_arr：动态规划表，用于记录每个站点在不同载重状态下的奖励值和追溯路径的状态。
            # reward_arr[k, i] 表示在第 i 个站点、载重为 k 时的最大需求满足值；trace_arr 用于记录路径选择，便于在计算完成后回溯最优路径。
            reward_arr, trace_arr = np.full((level_num, station_num), minus_M), np.full((level_num, station_num),minus_M)
            for j in range(level_num):
                reward_arr[j][0] = 0
            t_trip,t_spend_on_route = 0,0
            for i in range(1, station_num):
                site = path[i]
                demand = site_demand[site]
                current_inventory = site_inventory[site]
                t_trip += self.vrp_data.truck_travel_time[(path[i - 1], path[i])]
                t_spend_on_route += self.vrp_data.truck_travel_time[(path[i - 1], path[i])]
                for k in range(level_num):
                    for former_k in range(level_num):
                        if reward_arr[former_k, i - 1] == false_flag:  # infeasible
                            pass
                        else:
                            ins = former_k - k  # before - after  正为卸货  负为装货
                            # former_k 上一个站点可行时的最小需求满足值
                            # 找到能满足在former_k的前提下  找到能满足当前站点需求的所有k值
                            # 需求为正，表示需要卸货   ins  需大于0且大于该需求 ins-demand >= 0 ; 保证卸货后不能超过库存 current_inventory + ins < cap
                            # 需求为负，表示需要装货   ins  需小于0且小于该需求 ins-demand <=0  ;  因为 k 和 former_k都是在车辆库存限制里,所以不需要考虑车辆库存限制
                            if (demand > 0 and 0 <= ins-demand and current_inventory + ins <= cursite_max_inventory) or \
                               (demand < 0 and 0 >= ins - demand ):
                                station_cost = abs(ins)
                                if station_cost + reward_arr[former_k, i - 1] > reward_arr[k, i]:
                                    reward_arr[k, i] = station_cost + reward_arr[former_k, i - 1]
                                    trace_arr[k, i] = former_k

                    else:
                        if reward_arr[k, i] == minus_M:  # unable to reach this state
                            reward_arr[k, i] = false_flag
                            trace_arr[k, i] = false_flag

            if max(reward_arr[:, -1]) == false_flag:
                cost = -1
                instruct = [None for _ in range(len(p))]
            else:
                profit_ind = np.argmin(reward_arr, axis=0)[-1]
                trace_init = trace_arr[profit_ind, -1]
                min_cost = reward_arr[profit_ind, -1]
                # trace path
                trace_list, trace = [profit_ind, trace_init], trace_init
                for i in range(station_num - 2, -1, -1):
                    if trace < -1000:
                        logging.warning('here')
                    trace = trace_arr[int(trace), i]
                    trace_list.append(trace)
                assert len(trace_list) == station_num + 1
                trace_list = list(reversed(trace_list))
                instruct = [(trace_list[k] - trace_list[k + 1]) for k in range(len(trace_list) - 1)]
                cost = min_cost
        return cost, instruct




















