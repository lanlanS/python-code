#!/usr/bin/evn python
# -*- coding:utf-8 -*-

# FileName adbtools.py
# Created Time: 2016/9/15
"""
 基本操作类
"""

import os
import shutil
import subprocess
import logging
import time

ISOTIMEFORMAT = '%Y-%m-%d %Hh%Mm'
log = logging.getLogger("debug")


class OPRATION(object):
    def __init__(self, sn, eventtimes):
        self.sn = sn
        self.eventtimes = eventtimes

        '''init resultdir'''
        resultdir = time.strftime(ISOTIMEFORMAT, time.localtime())
        if os.path.exists(os.getcwd() + '\\' + resultdir):
            shutil.rmtree(os.getcwd() + '\\' + resultdir)
        os.mkdir(os.getcwd() + '\\' + resultdir)

    def getprcocessname(self, pid):
        pid_before = 0

        if pid_before != pid and pid != 'of':
            p = subprocess.Popen('adb -s ' + self.sn + ' shell ps ' + pid, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
            output = p.communicate()
            b = output[0]
            if b and b.split()[-1] not in 'NAME':
                proc = b.split()[-1].replace('/', '_')
            else:
                proc = 'Unkonw'
                print 'cannot find the process,check PID: ' + pid
            return proc

    def __killproc(self, proc):
        """
        :type proc: String
        """
        killcmd = 'adb -s ' + self.sn + ' shell am force-stop ' + proc
        k = subprocess.Popen(killcmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        kout = k.communicate()
        k.kill()
        print proc + ' has been killed..'
        return kout

    def kill(self, proc):
        grepcmd = 'adb -s ' + self.sn + ' shell ps |grep monkey'
        k = subprocess.Popen(grepcmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        kout = k.communicate()
        if not kout[0]:
            if proc not in "settings" or "dailer" or "mms" or "launcher" or "systemui":
                kout1 = self.__killproc(proc)
                if kout1[0] == '':
                    print proc + '_Monkey test compeleted.'
                else:
                    print "check process: " + proc + ",connot be killed !"

        os.system('adb kill-server')
        os.system('adb devices')
        pass

    def runmonkey(self, pname):
        """
        execute monkey test process by process
        :param pname:process name
        :return: monkey execution result
        """
        mcmd = 'adb -s ' + self.sn + ' shell monkey -p ' + pname + ' --ignore-crashes --ignore-timeouts ' \
                                                                   '--ignore-security-exceptions ' \
                                                                   '--kill-process-after-error --pct-trackball 0 ' \
                                                                   '--pct-nav 0 --pct-majornav 0 --pct-anyevent 0 ' \
                                                                   '-v -v -v --throttle 500 ' + str(self.eventtimes)
        m = subprocess.Popen(mcmd, shell=True, executable='C:\Windows\System32\cmd.exe',
                             stdout=subprocess.PIPE)

        mout = m.communicate()
        return mout

    def makedirc(self, dir):
        """ Make a new directory """
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)

        if os.path.exists(dir):
            return True
        else:
            return False

    def getallapp(self):
        appfile = os.getcwd() + '\\Appinfo.txt'
        f = open(appfile, 'r')
        # f = open(r'E:\app_bootup\application-boot-up-speed\database\flyme_app_list.txt','r')

        os.mkdir('./dumpsys')
        applist = f.readlines()


op = OPRATION('M95QACNS339EN', 55)

mout = op.runmonkey('com.meizu.mstore')
if ':Monkey:' == mout[0].split()[0]:
    op.kill('com.meizu.mstore')
