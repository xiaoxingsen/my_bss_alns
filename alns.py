from config import *
from base import QuestionDataHandle,VRPData
from solv import Solution
# from alns_destory import car_route_random_metro,car_route_random_normal,car_route_worst_metro,car_route_worst_normal, metro_route_random, metro_route_worst
import pprint  # 引入 pprint 模块，便于格式化输出

class Alns:
    def __init__(self, deposite_list, cargo_site_dict,metro_cargo_site_dict,normal_cargo_site_dict,departure_times_df,):
        self.vrp_data = VRPData(deposite_list, cargo_site_dict,metro_cargo_site_dict,normal_cargo_site_dict,departure_times_df,)
        self.solution = Solution(self.vrp_data)
        self.best_solution = self.solution.clone()
        self.removal_operators_list = ['shaw', 'distance', 'worst', 'worst_replenishment_time', 'random']
        self.insertion_operators_list = ['greedy', '2_regret', 'shaw','intermodal_1','intermodal_2', 'random']



