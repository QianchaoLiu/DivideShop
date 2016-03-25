# encoding=utf-8
import numpy as np
import time
import random
from Station import Staion
from Bus import Bus
__author__ = 'liuqianchao'


def init(stop_num=2, route_distribution=[], simulation_time=36000, lambda_distribution={}):
    result = np.zeros(stop_num)
    for stop_iter in range(stop_num):
        stop = Staion(0,2)
        buslist=[]#embedding object of buses that has been created.

        route_count = 0
        lambda_dict = {}
        for item in route_distribution:
            if item == stop_iter:  # 这个route在该stop停
                lambda_dict[route_count] = lambda_distribution[item]
                route_count += 1
        waiting_to_add_new_bus = [-1] * route_count

        #waiting_to_add_new_bus=-1


        for clock in range(simulation_time):
            None
            #Step 1: bus到站处理
            if clock == 0:
                #初始化第一辆车.
                bus=Bus(len(buslist),0) #new bus was created. And added into buslist.
                bus.arrive_time=clock #created time
                bus.active = True
                bus.wait_state = True
                bus.service = False
                buslist.append(bus)


                # 初始化waiting_to_add_new_bus
                for count, item in enumerate(waiting_to_add_new_bus):
                    waiting_to_add_new_bus[count] = round(random.expovariate(lambda_dict[count]/3600.0), 0)
            for count, item in enumerate(waiting_to_add_new_bus):
                if item == 0:  # 某条线路来车了
                    bus = Bus(len(buslist),0) #new bus was created. And added into buslist.
                    bus.arrive_time = clock #created time
                    bus.active = True
                    bus.wait_state = True
                    bus.service = False
                    buslist.append(bus)
                    # 更新waiting_to_add_new_bus
                    waiting_to_add_new_bus[count] = round(random.expovariate(lambda_dict[count]/3600.0),0)
                else:  # 该条线路没有来车,应该续1s
                    waiting_to_add_new_bus[count] -= 1

            print waiting_to_add_new_bus

            #Step 2: bus进站判断，没有进站继续等待，进入后开始服务

            for car in buslist:
                if car.active == True and car.service == False:
                    if car.wait_state == True: #还没进站，进行进站处理
                        if len(stop.parking) == 0:
                            stop.parking.append(car)
                            car.wait_state = False
                            car.start_s_time = clock
                        elif len(stop.parking) == 1:
                            stop.parking.append(car)
                            car.wait_state = False
                            car.start_s_time = clock
                        #判断泊位状况
                        elif len(stop.parking) == 2:
                            if stop.parking[0]==0 and stop.parking[1]==0:
                                #泊位没有车
                                stop.parking[0] = car
                                car.wait_state = False
                                car.start_s_time = clock
                            elif stop.parking[0]!=0 and stop.parking[1]==0:
                                #第一个泊位有车,第二个泊位没有车
                                stop.parking[1] = car
                                car.wait_state = False
                                car.start_s_time = clock
                            elif stop.parking[0]==0 and stop.parking[1]!=0:
                                #第二个泊位有车,第一个泊位没有车
                                car.wait_state = True
                            elif stop.parking[0]!=0 and stop.parking[1]!=0:
                                #两个泊位都有车
                                car.wait_state = True
                    if car.wait_state == False:  #已经准备开始服务。
                        #开始服务
                        servicetime=round(random.expovariate(1/30.0),0)
                        car.end_s_time = car.start_s_time +servicetime
                        car.ready_to_leave=0 #change ready_to_leave from -1 to 0
                        #car.leave_time = car.end_s_time + leave_stop_time
                        #累计的上车乘客、下车乘客进行清空
                        car.service = True

            #判断到end_s_time时，car是否能离开
            for car in buslist:
                if car.active == True and car.service == True and car.ready_to_leave!=-1:
                    if clock<car.end_s_time:
                    #汽车正在服务
                        None
                    elif clock >= car.end_s_time:
                    #汽车服务结束，判断是否能离开
                        if len(stop.parking)==1:
                            if stop.parking == car:
                                car.active = False

                                car.leave_time=car.end_s_time+car.ready_to_leave
                        if len(stop.parking)==2:
                            if stop.parking[0]==car:
                                #该车在第一个泊位,直接离开
                                car.active = False
                                car.leave_time=car.end_s_time+car.ready_to_leave
                            elif stop.parking[1]==car:
                                #该车在第二个泊位
                                if stop.parking[0]==0:
                                    car.active = False
                                    car.leave_time=car.end_s_time+car.ready_to_leave
                                elif stop.parking[0]!=0:
                                    car.ready_to_leave+=1

            #服务结束离开处理
            for car in buslist:
                if car.active == False:
                    if clock > car.leave_time:
                        if len(stop.parking) == 1:
                            if stop.parking[0] == car:
                                stop.parking[0]=0
                        elif len(stop.parking) == 2:
                            if stop.parking[0] == car:
                                stop.parking[0]=0
                            if stop.parking[1]==car:
                                stop.parking[1]=0

        #统计，并返回所有active=false的bus平均waiting_time
        i=0.0
        wait_time=0
        for car in buslist:
           if car.active==False:
             i+=1
             wait_time+=(car.leave_time-car.end_s_time)+(car.start_s_time-car.arrive_time)
        result[stop_iter] = wait_time/i

    return result

if __name__ == "__main__":
    print "Simulation has begun:"
    NUMBER_ROUTELINE = 20
    STOP_NUM = 2


    lambda_distribution= {}
    for item in range(NUMBER_ROUTELINE):
        lambda_distribution[item] = 12

    # 前一半条线路分配给第一个站点
    distribution = [0 if i < NUMBER_ROUTELINE/STOP_NUM else 1 for i in range(0, NUMBER_ROUTELINE)]
    start_time = time.time()
    simulation_time = 10 * 3600

    simulation_count = 10
    result_data = np.zeros(STOP_NUM)
    for simulation_count in range(simulation_count):
        time_s = time.time()
        data = init(STOP_NUM, distribution, simulation_time, lambda_distribution)
        result_data += data
        print data, time.time()-time_s
    result_data /= simulation_count

    print "After {:.0f} s of simulation, the average waiting time of {} stops are: {}".format(time.time()-start_time, STOP_NUM, result_data)
