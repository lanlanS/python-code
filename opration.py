import os
import shutil
import subprocess
import sys
import time

ISOTIMEFORMAT = '%Y-%m-%d %Hh%Mm'


class OPRATION:
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

    def killproc(self, proc):
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
                kout1 = self.killproc(proc)
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


op = OPRATION('M96GAEP5UKV93', 55)

op.getprcocessname()
op.runmonkey()