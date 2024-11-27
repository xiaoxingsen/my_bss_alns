from config import *

from algorithm.metro_insert import metro_greedy_repair, metro_intermodal_repair, metro_regret_repair, \
    metro_random_repair
from algorithm.metro_remove import metro_random_destroy, metro_shaw_destroy, metro_zone_destroy, \
    metro_worst_distance_destroy
from algorithm.truck_insert import truck_intermodal_repair, truck_random_repair, truck_greedy_repair, \
    truck_regret_dis_repair
from algorithm.truck_remove_normal import normal_random_destroy, normal_shaw_location_destroy, normal_zone_destroy, \
    normal_worst_distance_destroy

class QuestionDataHandle:
    def __init__(self):
        pass

    def get_data(self, pick_file):
        # 读取pickle文件
        with open(pick_file, 'rb') as f:
            data = pickle.load(f)

        # 提取各个DataFrame
        points_df = data['points_data']
        distance_matrix_df = data['distance_matrix']
        time_matrix_df = data['time_matrix']
        metro_travel_times = data['metro_travel_times']
        metro_schedule_df = data['metro_schedule']
        departure_times_df = data['departure_times']
        riv_ijk_indices_df = data['riv_ijk_indices']
        deposite_loc = []
        cargo_site_list = []
        cargo_site_dict = {}
        metro_cargo_site_dict = {}
        normal_cargo_site_dict = {}
        for index, row in points_df.iterrows():
            if row['Station Index'] == 0:  # 仓库点 (第一个和最后一个点)
                deposite_x = row['x']
                deposite_y = row['y']
                deposite_loc.append([deposite_x, deposite_y])
            elif row['Station Index'] == points_df.shape[0] - 1:
                break
            else:
                cargo_site = cargo_site_info(
                    location_x=row['x'],
                    location_y=row['y'],
                    cargo_weight=row['demand'],
                    start_time=row['time_window_start'],
                    end_time=row['time_window_end'],
                    capacity=row['capacity'],
                    initial_inventory=row['initial_inventory'],
                    desired_inventory=row['desired_inventory'],
                    if_metro_station=row['if_metro_station']
                )
                cargo_site_list.append(cargo_site)
                cargo_site_dict[index] = cargo_site
                if row['if_metro_station']:
                    metro_cargo_site_dict[index] = cargo_site
                else:
                    normal_cargo_site_dict[index] = cargo_site

        return deposite_loc, cargo_site_dict, metro_cargo_site_dict, normal_cargo_site_dict, points_df, distance_matrix_df, time_matrix_df, metro_travel_times, metro_schedule_df, departure_times_df, riv_ijk_indices_df


class VRPData:
    def __init__(self, deposite_loc, cargo_site_dict, metro_cargo_site_dict, normal_cargo_site_dict,
                 departure_times_df, ):
        self.deposite_loc = deposite_loc
        # 各站点信息字典
        self.cargo_site_dict = cargo_site_dict
        # 地铁站点信息字典
        self.metro_cargo_site_dict = metro_cargo_site_dict
        # 普通站点信息字典
        self.normal_cargo_site_dict = normal_cargo_site_dict
        # 所有站点编号
        self.all_sites = list(self.cargo_site_dict.keys())
        # 普通站点编号
        self.normal_sites = list(self.normal_cargo_site_dict.keys())
        # 地铁站点编号
        self.metro_sites = list(self.metro_cargo_site_dict.keys())
        # self.deposite_location = [(dep.location_x, dep.location_y) for dep in deposite_list]
        # 各站点的位置字典
        self.cargo_site_loc = [(cargo_site.location_x, cargo_site.location_y) for cargo_site in
                               cargo_site_dict.values()]
        # 地铁站点的位置字典
        self.metro_cargo_site_loc = [(metro_ccargo_site.location_x, metro_ccargo_site.location_y) for metro_ccargo_site
                                     in
                                     metro_cargo_site_dict.values()]

        # 站点需求字典
        self.site_demand = {site_id: site.cargo_weight for site_id, site in cargo_site_dict.items()}
        # 站点起始库存字典
        self.site_inventory = {site_id: site.initial_inventory for site_id, site in cargo_site_dict.items()}

        # 各站点到仓库的距离
        self.cargo_site_dep_dis = {}
        # 站点之间的距离字典
        self.cargo_site_dis = {}
        # 地铁站点之间的地铁距离字典
        self.metro_metro_dis = {}

        self.departure_times_dict = departure_times_df['Departure Time'].to_dict()
        self.sorted_distances = {}  # 新增的字典，用于存储每个站点到其他站点的排序后的距离信息
        # 车辆平均速度
        self.average_speed = vehicle_speed
        self.metro_speed = vehicle_speed * metrospeed_ration

        # 卡车旅行时间字典
        self.truck_travel_time = {}
        # 地铁旅行时间字典
        self.metro_travel_time = {}

        self.dis_cal()
        self.calculate_travel_times()
        self.sort_distances()
        self.metro_farthest_station_dict = {}
        self.cal_metro_farthest_station()
        self.vehicle_capacity = qc
        self.fixed_cost = Cf  # 每辆卡车的固定成本系数
        self.handling_cost_per_unit = Cc1  # 每单位搬运货物的成本
        self.travel_cost_per_unit_distance = Cc2  # 每单位距离的旅行时间成本
        self.metro_transport_cost_per_unit = Cm1  # 每单位地铁运输量的成本
        self.num_trucks = num_trucks





    def dis_cal(self):
        (dep_location_x, dep_location_y) = self.deposite_loc[0]
        # 计算仓库到每个货场站点的距离，并存入 cargo_site_dep_dis 和 cargo_site_dis
        for cargo_ix, cargo_site in self.cargo_site_dict.items():
            distance_to_depot = np.linalg.norm(
                np.array([dep_location_x, dep_location_y]) - np.array([cargo_site.location_x, cargo_site.location_y])
            )
            # 存储仓库到货场的距离
            self.cargo_site_dep_dis[cargo_ix] = distance_to_depot
            self.cargo_site_dis[(0, cargo_ix)] = distance_to_depot  # 假设仓库索引为 0
            self.cargo_site_dis[(cargo_ix, 0)] = distance_to_depot  # 双向距离
        cargo_site_keys = list(self.cargo_site_dict.keys())
        cargo_site_array = np.array([self.cargo_site_dict[key] for key in cargo_site_keys])
        distance_matrix = squareform(pdist(cargo_site_array))
        # distance_matrix = squareform(pdist(np.array(self.cargo_site_loc)))
        # 将距离矩阵转换为字典 cargo_site_dis，key为（货场，货场），值为两个货场之间的距离
        num_cargo_sites = distance_matrix.shape[0]
        for i in range(num_cargo_sites):
            for j in range(num_cargo_sites):
                if i != j:
                    self.cargo_site_dis[(cargo_site_keys[i], cargo_site_keys[j])] = \
                        distance_matrix[i, j]

        # 计算地铁站点之间的距离矩阵
        metro_cargo_site_keys = list(self.metro_cargo_site_dict.keys())
        metro_cargo_site_array = np.array([self.metro_cargo_site_dict[key] for key in metro_cargo_site_keys])
        metro_distance_matrix = squareform(pdist(metro_cargo_site_array))

        # 将地铁站点距离矩阵转换为字典 metro_metro_dis，key为（地铁站，地铁站），值为两个地铁站之间的距离
        num_metro_sites = metro_distance_matrix.shape[0]
        for i in range(num_metro_sites):
            for j in range(num_metro_sites):
                if i != j:
                    self.metro_metro_dis[(metro_cargo_site_keys[i], metro_cargo_site_keys[j])] = \
                        metro_distance_matrix[i, j] / metrospeed_ration


    def calculate_travel_times(self):
        # 计算卡车旅行时间
        for (site_a, site_b), distance in self.cargo_site_dis.items():
            self.truck_travel_time[(site_a, site_b)] = distance / self.average_speed

        # 计算地铁旅行时间
        for (metro_a, metro_b), distance in self.metro_metro_dis.items():
            self.metro_travel_time[(metro_a, metro_b)] = distance / self.metro_speed

    def sort_distances(self):
        """
        对每个站点到其他站点的距离进行排序，并存储在 self.sorted_distances 中。
        """
        all_sites = list(self.cargo_site_dict.keys())

        for site in all_sites:
            distances = []
            for other_site in all_sites:
                if site != other_site:
                    distance = self.cargo_site_dis.get((site, other_site), float('inf'))
                    distances.append((other_site, distance))
            # 按照距离从小到大排序
            distances.sort(key=lambda x: x[1])
            self.sorted_distances[site] = distances

    def cal_metro_farthest_station(self):
        """
        计算并生成一个字典，字典的键为地铁站点，值为与该地铁站点最远距离的站点及其距离。
        """
        for metro_station in self.metro_cargo_site_dict.keys():
            farthest_station = None
            max_distance = -1
            for other_station, distance in self.metro_metro_dis.items():
                if metro_station in other_station:
                    if distance > max_distance:
                        max_distance = distance
                        farthest_station = other_station[1] if other_station[0] == metro_station else other_station[0]
            self.metro_farthest_station_dict[metro_station] = (farthest_station, max_distance)


def greedy_get_a_possible_solution(vrp_data):
    turck_route = []
    metro_routes = {}  # 使用新的格式初始化地铁线路
    cargo_inventory = {site: vrp_data.cargo_site_dict[site].initial_inventory for site in
                       vrp_data.cargo_site_dict}  # 初始化每个站点的库存

    # car_dis_list   列表里有 该货物站点的基本信息、该货物站点到仓库的距离、该货物站点的编号
    car_dis_list = [(vrp_data.cargo_site_dict[cargo_ix],
                     vrp_data.cargo_site_dep_dis[cargo_ix], cargo_ix)
                    for cargo_ix in vrp_data.all_sites]
    # 排序先考虑距离最近的货物站点，其次是开始时间最早的货物站点，最后是货物重量
    car_dis_list.sort(key=lambda car_dis: (car_dis[1], car_dis[0].start_time, car_dis[0].cargo_weight))

    # 总是假设 车辆可以在最早时间到达第一个货物点
    initial_load_1 = max(site.cargo_weight for site in vrp_data.cargo_site_dict.values() if site.cargo_weight > 0)
    initial_load_2 = min(vrp_data.vehicle_capacity + site.cargo_weight for site in vrp_data.cargo_site_dict.values() if
                         site.cargo_weight < 0)
    initial_load = min(initial_load_1, initial_load_2)
    carload = initial_load
    elapse_time = 0

    path = [0]  # 初始路径从仓库开始
    leave_times = [elapse_time]  # 离开时间列表，从仓库开始
    arrive_times = [elapse_time]  # 到达时间列表，从仓库开始
    workloads = [initial_load]  # 仓库的作业量为初始装载量
    load_history = [carload]  # 记录每个站点离开时的载重量
    visited_sites = set()  # 已访问站点
    current_site = 0  # 当前站点（仓库）

    while len(visited_sites) < len(vrp_data.all_sites) - 1:  # 除去仓库点
        next_site_info = None
        min_distance = float('inf')

        for cargo_ix, cargo_site in vrp_data.cargo_site_dict.items():
            if cargo_ix not in visited_sites:
                # 获取当前站点到目标站点的距离
                distance = vrp_data.cargo_site_dis.get((current_site, cargo_ix), float('inf'))

                # 判断是否符合装卸货条件
                if cargo_site.cargo_weight > 0:  # 卸货站点
                    feasible = carload >= cargo_site.cargo_weight
                else:  # 装货站点
                    feasible = (carload - cargo_site.cargo_weight) <= vrp_data.vehicle_capacity

                if feasible and distance < min_distance:
                    # 计算到达时间
                    travel_time = distance / vrp_data.average_speed
                    arrival_time = elapse_time + travel_time
                    # 确保到达时间在时间窗内
                    if arrival_time <= cargo_site.end_time:
                        next_site_info = (cargo_ix, cargo_site, distance, arrival_time)
                        min_distance = distance

        if next_site_info:
            cargo_ix, cargo_site, distance, arrival_time = next_site_info
            path.append(cargo_ix)
            visited_sites.add(cargo_ix)

            # 如果到达时间早于时间窗开始时间，则等待至 start_time
            arrival_time = max(arrival_time, cargo_site.start_time)
            arrive_times.append(arrival_time)  # 记录到达时间

            # 计算并记录作业量为货物变化值
            # 需求大于0 --> 卸货 --> carload减小  --> workload 为负值
            # 需求小于0 --> 装货 --> carload增加  --> workload 为正值
            previous_carload = carload  # 记录进入站点前的负载
            carload -= cargo_site.cargo_weight  # 更新负载（卸货减少，装货增加）
            workload = carload - previous_carload  # 作业量为离开站点前后负载变化
            workloads.append(workload)
            load_history.append(carload)

            # 加上装卸货物时间并记录离开时间
            elapse_time = arrival_time + abs(workload) * tc  # 更新为离开时间
            leave_times.append(elapse_time)

            cargo_inventory[cargo_ix] -= cargo_site.cargo_weight
            current_site = cargo_ix  # 更新当前站点

            # 判断是否需要结束路径
            if carload >= vrp_data.vehicle_capacity or cargo_site.end_time <= elapse_time:
                # 将完整路径信息记录到 route_info
                turck_route.append(
                    (path.copy(), arrive_times.copy(), leave_times.copy(), workloads.copy(), load_history.copy()))
                path = [0]  # 新路径从仓库开始
                elapse_time = 0
                arrive_times = [elapse_time]
                leave_times = [elapse_time]
                workloads = [initial_load]
                load_history = [initial_load]
                carload = initial_load
                current_site = 0

        else:
            # 无合适站点，结束当前路径并返回仓库
            turck_route.append(
                (path.copy(), arrive_times.copy(), leave_times.copy(), workloads.copy(), load_history.copy()))
            elapse_time = 0
            path = [0]  # 新路径从仓库开始
            arrive_times = [elapse_time]
            leave_times = [elapse_time]
            workloads = [initial_load]
            load_history = [initial_load]
            carload = initial_load
            current_site = 0

    # 最后将路径信息记录到 route_info
    turck_route.append((path.copy(), arrive_times.copy(), leave_times.copy(), workloads.copy(), load_history.copy()))

    # 添加缺失的卡车路径，只包含仓库点
    while len(turck_route) < num_trucks:
        turck_route.append(([0], [0], [0], [0], [0]))  # 仅包含仓库点的路径

    return turck_route, metro_routes


def cal_add_time(vrp_data, cargo_ix, handle_time, last_cargo_ix, car_type='', car=None):
    # 如果没有上一个货物站点，则仅返回作业时间
    if last_cargo_ix:
        if not car_type:
            if not car:
                raise ValueError("the car_type and car can not be empty simultaneously!")
            car_type = car.type

        drive_time = vrp_data.cargo_site_dis[(last_cargo_ix, cargo_ix)] / vrp_data.average_speed
        return handle_time + drive_time
    return handle_time


def createDict(key):
    # key = [metro_greedy_repair, metro_intermodal_repair, metro_regret_repair, metro_random_repair,
    #        metro_random_destroy,
    #        metro_shaw_destroy, metro_zone_destroy, metro_worst_distance_destroy, truck_intermodal_repair,
    #        truck_random_repair, truck_greedy_repair, truck_regret_repair, truck_random_destroy, truck_shaw_destroy,
    #        truck_zone_destroy, truck_worst_distance_destroy]
    value = np.zeros(len(key), int)
    dic = dict(zip(key, value))
    return dic

def updateDict(dic, destroy, repair, val):
    """
    update dict with value (using times and operator score)
    :param dic: the dict to be updated
    :param destroy: destroy operator
    :param repair: repair operator
    :param val: value
    :return: dict
    """
    dic[destroy] += val
    dic[repair] += val
    return dic




