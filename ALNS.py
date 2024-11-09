from config import *
import ALNSParams as Params
from help_function import QuestionDataHandle, VRPData, createDict, updateDict
from solv import Solution
import help_function
import pprint  # 引入 pprint 模块，便于格式化输出
from algorithm.metro_insert import metro_greedy_repair, metro_intermodal_repair, metro_regret_repair, \
    metro_random_repair
from algorithm.metro_remove import metro_random_destroy, metro_shaw_destroy, metro_zone_destroy, \
    metro_worst_distance_destroy,metro_no_destroy
from algorithm.truck_insert import truck_intermodal_repair, truck_random_repair, truck_greedy_repair, \
    truck_regret_repair
from algorithm.truck_remove import truck_random_destroy, truck_shaw_location_destroy, truck_shaw_demand_destroy,truck_shaw_timewindow_destroy,truck_zone_destroy, \
    truck_worst_distance_destroy
import numpy as np
import random
import time
import copy
import math


class Alns:
    def __init__(self, deposite_list, cargo_site_dict, metro_cargo_site_dict, normal_cargo_site_dict,
                 departure_times_df, ):
        self.params = Params.parameter()
        self.end_temp = self.params.init_temp * self.params.t  # end temperature

        self.metro_destroyList = [metro_random_destroy,
                                  metro_worst_distance_destroy,metro_no_destroy]
        self.truck_destroyList = [truck_random_destroy, truck_shaw_location_destroy, truck_shaw_demand_destroy,truck_shaw_timewindow_destroy,
                                  truck_worst_distance_destroy]
        self.truck_repairList = [truck_intermodal_repair, truck_random_repair, truck_greedy_repair, truck_regret_repair]
        self.metro_repairList = [metro_greedy_repair, metro_intermodal_repair, metro_regret_repair, metro_random_repair]
        self.mix_destroyList  = self.truck_destroyList
        self.mix_repairList = self.truck_repairList + self.metro_repairList

        self.weight_metro_destroy = np.array([1 for _ in range(len(self.metro_destroyList))],
                                             dtype=float)  # 每个destroy算子的权重
        self.weight_metro_repair = np.array([1 for _ in range(len(self.metro_repairList))],
                                            dtype=float)  # 每个repair算子的权重
        self.weight_truck_destroy = np.array([1 for _ in range(len(self.truck_destroyList))],
                                             dtype=float)  # 每个destroy算子的权重
        self.weight_truck_repair = np.array([1 for _ in range(len(self.truck_repairList))],
                                            dtype=float)  # 每个repair算子的权重
        self.metro_operator_time = createDict(self.metro_destroyList + self.metro_repairList)  # 记录每个算子选中次数
        self.metro_operator_score = createDict(self.metro_destroyList + self.metro_repairList)  # 记录每个算子的得分
        self.truck_operator_time = createDict(self.truck_destroyList + self.truck_repairList)  # 记录每个算子选中次数
        self.truck_operator_score = createDict(self.truck_destroyList + self.truck_repairList)  # 记录每个算子的得分

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

            # this is for metro_route operation
            if iter_num % self.params.N_metro == 0:
                start_1 = time.time()
                Destroy = np.random.choice(self.metro_destroyList, p=p_metro_destroy)
                Repair = np.random.choice(self.metro_repairList, p=p_metro_repair)
                sol_before_destroy = current_sol.clone()
                removed_metro_routes, removed_stations = Destroy.destroy(solution=sol_before_destroy,
                                                                         destroy_rate_low=self.destroy_ratio_low,
                                                                         destroy_rate_upper=self.destroy_ratio_upper,
                                                                         vrp_data = self.vrp_data)
                tmp_sol = Repair.repair(solution=sol_before_destroy,
                                        removed_metro_routes = removed_metro_routes,
                                        removed_stations=removed_stations,
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

            else:
                # this is for truck_route operation
                start_2 = time.time()
                Destroy = np.random.choice(self.truck_destroyList, p=p_truck_destroy)
                Repair = np.random.choice(self.truck_repairList, p=p_truck_repair)
                sol_before_destroy = current_sol.clone()
                removed_truck_routes, removed_stations = Destroy.destroy(solution=sol_before_destroy,
                                                                         destroy_rate_low=self.destroy_ratio_low,
                                                                         destroy_rate_upper=self.destroy_ratio_upper,
                                                                         vrp_data = self.vrp_data)
                tmp_sol = Repair.repair(solution=sol_before_destroy,
                                        removed_truck_routes = removed_truck_routes,
                                        removed_stations=removed_stations,
                                        vrp_data = self.vrp_data)
                end_2 = time.time()
                # print(end_1-start_1)
                time_2 += end_2 - start_2  # operator operation time
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





