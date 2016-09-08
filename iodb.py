# coding = utf-8
# !/usr/bin/python

import os
import shutil
import subprocess


class IODB(object):
    def __init__(self, sn, eventtimes):
        self.sn = sn
        self.eventtimes = eventtimes
        pass

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
                # if os.path.exists(io_dir1):
                #     shutil.rmtree(io_dir1)
                # if os.path.exists(sql_dir1):
                #     shutil.rmtree(sql_dir1)
                # if os.path.exists(diskwork_dir1):
                #     shutil.rmtree(diskwork_dir1)
                #     os.listdir(procdir)
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
                                                                      '--ignore-security-exceptions --kill-process-after-error ' \
                                                                      '--pct-trackball 0 --pct-nav 0 --pct-majornav 0 --pct-anyevent 0 ' \
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

    # def verifedmode(self):
    #     print 'open the app you need to test\n'
    #     time.sleep(3)  # wait for 3 secs
    #
    #     os.system('adb devices')
    #
    #     temp = os.popen('adb -s ' + self.sn + ' shell dumpsys window ^|grep mFocusedApp=AppWindowToken').read()
    #     if len(temp.split()) > 5:
    #         focusedapp = temp.split()[-2].split('/')[0]
    #
    #         if focusedapp:
    #             print 'Process : ' + focusedapp
    #             dirc = raw_input('Please input rusult address: ')
    #             excucmd(dirc, focusedapp)
    #         else:
    #             print 'cannot get app need to be tested.'
    #             sys.exit(0)
    #     else:
    #         print temp
    #         print 'excute adb command error...'

    def autoMonkey(self):
        # dirc = raw_input('Please input rusult address: ')
        dirc = os.getcwd() + '\\io_result'

        if os.path.exists(dirc):
            shutil.rmtree(dirc)
        os.mkdir(dirc)
        with open(os.getcwd() + r'\Appinfo.txt', 'r') as packagename:
            for n in packagename.readlines():
                name = n.strip().split('/')[0]
                self.excucmd(dirc, name)

    def dealwithsqlfile(self, infile):
        pid_before = 0
        # infile = raw_input('Please input SQL_File log address: ')

        dir1 = os.path.dirname(infile)
        if os.path.exists(dir1):

            with open(infile, 'r') as iofile:
                # regex = '[\d]+'
                # patten = re.compile(regex, re.M | re.I)
                for line in iofile.readlines():
                    templine = line.strip('\n').split()
                    # matchobj = patten.search(line)

                    if len(templine) > 8:
                        # pid = matchobj.group()
                        pid = templine[2]

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
                            fileadd = dir1 + '\\' + pid + ' ' + proc
                        if templine[6].startswith('executeFor') or templine[6].startswith('prepare'):
                            for c in templine:
                                if 'sql' in c and 'PRAGMA' not in c and 'android_metadata' not in c:
                                    i = templine.index(c)

                                    with open(dir1 + '\\' + 'a_sqlinfo', 'a+') as resultfile:
                                        info = '\t'.join([pid, proc, templine[6], ' '.join(templine[i:]), templine[8]])
                                        resultfile.write(info)
                                        resultfile.write('\n')

                        if os.path.isfile(fileadd):
                            with open(fileadd, 'a+') as tempfile2:
                                tempfile2.write(line)
                        if not os.path.isfile(fileadd):
                            with open(fileadd, 'w+') as tempfile1:
                                tempfile1.write(line)
                            print 'initialize SQL file:' + dir1 + '\\' + pid + ' ' + proc

                        pid_before = pid

        print os.listdir(dir1)
        print '\n'
        print r'Go ' + dir1 + ', check SQL opration in mainthread'

    def dealwithdiskwordfile(self, infile):
        procdic = {}
        inode0count = 0

        dir1 = os.path.dirname(infile)
        fileadd = dir1 + '\\disk_result'
        if os.path.exists(dir1):
            with open(infile, 'r') as diskworkfile:

                for lines in diskworkfile.readlines():
                    line = lines.strip().split()
                    if len(line) > 5:
                        if line[4] in 'bytes':
                            if line[1] in procdic.keys():
                                procdic[line[1]] += int(line[-3])
                            else:
                                procdic[line[1]] = int(line[-3])
                        elif line[1] in 'port':
                            inode0count += int(line[6])
                            procdic["inode = 0"] = inode0count

                templist1 = sorted(procdic.iteritems(), key=lambda d: d[1], reverse=True)
                if os.path.isfile(fileadd):
                    os.remove(fileadd)
                for t_item in templist1:
                    print t_item[0], t_item[1]
                    with open(fileadd, 'a+') as diskfile:
                        diskfile.write(t_item[0] + '          ' * 2 + str(t_item[1]) + ' bytes' + '\n')
                        # diskfile.write('\n')

        print os.listdir(dir1)
        print '\n'
        print 'Go ' + dir1 + ', check diskwork result in mainthread'

    def dealwithiofile(self, infile):
        # infile = raw_input('Please input IO_File log address: ')

        dir1 = os.path.dirname(infile)
        if os.path.exists(dir1):
            with open(infile, 'r') as iofile:
                # RegEx = "W/Perf_IO[\s][(][\s]+\d+[)]: opened file:([\s\S]*)W/Perf_IO[\s][(][\s]+\d+[)]: opened file:"
                # patten = re.compile(RegEx,re.M|re.I)

                for line in iofile.readlines():
                    if line.strip():
                        templine = line.strip().split()
                        # print templine
                        if templine and len(templine) > 8:
                            pid = templine[2]
                            proc = self.__getprcocessname(pid)
                            fileadd = dir1 + '\\' + pid + ' ' + proc + '.txt'
                            if templine[7] == 'opened':
                                filename = templine[8].split('/')[-2] + ' ' + templine[8].split('/')[-1]
                                l = line
                                if filename:
                                    print 'initialize IO file:' + filename
                            elif templine[7] in 'read':
                                t = templine[-3]
                                # l = line
                                if 'readCount:' in t and int(t.split(':')[1]) >= 0:
                                    l = '*[WARNING ' + t.split(':')[
                                        1] + '] ' + line  # logger:*[WARNING FileSize']+lineinfo
                                    print l
                            elif templine[7] in 'write':
                                t1 = templine[8]
                                if 'byteCount' in t1 and int(t1.split(':')[1]) >= 0:
                                    l = '*[WARNING ' + t1.split(':')[
                                        1] + '] ' + line  # logger:*[WARNING FileSize']+lineinfo
                                    print l
                            elif templine[7] == 'closed':
                                l = line
                            else:
                                l = None
                            if l and fileadd:
                                if os.path.isfile(fileadd):
                                    with open(fileadd, 'a+') as tempfile2:
                                        tempfile2.write(l)
                                if not os.path.isfile(fileadd):
                                    with open(fileadd, 'w+') as tempfile1:
                                        tempfile1.write(l)

        print os.listdir(dir1)
        print '\n'
        print 'Go ' + dir1 + ', check IO opration in mainthread'


a = IODB('M96GAEP5UKV93', 50)
a.autoMonkey()
