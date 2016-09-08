#!/usr/bin/python
# coding=utf-8

import os
import adbhelper
import sys


class Phoneinfo(Object):
    def __init__(self, sn, version):
        self.sn = sn
        self.version = version

    # def Meminfo(self):



    def getsysapk(self):
        sysapklist = []
        if os._exists(os.getcwd() + '\\Appinfo'):
            with open(os.getcwd() + '\\Appinfo', 'r') as infile:
                for n in infile.readlines():
                    name = n.strip().split('/')[0]
                    sysapklist.append(name)
        return sysapklist

    def get3rdapk(self):
        device = adbhelper.ADB(self.sn)
        templist = device.adbshell("pm package list").split('\n')

        otherlist = ['meizu', 'sumsung']  # 系统包名

        trdlist = filter(lambda x: (x not in otherlist), templist)

        return trdlist
