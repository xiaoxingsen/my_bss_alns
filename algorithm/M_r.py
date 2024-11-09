import random
import copy
import math
class metro_no_destroy:
    def repair(self,solution, destroy_rate,vrp_data):
        """
        This function does nothing, because the destruction of the metro routes is not necessary for insertion
        :param solution:
        :param destroy_rate:
        :param vrp_data:
        :return:
        """

        return solution.metro_routes, []

class metro_random_destroy:
    def destroy(self,solution, destroy_rate_low, destroy_rate_upper, vrp_data):
        """
        This function does nothing, because the destruction of the metro routes is not necessary for insertion
        :param solution:
        :param destroy_rate:
        :param vrp_data:
        :return:
        """

        if not solution.metro_routes:
            return solution.metro_routes, []

        destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
        num_routes_to_remove = max(1, math.ceil(len(solution.metro_routes) * destroy_rate))

        # 随机选择要移除的地铁路线
        routes_to_remove = random.sample(list(solution.metro_routes.keys()), num_routes_to_remove)

        tem_metro_routes = copy.deepcopy(solution.metro_routes)
        # 创建新的地铁运输路线字典
        new_metro_routes = {k: v for k, v in tem_metro_routes.items() if k not in routes_to_remove}

        return new_metro_routes, routes_to_remove

class metro_shaw_destroy:
    def destroy(self, solution, destroy_rate_low, destroy_rate_upper, vrp_data):
        """
        This function does nothing, because the destruction of the metro routes is not necessary for insertion
        :param solution:
        :param destroy_rate:
        :param vrp_data:
        :return:
        """

        if not solution.metro_routes:
            return solution.metro_routes, []

        destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
        num_routes_to_remove = max(1, math.ceil(len(solution.metro_routes) * destroy_rate))

        # 随机选择要移除的地铁路线
        routes_to_remove = random.sample(list(solution.metro_routes.keys()), num_routes_to_remove)

        tem_metro_routes = copy.deepcopy(solution.metro_routes)
        # 创建新的地铁运输路线字典
        new_metro_routes = {k: v for k, v in tem_metro_routes.items() if k not in routes_to_remove}

        return new_metro_routes, routes_to_remove

class metro_worst_distance_destroy:
    def destroy(self, solution, destroy_rate_low, destroy_rate_upper, vrp_data):
        """
        使用最远距离破坏算子，移除部分地铁运输路线。

        :param solution: 包含地铁路线的解决方案对象
        :param destroy_rate_low: 破坏比例下界
        :param destroy_rate_upper: 破坏比例上界
        :param vrp_data: 包含地铁站点间距离等信息的数据对象
        :return: 新的地铁运输路线字典和被移除的路径列表
        """

        # 如果没有地铁路径可供破坏，返回原地铁解和空的移除列表
        if not solution.metro_routes:
            return solution.metro_routes, []

        # 计算每条地铁路径的总距离
        distance_cost = {}
        for (from_station, to_station), (schedule, cargo_weight) in solution.metro_routes.items():
            # 直接获取固定距离
            total_distance = vrp_data.metro_metro_dis[from_station, to_station]
            distance_cost[(from_station, to_station)] = total_distance

        # 根据距离降序排序
        sorted_routes = sorted(distance_cost.items(), key=lambda item: item[1], reverse=True)

        # 随机选择要移除的路径数量，范围在 [destroy_rate_low, destroy_rate_upper] 之间
        destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
        num_routes_to_remove = math.ceil(len(sorted_routes) * destroy_rate)

        # 移除距离最大的路径
        routes_to_remove = [route[0] for route in sorted_routes[:num_routes_to_remove]]

        # 生成新的地铁运输路线字典
        new_metro_routes = {k: v for k, v in solution.metro_routes.items() if k not in routes_to_remove}

        return new_metro_routes, routes_to_remove

class metro_zone_destroy:
    def destroy(self, solution, destroy_rate_low, destroy_rate_upper, vrp_data):
        """
        This function does nothing, because the destruction of the metro routes is not necessary for insertion
        :param solution:
        :param destroy_rate:
        :param vrp_data:
        :return:
        """

        if not solution.metro_routes:
            return solution.metro_routes, []

        destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
        num_routes_to_remove = max(1, math.ceil(len(solution.metro_routes) * destroy_rate))

        # 随机选择要移除的地铁路线
        routes_to_remove = random.sample(list(solution.metro_routes.keys()), num_routes_to_remove)

        tem_metro_routes = copy.deepcopy(solution.metro_routes)
        # 创建新的地铁运输路线字典
        new_metro_routes = {k: v for k, v in tem_metro_routes.items() if k not in routes_to_remove}

        return new_metro_routes, routes_to_remove

