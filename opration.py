import os
import shutil
import subprocess


class Operation(Object):
    def __init__(self, sn):
        self.sn = sn

    def __getprcocessname(self, pid):
        # pid = templine[2]
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

    def excucmd(self, dirc, name):
        procdir = dirc + '\\' + name
        if os.path.exists(dirc):
            if os.path.exists(procdir):
                shutil.rmtree(procdir)
                # os.listdir(procdir)
            os.mkdir(procdir)

            io_dir1 = procdir + r'\io_result'
            sql_dir1 = procdir + r'\sql_result'
            # diskwork_dir1 = procdir + r'\disk_result'
            if os.path.exists(procdir):
                os.mkdir(io_dir1)
                os.mkdir(sql_dir1)
                # os.mkdir(diskwork_dir1)

            iolog = io_dir1 + r"\iolog_" + name
            sqllog = sql_dir1 + r"\sqllog_" + name
            # disklog = diskwork_dir1 + r"\disklog_" + name

            iocmd = 'adb -s ' + self.sn + ' logcat -s "Perf_IO" > ' + iolog
            sqlcmd = 'adb -s ' + self.sn + ' logcat -s "SQLiteConnection" >  ' + sqllog
            # diskcmd = 'adb -s ' + self.sn + ' shell packagemonitor > ' + disklog

            mcmd = 'adb -s ' + self.sn + ' shell monkey -p ' + name + ' --ignore-crashes --ignore-timeouts ' \
                                                                      '--ignore-security-exceptions ' \
                                                                      '--kill-process-after-error --pct-trackball 0 ' \
                                                                      '--pct-nav 0 --pct-majornav 0 --pct-anyevent 0 '\
                                                                      '-v -v -v --throttle 500 ' + str(self.eventtimes)

            io = subprocess.Popen(iocmd, shell=True, executable='C:\Windows\System32\cmd.exe',
                                  stdout=subprocess.PIPE)
            sql = subprocess.Popen(sqlcmd, shell=True, executable='C:\Windows\System32\cmd.exe',
                                   stdout=subprocess.PIPE)
            # disk = subprocess.Popen(diskcmd, shell=True, executable='C:\Windows\System32\cmd.exe',
            #                        stdout=subprocess.PIPE)
            m = subprocess.Popen(mcmd, shell=True, executable='C:\Windows\System32\cmd.exe',
                                 stdout=subprocess.PIPE)

            mout = m.communicate()

            if ':Monkey:' == mout[0].split()[0]:
                io.kill()
                sql.kill()
                # disk.kill()
                m.kill()

                self.dealwithiofile(iolog)
                self.dealwithsqlfile(sqllog)
                # self.dealwithdiskwordfile(disklog)

                self.kill(name)

        else:
            print 'Error,check process ' + name

    def makedirc(self, dirname):
        """ Make a new directory """
        



