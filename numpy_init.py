# encoding=utf-8
# __init__.py在最严格离站策略下两个公交站点,在不同的分站策略下,汽车到达率对汽车等待时间的影响:

# 本版本重构__init__.py采用数值计算的方法计算平均等待时间

# Demand at 2016/3/31: 1, add service time to parameter; 2, granularity of data ranged by route line
# Demand at 2016/4/3: 1, distinguish blocking time from queuing time; 2, output the structural data; 3. percent of usage at each stop
# Demand at 2016/4/7: 1.check gamma distribution; 2.add genetic algorithm
import os
import random
import numpy as np
import time
import sys
__author__ = 'liuqianchao'

# 到达率
LAMBDA_DISTRIBUTION = {
    0: 30.0,
    1: 12.0,
    2: 12.0,
    3: 12.0,
    4: 12.0,
    5: 12.0,
    6: 12.0,
    7: 12.0,
    8: 12.0,
    9: 12.0,
    10: 12.0,
    11: 12.0,
    12: 12.0,
    13: 12.0,
    14: 12.0,
    15: 12.0,
    16: 12.0,
    17: 12.0,
    18: 12.0,
    19: 12.0,
}

#4,5,6
# 服务时间
SERVICE_TIME_DISTRIBUTION = {
    0: 30.0,
    1: 30.0,
    2: 30.0,
    3: 30.0,
    4: 30.0,
    5: 30.0,
    6: 30.0,
    7: 30.0,
    8: 30.0,
    9: 30.0,
    10: 30.0,
    11: 30.0,
    12: 30.0,
    13: 30.0,
    14: 30.0,
    15: 30.0,
    16: 30.0,
    17: 30.0,
    18: 30.0,
    19: 30.0,
}


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
    Wdelayi = np.zeros(bus_num)  # 进站入泊位前的等待
    Wblocki = np.zeros(bus_num)  # 离开泊位时的等待
    Hi = np.zeros(bus_num)  # Headway between the arrivals of the (i-1)th bus and the ith bus
    # round(random.expovariate(lambda_1/3600.0),0)
    AVLj = np.zeros(2)  # Time when the jth berth(j=1,2) become available
    ARRi = np.zeros(bus_num)  # Arrival time at the stop of the ith bus
    Pi = np.zeros(bus_num)  # Position of the berth where the ith bus to use
    Ti = np.zeros(bus_num)  # A tap to record the bus belongs to which route line

    # Time
    Berth1_Use = []  # looks like [[1,3],[7,9],[19,52]
    Berth2_Use = []  # looks like [[2,4],[11,39]]
    System_time = 0.0

    # 归并途径该站的所有线路的到达车辆
    car_per_route = int(2.5 * float(bus_num) / len(lambda_distribution))
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

    # 迭代
    for i in range(bus_num):
        if i == 0:
            Ti[i] = -1  # 该辆车随便分配一个不存在的线路 暂定-1
            Hi[i] = round(0)
            ARRi[i] = Hi[i]  # 到达时间由lambda决定
            Pi[i] = 0  # 使用第一个泊位
            Wi[i] = 0  # 等待时间为0
            Si[i] = round(random.expovariate(1/30.0), 0)  # 服务时间 暂定 30
            AVLj[0] = Hi[i] + Si[i]  # 第一个泊位的可用时间
            AVLj[1] = 0  # 第二个泊位的可用时间

            Berth1_Use.append([0, AVLj[0]])
        else:
            Hi[i] = headwaylist[i][1] - headwaylist[i-1][1]
            Ti[i] = headwaylist[i][0]
            # 经过Hi[i]来了下一辆车
            ARRi[i] = Hi[i] + ARRi[i-1]  # 到达时间
            Si[i] = round(random.expovariate(1/service_time_distribution[Ti[i]]), 0)  # 服务时间
            if AVLj[0] <= ARRi[i] and AVLj[1] <= ARRi[i]:  # 两个泊位都可用,进入第一个泊位
                Wi[i] = 0
                Pi[i] = 0
                AVLj[0] = ARRi[i] + Si[i]
                Berth1_Use.append([ARRi[i], AVLj[0]])
            elif AVLj[0] > ARRi[i] and AVLj[1] <= ARRi[i]:  # 仅第二个泊位可用

                Pi[i] = 1
                Wi[i] = max(0, AVLj[0]-(ARRi[i]+Si[i]))  # 可能产生等待,仅可能产生block
                Wblocki[i] = Wi[i]

                AVLj[1] = ARRi[i] + Si[i] + Wi[i]
                AVLj[0] = max(AVLj[0], AVLj[1])
                Berth2_Use.append([ARRi[i], AVLj[1]])
            elif AVLj[1] > ARRi[i]:  # 第二个泊位不可用  AVLj[1] > ARRi[i] 现产生
                if AVLj[0] <= AVLj[1] and Pi[i-1] == 1:  # 第一个泊位先空出来,一旦第二个泊位空出来,bus进入第一个泊位,
                    Wi[i] = AVLj[1] - ARRi[i]
                    Wdelayi[i] = Wi[i]
                    Pi[i] = 0
                    AVLj[0] = ARRi[i] + Wi[i] + Si[i]
                    AVLj[1] = ARRi[i] + Wi[i]
                    Berth1_Use.append([ARRi[i]+Wdelayi[i], AVLj[0]])
                elif AVLj[0] > AVLj[1] and Pi[i-1] == 1:  # 第二个泊位的车先结束服务,等第一个泊位的车结束服务,第一泊位的车和第二泊位的车同时驶出,bus进入第一个泊位.
                    Wi[i] = AVLj[0]-ARRi[i]
                    Wdelayi[i] = Wi[i]
                    Pi[i] = 0
                    AVLj[0] = ARRi[i] + Wi[i] + Si[i]
                    AVLj[1] = ARRi[i] + Wi[i]
                    Berth1_Use.append([ARRi[i]+Wdelayi[i], AVLj[0]])
                elif AVLj[0] <= AVLj[1] and Pi[i-1] == 0:
                    None

                elif AVLj[0] > AVLj[1] and Pi[i-1] == 0:  #大 小
                    Wi[i] = max(0, AVLj[0]-ARRi[i], AVLj[0]-ARRi[i] + AVLj[0]-(ARRi[i]+AVLj[0]-ARRi[i] + Si[i]))
                    Wdelayi[i] = max(0, AVLj[0] - ARRi[i])
                    Wblocki[i] = max(0, AVLj[0] - (ARRi[i] + AVLj[0] - ARRi[i] + Si[i]))
                    Pi[i] = 1
                    AVLj[1] = ARRi[i] + Wi[i] + Si[i]
                    AVLj[0] = max(AVLj[0], AVLj[1])
                    Berth2_Use.append([ARRi[i]+Wdelayi[i], AVLj[1]])
        if i == bus_num-1:
            System_time = AVLj[Pi[i]]
    # Time
    total_time_1 = np.zeros(System_time)
    total_time_2 = np.zeros(System_time)
    for item in Berth1_Use:
        total_time_1[slice(item[0], item[1]+1)] = 1
    for item in Berth2_Use:
        total_time_2[slice(item[0], item[1]+1)] = 1
    berth1_bus = np.count_nonzero(total_time_1)
    berth2_bus = np.count_nonzero(total_time_2)

    and_operation = np.logical_and(total_time_1,total_time_2)
    both_use_time = np.count_nonzero(and_operation)
    use_percent = [berth1_bus/System_time, berth2_bus/System_time, both_use_time/System_time]

    # waiting 分流成各个线路
    result_list_total = [[] for item in range(len(lambda_distribution))]
    result_list_delay = [[] for item in range(len(lambda_distribution))]
    result_list_block = [[] for item in range(len(lambda_distribution))]

    for index,value in enumerate(Wi):
        if Ti[index] != -1:
            result_list_total[int(Ti[index])].append(value)
            result_list_delay[int(Ti[index])].append(Wdelayi[index])
            result_list_block[int(Ti[index])].append(Wblocki[index])

    result_list_total_average, result_list_total_std= [np.average(item) for item in result_list_total], [np.std(item) for item in result_list_total]
    result_list_delay_average, result_list_delay_std = [np.average(item) for item in result_list_delay], [np.std(item) for item in result_list_delay]
    result_list_block_average, result_list_block_std = [np.average(item) for item in result_list_block], [np.std(item) for item in result_list_block]

    # 以站为单位,以线路为单位,站的使用率
    return np.average(Wi), [[result_list_total_average, result_list_total_std], [result_list_delay_average, result_list_delay_std],[result_list_block_average, result_list_block_std]], use_percent

def init(gene):
    if os.path.exists('result.txt'):
        os.remove('result.txt')
    if '--help' in sys.argv or '--h' in sys.argv:
        print("Build a simulation to evaluate ")

    #print "Simulation has begun:"
    NUMBER_ROUTELINE = 20
    STOP_NUM = 2


    # 线路分配
    distribution = gene

    # 提取到达率,服务时间
    stop_1_lambda_dict_from_0 = {}
    stop_2_lambda_dict_from_0 = {}
    stop_1_lambda_dict_by_id = {}
    stop_2_lambda_dict_by_id = {}

    stop_1_service_time_dict_from_0 = {}
    stop_2_service_time_dict_from_0 = {}
    for index,value in enumerate(distribution):
        if value == 0:
            stop_1_lambda_dict_from_0[len(stop_1_lambda_dict_from_0)] = LAMBDA_DISTRIBUTION[index]
            stop_1_lambda_dict_by_id[index] = LAMBDA_DISTRIBUTION[index]
            stop_1_service_time_dict_from_0[len(stop_1_service_time_dict_from_0)] = SERVICE_TIME_DISTRIBUTION[index]
        else:
            stop_2_lambda_dict_from_0[len(stop_2_lambda_dict_from_0)] = LAMBDA_DISTRIBUTION[index]
            stop_2_lambda_dict_by_id[index] = LAMBDA_DISTRIBUTION[index]
            stop_2_service_time_dict_from_0[len(stop_2_service_time_dict_from_0)] = SERVICE_TIME_DISTRIBUTION[index]
    start_time = time.time()
    simulation_count = 10

    total = np.zeros(2)
    routedata1 = np.zeros((3, 2, len(stop_1_lambda_dict_from_0)))
    routedata2 = np.zeros((3, 2, len(stop_2_lambda_dict_from_0)))
    time_percent = np.zeros((2, 3))
    for simulation_count in range(simulation_count):
        time_s = time.time()
        data_1, route_data_1, stop1_use_percent = service_time(50000, stop_1_lambda_dict_from_0, stop_1_service_time_dict_from_0)
        data_2, route_data_2, stop2_use_percent = service_time(50000, stop_2_lambda_dict_from_0, stop_2_service_time_dict_from_0)

        total += np.array([data_1, data_2])
        routedata1 += np.array(route_data_1)
        routedata2 += np.array(route_data_2)
        time_percent += np.array([stop1_use_percent, stop2_use_percent])

    total /= simulation_count
    routedata1 /= simulation_count
    routedata2 /= simulation_count

    time_percent /= simulation_count
    with open('result.txt', 'a') as f:
        f.write(str(routedata1))
        f.write('\n\n')
        f.write(str(routedata2))
        f.write('\n\n')
        f.write(str(time_percent))
    return data_1 + data_2

    #print "After {:.0f} s of simulation, the average waiting time of {} stops are: {}".format(time.time()-start_time, STOP_NUM, total)
    #print "   --usage percent at stop1: berth1: {}%, berth2: {}%, both berth: {}%".format(time_percent[0][0], time_percent[0][1], time_percent[0][2])
    #print "   --usage percent at stop2: berth1: {}%, berth2: {}%, both berth: {}%".format(time_percent[1][0], time_percent[1][1], time_percent[1][2])

#if __name__ == "__main__":
#    pass