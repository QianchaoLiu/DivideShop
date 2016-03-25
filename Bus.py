# encoding=utf-8
__author__ = 'liuqianchao'


class Bus:
    busID=0#公交车车号
    active=False

    busLineID=0#目前所属交通线路

    wait_state=False
    arrive_time=0
    start_s_time=0
    end_s_time=0
    ready_to_leave=-1
    leave_time=0
    service=True

    def __init__(self,id,buslineid):
        self.busID=id
        self.busLineID=buslineid

        self.wait_state = True
        self.wait_to_leave = False
        self.service = False
        self.ready_to_leave = -1
