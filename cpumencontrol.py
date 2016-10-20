#!/usr/bin/evn python
# -*- coding:utf-8 -*-

# FileName cpumencontrol.py
# Created Time: 2016/9/13
"""
捕获CPU - MEMORY类
"""

# start
import os
import shutil
import threading
from time import sleep
import subprocess
import platform


class CpuMencontrol(object):
    def __init__(self, pkg_name, sn):

        self.pkg_info = {"pkg_name": pkg_name, "pid": None, "sn": sn}
        self.cpu_result = {"cpu_Total": None, "cpu_User": None, "cpu_Sys": None, "cpu_iowait": None, "cpu_app": None}
        self.cpu_temp = {"idle": None, "user": None, "system": None, "iowait": None, "total": None, "cpu_app": None}

    # function start
    # ex_cmd

    def __record(self, filename, result):

        resultdir = os.getcwd() + '\\' + "Cpu&Mem result"
        if not os.path.isdir(resultdir):
            os.mkdir(resultdir)
        file = resultdir + '\\' + filename
        with open(file, 'a+') as resultdoc:
            for key in result.keys():
                resultdoc.write(('\t'*2).join([key, str(result[key])]))
                resultdoc.write('\t')
            resultdoc.write('\n')

    def __ex_cmd(self, cmd):
        res = list()
        try:
            fh = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            fh.wait()
            for line in fh.stdout.readlines():
                line = line.decode().strip()
                if line != '':
                    res.append(line)
            fh.stdout.close()
        except Exception as ex:
            print('run cmd exception: %s' % ex)
            res.append('error')
        return res

    # get package pid ...
    def get_pkg(self):
        pt_name = platform.platform()
        if pt_name.startswith('Windows'):
            GREP = 'findstr'
        else:
            GREP = 'grep'
        pid_file = self.__ex_cmd('adb -s %s shell ps|%s %s' % (self.pkg_info['sn'], GREP, self.pkg_info['pkg_name']))
        if len(pid_file) > 0:
            self.pkg_info['pid'] = pid_file[0].split()[1]
        else:
            self.pkg_info['pid'] = None

    # get proc file
    def Read_Proc(self, file):
        proc_file = self.__ex_cmd('adb -s %s shell cat /proc/%s' % (self.pkg_info['sn'], file))
        return proc_file

    # get memory
    def And_Memory(self):
        mem_result = {"MemTotal": None, "MemUsage": None, "Buffers": None, "Cached": None, "MemUsage_pct": None}
        Proc_MemInfo = self.Read_Proc('meminfo')
        if len(Proc_MemInfo) == 0:
            for x in mem_result:
                mem_result[x] = None
            return None
        Memory = dict()
        for i in Proc_MemInfo:
            Memory[i.split()[0][0:-1]] = int(i.split()[1])
        MemTotal = Memory['MemTotal']
        MemFree = Memory['MemFree']
        Buffers = Memory['Buffers']
        Cached = Memory['Cached']
        # memusage calc
        MemUsage = MemTotal - MemFree - Buffers - Cached
        # result value
        mem_result['MemTotal'] = MemTotal
        mem_result['MemUsage'] = MemUsage
        mem_result['Buffers'] = Buffers
        mem_result['Cached'] = Cached
        mem_result['MemUsage_pct'] = ('%.3f' % (float(MemUsage) * 100 / MemTotal))

        self.__record('Sys_MemResult', mem_result)

    # get app mem
    def And_AppMem(self):
        """

        :rtype: dict
        """
        appmem_result = {"Native_heap": None, "Dalvik_heap": None, "Mem_app": None}

        if self.pkg_info['pid'] is None:
            for x in appmem_result:
                appmem_result[x] = None
        else:
            # mem calc
            ad_mem_info = self.__ex_cmd(
                    'adb -s %s shell dumpsys meminfo %s' % (self.pkg_info['sn'], self.pkg_info['pkg_name']))
            if len(ad_mem_info) > 5:
                for info in ad_mem_info:
                    info = info.split()
                    if info[0] == 'Native':
                        if info[1].isdigit():
                            appmem_result['Native_heap'] = info[1]
                        elif info[1] == 'Heap':
                            appmem_result['Native_heap'] = info[2]
                    elif info[0] == 'Dalvik':
                        if info[1].isdigit():
                            appmem_result['Dalvik_heap'] = info[1]
                        elif info[1] == 'Heap':
                            appmem_result['Dalvik_heap'] = info[2]
                    elif info[0] == 'TOTAL':
                        appmem_result['Mem_app'] = info[1]
                        break
                # return appmem_result
                self.__record(' '.join(['[' + self.pkg_info['pkg_name'] + ']', 'MemResult']), appmem_result)

    # get CPU
    def And_Cpu(self):
        """

        :rtype: dict
        """

        Cpu_data = self.Read_Proc('stat')
        if len(Cpu_data) == 0:
            for x in self.cpu_temp:
                self.cpu_temp[x] = None
            for x in self.cpu_result:
                self.cpu_result[x] = None
            return None
        Cpu_data = Cpu_data[0].split()
        app_cpu1 = None
        if self.pkg_info['pid'] is not None:
            Cpu_app_data = self.Read_Proc('%s/stat' % self.pkg_info['pid'])[0].split()
            if len(Cpu_app_data) > 20:
                app_cpu1 = float(Cpu_app_data[13]) + float(Cpu_app_data[14]) + float(Cpu_app_data[15]) + float(
                        Cpu_app_data[16])
        idle = float(Cpu_data[4])
        user = float(Cpu_data[1]) + float(Cpu_data[2])
        system = float(Cpu_data[3]) + float(Cpu_data[6]) + float(Cpu_data[7])  # 待确认
        iowait = float(Cpu_data[5])
        total = idle + user + system + iowait

        if self.cpu_temp['idle'] is not None:
            cpu_result_temp = dict()
            cpu_per = total - self.cpu_temp['total']
            cpu_result_temp['cpu_User'] = str("%.3f" % ((user - self.cpu_temp['user']) / cpu_per * 100))
            cpu_result_temp['cpu_Sys'] = str("%.3f" % ((system - self.cpu_temp['system']) / cpu_per * 100))
            cpu_result_temp['cpu_iowait'] = str("%.3f" % ((iowait - self.cpu_temp['iowait']) / cpu_per * 100))
            cpu_result_temp['cpu_Total'] = str("%.3f" % ((cpu_per - idle + self.cpu_temp['idle']) / cpu_per * 100))
            if self.cpu_temp['cpu_app'] is not None and app_cpu1 is not None:
                cpu_result_temp['cpu_app'] = str("%.3f" % ((app_cpu1 - self.cpu_temp['cpu_app']) / cpu_per * 100))
                if float(cpu_result_temp['cpu_app']) < 0:
                    cpu_result_temp['cpu_app'] = None
            else:
                cpu_result_temp['cpu_app'] = None
            if float(cpu_result_temp['cpu_Total']) < 0 or float(cpu_result_temp['cpu_User']) < 0 or float(
                    cpu_result_temp['cpu_Sys']) < 0:
                # print('zero###############################')
                return None
            else:
                self.cpu_result = cpu_result_temp
                self.__record(' '.join(['[' + self.pkg_info['pkg_name'] + ']', 'CPU_Result']), self.cpu_result)

        self.cpu_temp['idle'] = idle
        self.cpu_temp['user'] = user
        self.cpu_temp['system'] = system
        self.cpu_temp['iowait'] = iowait
        self.cpu_temp['total'] = total
        self.cpu_temp['cpu_app'] = app_cpu1

    def mon_run(self):
        interval = 5
        while True:
            thrs = list()
            t0 = threading.Thread(target=self.get_pkg())
            t0.start()
            thrs.append(t0)
            t1 = threading.Thread(target=self.And_Memory())
            t1.start()
            thrs.append(t1)
            t2 = threading.Thread(target=self.And_Cpu())
            t2.start()
            thrs.append(t2)
            t3 = threading.Thread(target=self.And_AppMem())
            t3.start()
            thrs.append(t3)
            for t in thrs:
                t.join()

            sleep(interval)


test = CpuMencontrol('com.meizu.media.camera', '80QBDNC2223T')

# cpuinfo = test.And_Cpu()
# sysmem = test.And_Memory()
# appmem = test.And_AppMem

test.mon_run()