
class parameter:
    def __init__(self):
        # 算子更新频率 250
        self.fre = 5

        # 卡车算子更新频率
        self.fre_truck = 100
        # 地铁算子更新频率
        self.fre_metro = 200

        # 执行地铁路径操作所需卡车操作次数
        self.N_metro = 50

        # 新解优于最优解时得分
        self.theta1 = 20

        # 新解优于当前解时得分
        self.theta2 = 12

        # 新解不优于当前解但接受
        self.theta3 = 6

        # 新解不优于当前解且没接受
        self.theta4 = 0

        # 冷却系数
        self.c = 0.995

        # 反应系数
        self.r = 0.5

        # 破坏率
        self.drate_low = 0.1
        self.drate_upper = 0.1

        # 初始温度
        self.init_temp = 10000

        # 温度终止系数
        self.t = 0.01

        # 迭代总次数限制
        self.iter_time = 10000

        # 迭代总时间限制
        self.time_limit = 300  # in seconds




