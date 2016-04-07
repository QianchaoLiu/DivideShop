# encoding=utf-8
author = 'liuqianchao'
import numpy as np

class geneticalgo(object):
    """
    Class for genetic algorithm
    """
    def __init__(self, gene_len=20, population_size=50, cross_rate=0.5, mutation_rate=0.015, elitism_rate=0.1, iter_num=50):
        # 接收系统参数,self.__dict__.update({k:v for k,v in locals().items() if k!='self'})
        self.gen_len = gene_len
        self.population_size = population_size
        self.cross_rate = cross_rate
        self.mutation_rate = mutation_rate
        self.elitism_rate = elitism_rate
        self.iter_num = iter_num
        # 定义list来存储集合种群
        self.poplist = []

    def initialize(self):
        # 初始化一个种群,该种群随机生成,种群的大小设定为popluation_size, 每个个体的基因长度为gene_len
        self.poplist = np.random.randint(0, 2, size=(self.population_size, self.gen_len)).tolist()

    def evaluate(self, evaluate_func):
        # 评价,计算每一个个体的得分(适应度),这里采用delay time的倒数, 评价后按照分数维从高到低排序
        pop_score_list = []
        for item in self.poplist:
            pop_score_list.append([item, 1.0/evaluate_func(item)])
        pass

    def select(self):
        # 从群体中选择优胜个体,淘汰劣质个体
        # 轮盘赌选法,适应度越高选择概率越大(比如a,b,c适应度分为a,b,c,则a被选的概率为a/(a+b+c))
        # elitism rate为0.1,最优的个体被保留到下一代,被选的所有个体随机组成交配对,进行交叉操作
        pass

    def crossover(self):
        # 采用单点交叉(one-point crossover),在个体串中设定一个交叉点,实行交叉时,该点前后的两个个体的部分结构进行交换
        pass

    def mutation(self):
        # 变异率一般为0.001到0.1
        pass

    def iter(self):
        # 迭代,迭代的代数一般为100-500代
        pass

    @classmethod  # 只操作类,而不操作instance
    def output(cls):
        print cls.input
        '''
        :return:
        '''
        pass

    @staticmethod  # 与类有关的函数,但不操作实例或类
    def stic():
        pass

if __name__ == "__main__":
    ob = geneticalgo()
    ob.initialize()
