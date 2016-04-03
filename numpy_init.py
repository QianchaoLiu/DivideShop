# encoding=utf-8
# __init__.py在最严格离站策略下两个公交站点,在不同的分站策略下,汽车到达率对汽车等待时间的影响:

# 本版本重构__init__.py采用数值计算的方法计算平均等待时间

# Demand at 2016/3/31: 1, add service time to parameter; 2, granularity of data ranged by route line
__author__ = 'liuqianchao'
import os
import random
import numpy as np
import time
import sys
def service_time(bus_num=50000, lambda_distribution={}, service_time_distribution={}):
    '''
    :param bus_num: All number of bus to simulate in this stop
    :param lambda_distribution: lambda of different route lines
    :param service_time_distribution: service time of different route lines
    :return: average delay time of this stop
    '''
    # 一组仿真下的servicetime,
    Si = np.zeros(bus_num)  # Si存储Service time of bus i,服务时间满足均值为30s的负指数分布
    # round(random.expovariate(1/30.0),0)
    Wi = np.zeros(bus_num)  # Delay of the ith bus
    Hi = np.zeros(bus_num)  # Headway between the arrivals of the (i-1)th bus and the ith bus
    # round(random.expovariate(lambda_1/3600.0),0)
    AVLj = np.zeros(2)  # Time when the jth berth(j=1,2) become available
    ARRi = np.zeros(bus_num)  # Arrival time at the stop of the ith bus
    Pi = np.zeros(bus_num)  # Position of the berth where the ith bus to use
    Ti = np.zeros(bus_num)  # A tap to record the bus belongs to which route line
    # 归并途径该站的所有线路的到达车辆

    car_per_route = 10000
    valuelist = [[] for i in range(len(lambda_distribution))]
    for key,value in lambda_distribution.items():
        for i in range(car_per_route):
            if i==0:
                valuelist[key].append([key, 0 + round(random.expovariate(value/3600.0),0)] )
            else:
                valuelist[key].append([key, valuelist[key][i-1][1] + round(random.expovariate(value/3600.0),0)])
    valuelist = np.array(valuelist)
    headwaylist = list(valuelist.reshape((car_per_route*len(lambda_distribution),2)))
    headwaylist.sort(key=lambda x: x[1])

    for i in range(bus_num):
        if i == 0:
            Ti[i] = -1  # 该辆车随便分配一个不存在的线路 暂定-1
            Hi[i] = round(0)
            ARRi[i] = Hi[i]  # 到达时间由lambda决定
            Pi[i] = 0  # 使用第一个泊位
            Wi[i] = 0  # 等待时间为0
            Si[i] = round(random.expovariate(1/30.0),0)  # 服务时间 暂定 30
            AVLj[0] = Hi[i] + Si[i]  # 第一个泊位的可用时间
            AVLj[1] = 0  # 第二个泊位的可用时间
        else:
            Hi[i] = headwaylist[i][1] - headwaylist[i-1][1]
            Ti[i] = headwaylist[i][0]
            # 经过Hi[i]来了下一辆车
            ARRi[i] = Hi[i] + ARRi[i-1]  #到达时间
            Si[i] = round(random.expovariate(1/service_time_distribution[Ti[i]]),0)  # 服务时间
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
    result_dict={}
    for key,value in lambda_distribution.items():
        result_dict[key] = 0
    for index,value in enumerate(Ti):
        if value!=-1:
            result_dict[value] += Wi[index]
    for key,value in result_dict.items():
        result_dict[key] /= list(Ti).count(key)
    return np.average(Wi),result_dict

if __name__ == "__main__":
    #kwargs = {}
    #if len(sys.argv) > 1:
    #    kwargs[1] = sys.argv[1]
    if '--help' in sys.argv or '--h' in sys.argv:
        print("Build a simulation to evaluate ")

    print "Simulation has begun:"
    NUMBER_ROUTELINE = 20
    STOP_NUM = 2

    # 到达率
    lambda_distribution = {}
    for item in range(NUMBER_ROUTELINE):
        lambda_distribution[item] = 12

    # 服务时间
    service_time_distribution = {}
    for item in range(NUMBER_ROUTELINE):
        service_time_distribution[item] = 30.0

    # 线路分配
    distribution = [0 if i < NUMBER_ROUTELINE/STOP_NUM else 1 for i in range(0, NUMBER_ROUTELINE)]

    # 提取到达率,服务时间
    stop_1_lambda_dict_from_0 = {}
    stop_2_lambda_dict_from_0 = {}
    stop_1_lambda_dict_by_id = {}
    stop_2_lambda_dict_by_id = {}

    stop_1_service_time_dict_from_0 = {}
    stop_2_service_time_dict_from_0 = {}
    for index,value in enumerate(distribution):
        if value == 0:
            stop_1_lambda_dict_from_0[len(stop_1_lambda_dict_from_0)] = lambda_distribution[index]
            stop_1_lambda_dict_by_id[index] = lambda_distribution[index]
            stop_1_service_time_dict_from_0[len(stop_1_service_time_dict_from_0)] = service_time_distribution[index]
        else:
            stop_2_lambda_dict_from_0[len(stop_2_lambda_dict_from_0)] = lambda_distribution[index]
            stop_2_lambda_dict_by_id[index] = lambda_distribution[index]
            stop_2_service_time_dict_from_0[len(stop_2_service_time_dict_from_0)] = service_time_distribution[index]

    start_time = time.time()
    simulation_count = 10

    total = np.zeros(STOP_NUM)
    first_route = np.zeros(len(stop_1_lambda_dict_by_id))
    second_route = np.zeros(len(stop_2_lambda_dict_by_id))

    for simulation_count in range(simulation_count):
        time_s = time.time()
        data_1, data_1_detail = service_time(50000, stop_1_lambda_dict_from_0, stop_1_service_time_dict_from_0)
        data_2, data_2_detail = service_time(50000, stop_2_lambda_dict_from_0, stop_2_service_time_dict_from_0)
        data_1_detail, data_2_detail = data_1_detail.values(), data_2_detail.values()

        total += np.array([data_1,data_2])
        first_route += np.array(data_1_detail)
        second_route += np.array(data_2_detail)

        print time.time()-time_s,[data_1,data_2]
    total /= simulation_count
    first_route /= simulation_count
    second_route /= simulation_count
    print "After {:.0f} s of simulation, the average waiting time of {} stops are: {}".format(time.time()-start_time, STOP_NUM, total)
    print "Route lines at stop1:{}, \nroute lines at stop2:{}".format(first_route, second_route)