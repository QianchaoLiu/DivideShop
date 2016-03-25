# encoding=utf-8
#__init__.py在最严格离站策略下两个公交站点,在不同的分站策略下,汽车到达率对汽车等待时间的影响:

#本版本重构__init__.py采用数值计算的方法计算平均等待时间

__author__ = 'liuqianchao'
import os
import random
import numpy as np
import time
def service_time(bus_num=50000, lambda_distribution={}):
    # 一组仿真下的servicetime,
    Si = np.zeros(bus_num)  # Si存储Service time of bus i,服务时间满足均值为30s的负指数分布
    # round(random.expovariate(1/30.0),0)
    Wi = np.zeros(bus_num)  # Delay of the ith bus
    Hi = np.zeros(bus_num)  # Headway between the arrivals of the (i-1)th bus and the ith bus
    # round(random.expovariate(lambda_1/3600.0),0)
    AVLj = np.zeros(2)  # Time when the jth berth(j=1,2) become available
    ARRi = np.zeros(bus_num)  # Arrival time at the stop of the ith bus
    Pi = np.zeros(bus_num)  # Position of the berth where the ith bus to use


    valuelist = [[] for i in range(len(lambda_distribution))]

    for index,value in lambda_distribution.items():
        for i in range(10000):
            if i ==0:
                valuelist[index].append(0 + round(random.expovariate(value/3600.0),0))
            else:
                valuelist[index].append(valuelist[index][i-1]+round(random.expovariate(value/3600.0),0))

    headwaylist = np.ravel(valuelist)
    headwaylist.sort()

    for i in range(bus_num):
        if i == 0:

            Hi[i] = round(0)
            ARRi[i] = Hi[i]  # 到达时间由lambda决定
            Pi[i] = 0  # 使用第一个泊位
            Wi[i] = 0  # 等待时间为0
            Si[i] = round(random.expovariate(1/30.0),0)  # 服务时间
            AVLj[0] = Hi[i] + Si[i]  # 第一个泊位的可用时间
            AVLj[1] = 0  # 第二个泊位的可用时间
        else:
            Hi[i] = headwaylist[i] - headwaylist[i-1]
            # 经过Hi[i]来了下一辆车
            ARRi[i] = Hi[i] + ARRi[i-1]  #到达时间
            Si[i] = round(random.expovariate(1/30.0),0)  # 服务时间
            if AVLj[0] <= ARRi[i] and AVLj[1] <= ARRi[i]:  # 两个泊位都可用,进入第一个泊位
                Wi[i] = 0
                Pi[i] = 0
                AVLj[0] = ARRi[i] + Si[i]
            elif AVLj[0] > ARRi[i] and AVLj[1] <= ARRi[i]:  # 仅第二个泊位可用

                Pi[i] = 1


                Wi[i] = max(0, AVLj[0]-(ARRi[i]+Si[i]))  # 可能产生等待

                AVLj[1] = ARRi[i] + Si[i] + Wi[i]
                AVLj[0] = max(AVLj[0], AVLj[1])

            elif AVLj[1] > ARRi[i]:  # 第二个泊位不可用  AVLj[1] > ARRi[i]
                if AVLj[0] <= AVLj[1] and Pi[i-1] == 1:  # 第一个泊位先空出来,一旦第二个泊位空出来,bus进入第一个泊位,
                    Wi[i] = AVLj[1] - ARRi[i]
                    Pi[i] = 0
                    AVLj[0] = ARRi[i] + Wi[i] + Si[i]
                    AVLj[1] = ARRi[i] + Wi[i]
                elif AVLj[0] > AVLj[1] and Pi[i-1] == 1:  # 等第一个泊位的车结束服务,第一泊位的车和第二泊位的车同时驶出,bus进入第一个泊位.
                    Wi[i] = AVLj[0]-ARRi[i]
                    Pi[i] = 0
                    AVLj[0] = ARRi[i] + Wi[i] + Si[i]
                    AVLj[1] = ARRi[i] + Wi[i]
                elif AVLj[0] <= AVLj[1] and Pi[i-1] == 0:
                    None

                elif AVLj[0] > AVLj[1] and Pi[i-1] == 0:  #大 小
                    Wi[i] = max(0, AVLj[0]-ARRi[i], AVLj[0]-ARRi[i] + AVLj[0]-(ARRi[i]+AVLj[0]-ARRi[i] +Si[i]))
                    Pi[i] = 1
                    AVLj[1] = ARRi[i] + Wi[i] + Si[i]
                    AVLj[0] = max(AVLj[0], AVLj[1])


    return np.average(Wi)


if __name__ == "__main__":

    print "Simulation has begun:"
    NUMBER_ROUTELINE = 20
    STOP_NUM = 2

    lambda_distribution= {}
    for item in range(NUMBER_ROUTELINE):
        lambda_distribution[item] = 12

    # 前一半条线路分配给第一个站点
    distribution = [0 if i < NUMBER_ROUTELINE/STOP_NUM else 1 for i in range(0, NUMBER_ROUTELINE)]

    stop_1_lambda_list ={}
    stop_2_lambda_list ={}

    for index,value in enumerate(distribution):
        if value == 0:
            stop_1_lambda_list[len(stop_1_lambda_list)] = lambda_distribution[index]
        else:
            stop_2_lambda_list[len(stop_2_lambda_list)] = lambda_distribution[index]


    start_time = time.time()
    simulation_count = 10
    result_data = np.zeros(STOP_NUM)
    for simulation_count in range(simulation_count):
        time_s = time.time()
        data_1 = service_time(50000, stop_1_lambda_list)
        data_2 = service_time(50000, stop_2_lambda_list)
        result_data += np.array([data_1,data_2])
        print time.time()-time_s,[data_1,data_2]
    result_data /= simulation_count

    print "After {:.0f} s of simulation, the average waiting time of {} stops are: {}".format(time.time()-start_time, STOP_NUM, result_data)
