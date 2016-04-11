# encoding=utf-8
author = 'liuqianchao'
import numpy as np
import numpy_init
import random
class geneticalgo(object):
    """
    Class for genetic algorithm
    """
    def __init__(self, gene_len=20, population_size=50, cross_rate=0.5, mutation_rate=0.015, elitism_rate=0.1, iter_num=50):
        # 接收系统参数,self.__dict__.update({k:v for k,v in locals().items() if k!='self'})
        self.gene_len = gene_len
        self.population_size = population_size
        self.cross_rate = cross_rate
        self.mutation_rate = mutation_rate
        self.elitism_rate = elitism_rate
        self.iter_num = iter_num

        # 定义poplist来存储集合种群
        self.poplist = []
        # pop_score_list来存储种群及其适应度
        self.pop_score_list = []
        # already_evaluate 存储已经计算计算过的基因以及其适应度
        self.already_evaluate = []
        # new_pop

    def initialize(self):
        # 初始化一个种群,该种群随机生成,种群的大小设定为popluation_size, 每个个体的基因长度为gene_len
        self.poplist = np.random.randint(0, 2, size=(self.population_size, self.gene_len)).tolist()

    def evaluate(self, evaluate_func):
        # 评价,计算每一个个体的得分(适应度),这里采用delay time的倒数, 评价后按照分数维从高到低排序
        self.pop_score_list = []

        for item in self.poplist:
            for ard_item in self.already_evaluate:
                if item == ard_item[0]:

                    eva = ard_item
                    self.pop_score_list.append(eva)
                    print eva
                    break
                    # 一旦break就不会执行else
            else:
                eva = [item, 1.0/evaluate_func(item)]
                self.pop_score_list.append(eva)
                self.already_evaluate.append(eva)
                print eva

        self.pop_score_list.sort(key=lambda x: x[1], reverse=True)  # 从大到小
        return self.pop_score_list[0][0], self.pop_score_list[0][1]

    def select(self):
        # 从群体中选择优胜个体,淘汰劣质个体
        # 轮盘赌选法,适应度越高选择概率越大(比如a,b,c适应度分为a,b,c,则a被选的概率为a/(a+b+c))
        # elitism rate为0.1,最优的个体被保留到下一代,被选的所有个体随机组成交配对,进行交叉操作
        # 选取后进行染色体交换后
        np_pop_score_list = np.array(self.pop_score_list)
        sum_pro= np_pop_score_list[:, 1].sum()
        np_pop_score_list[:, 1] /= sum_pro

        for index, value in enumerate(np_pop_score_list):
            if index != 0:
                np_pop_score_list[index][1] = np_pop_score_list[index-1][1] + np_pop_score_list[index][1]


        # 定义选出来交叉的父个体以及结果
        to_cross = []
        temp_off_elitism = []
        elitism = np_pop_score_list[:, 0][0:round(self.elitism_rate*self.population_size)].tolist()
        elitism_num = len(elitism)

        # 50个个体中0.1%的即前五的保留,然后从全集里提取45*2个组成45对进行交叉,(前五+交叉后的45个)*变异概率=新种群
        for item in range((self.population_size - elitism_num) * 2):
            rand = random.random()
            for index, value in enumerate(np_pop_score_list):
                if index == 0:
                    if 0 <= rand <= value[1]:
                        to_cross.append(value[0])
                        break
                else:
                    if np_pop_score_list[index-1][1] <= rand <= np_pop_score_list[index][1]:
                        to_cross.append(value[0])
                        break


        for index,value in enumerate(to_cross):
            if index % 2 == 1:
                temp_off_elitism.append(self.crossover(to_cross[index-1], to_cross[index], self.cross_rate))

        self.poplist = temp_off_elitism + elitism

        assert len(self.poplist) == self.population_size

    @staticmethod
    def crossover(gene1, gene2, cross_rate):
        # 对种群中的elitism 和 经过轮盘赌选法选出的个体进行交叉
        # 采用单点交叉(one-point crossover),在个体串中设定一个交叉点,实行交叉时,该点前后的两个个体的部分结构进行交换
        # 如果变异,返回某一子基因,不变异,随机返回某父基因
        rand = random.random()
        if rand < cross_rate:
            randint = random.randint(0, len(gene1))
            new_gene1 = gene1[0:randint+1] + gene2[randint:-1]
            new_gene2 = gene2[0:randint+1] + gene1[randint:-1]
            return random.choice([new_gene1, new_gene2])
        else:
            return random.choice([gene1, gene2])

    def mutation(self):
        # 变异率一般为0.001到0.1

        for index, item in enumerate(self.poplist):
            rand = random.random()
            if rand < self.mutation_rate:
                randint = random.randint(0, self.gene_len-1)  # para1 <= randit <= para2
                self.poplist[index][randint] = random.choice([0, 1])

    def iter(self,func):
        # 迭代,迭代的代数一般为100-500代
        for i in range(self.iter_num):
            gene, score = self.evaluate(evaluate_func=func)
            print '第{}代,该代的最优得分为:{},最优基因为{}'.format(i+1, score, gene)
            self.select()
            self.mutation()



if __name__ == "__main__":

    #ob = geneticalgo(gene_len=20, population_size=50, cross_rate=0.5, mutation_rate=0.015, elitism_rate=0.1, iter_num=50)
    #ob.initialize()
    #ob.iter(numpy_init.init)
    #print 1.0/numpy_init.init([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    #print 1.0/numpy_init.init([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    print 724.827,887.735439996,739.45846
    print numpy_init.init([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0])