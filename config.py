import pickle
from collections import namedtuple, defaultdict
import random
import numpy as np
from scipy.spatial.distance import pdist, squareform
import copy
from functools import wraps


args = {}
# ***** start config *****
num_normal_stations = 5
num_metro_stations = 3
num_customers = num_normal_stations + num_metro_stations
num_stations = num_normal_stations + num_metro_stations  # 总站点数量
total_service_minutes = 480
intervals = [10, 15, 20]
vehicle_speed = 3
num_trucks = 5
metrospeed_ration = 2  # 地铁速度是卡车速度的几倍
qc = 50  # 假设卡车的载量
qm = 40  # 假设地铁的载量
# 假设每辆车的派出固定成本
Cf = 50
# 假设每分钟的搬迁成本
Cc1 = 2
# 假设每分钟的货车运营成本
Cc2 = 1
# 假设每分钟的地铁搬迁成本
Cm1 = 0.5
# 假设每分钟的地铁运营成本
Cm2 = 0.6
# 假设每个单位货币的库存相关惩罚成本
Cp = 1000
# 设置每装卸一辆单车所需要的人工时间 （分钟）
tc = 1  # 货车
tm = 5  # 地铁
T_end = 60  # 所有车辆必须完成旅行的截止时间
T_cor = 30
T_DAY = 480
car_speeds = (3.05, 3.0, 2.95)
# **** 算法配置
max_iter = 5000
clear_adap_iter = 1000  # 每迭代多少次，清理一下自适应信息
volatil_factor = 0.4  # 挥发速度
path_destroy_min = 1
path_destroy_max = 3
max_try_times = 200  # 设得越大 单次搜索时间加大 但搜到feasible solution可能性也越大  太小了可能 单次总是搜不到feasible solution
accept_scores = (1.5, 1.2, 0.8, 0.5)
max_car_no = 999
capacity = 150
# ***** end config *****

# 配置计算 及 其他定义

deposite_info = namedtuple("deposite_info", ("location_x", "location_y",
                                             "start_time", "end_time", "capacity", "initial_inventory",
                                             "desired_inventory"))
cargo_site_info = namedtuple("cargo_site_info", ("location_x", "location_y", "cargo_weight",
                                                 "start_time", "end_time", "capacity", "initial_inventory",
                                                 "desired_inventory","if_metro_station"))