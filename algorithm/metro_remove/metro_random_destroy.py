import random
import copy
import math
def destroy(solution, destroy_rate_low, destroy_rate_upper, vrp_data):

    if not solution.metro_routes:
        return solution.metro_routes,[]

    destroy_rate = random.uniform(destroy_rate_low, destroy_rate_upper)
    num_routes_to_remove = max(1, math.ceil(len(solution.metro_routes) * destroy_rate))

    # 随机选择要移除的地铁路线
    routes_to_remove = random.sample(list(solution.metro_routes.keys()), num_routes_to_remove)

    tem_metro_routes = copy.deepcopy(solution.metro_routes)
    # 创建新的地铁运输路线字典
    new_metro_routes = {k: v for k, v in tem_metro_routes.items() if k not in routes_to_remove}

    return new_metro_routes, routes_to_remove