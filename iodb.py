# coding=utf-8
# coding = utf-8
# !/usr/bin/python

import os
import shutil
import subprocess

import xlwt


class IODB(object):
    def __init__(self, sn, eventtimes):
        self.sn = sn
        self.eventtimes = eventtimes
        pass

    def __getprcocessname(self, pid_before, pid):
        # pid = templine[2]
        # pid_before = 0
        proc = 'Unkonw'
        if pid_before != pid and pid != 'of':
            p = subprocess.Popen('adb -s ' + self.sn + ' shell ps ' + pid, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
            output = p.communicate()
            b = output[0]
            if b and b.split()[-1] not in 'NAME':
                proc = b.split()[-1].replace('/', '_')
            else:
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
        sqlresult = {}

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
                        pid_before = pid

                        if templine[6].startswith('executeFor') or templine[6].startswith('prepare'):
                            for c in templine:
                                if 'sql' in c:
                                    i = templine.index(c)
                                    sql = ' '.join(templine[i:])
                                    if 'PRAGMA' not in sql and 'android_metadata' not in sql:
                                        key = ' '.join([pid, proc, templine[6], ' '.join(templine[i:])])
                                        if sqlresult.has_key(key):
                                            sqlresult[key] += 1
                                        if not sqlresult.has_key(key):
                                            sqlresult.setdefault(key, 1)

                        if os.path.isfile(fileadd):
                            with open(fileadd, 'a+') as tempfile2:
                                tempfile2.write(line)
                        if not os.path.isfile(fileadd):
                            with open(fileadd, 'w+') as tempfile1:
                                tempfile1.write(line)
                            print 'initialize SQL file:' + dir1 + '\\' + pid + ' ' + proc

                with open(dir1 + '\\' + 'sqlresult', 'a+') as resultfile:
                    sqlresult = sorted(sqlresult.iteritems(), key=lambda d: d[0].split()[0], reverse=True)
                    for lines in sqlresult:
                        # info = ('\t' * 3).join([lines, sqlresult[]])
                        resultfile.write(('\t' * 3).join([lines[0], str(lines[1])]))
                        resultfile.write('\n')

        print os.listdir(dir1)
        print '\n'
        print r'Go ' + dir1 + ', check SQL opration in mainthread'
        return dir1 + '\\' + 'sqlresult'

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
        ioresult = {}
        pidbefore = 0

        dir1 = os.path.dirname(infile)
        if os.path.exists(dir1):
            with open(infile, 'r') as iofile:
                for line in iofile.readlines():
                    if line.strip():
                        templine = line.strip().split()
                        # print templine
                        if templine and len(templine) > 8:
                            pid = templine[2]
                            proc = self.__getprcocessname(pidbefore, pid)
                            fileadd = dir1 + '\\' + pid + ' ' + proc + '.txt'
                            if templine[7] == 'opened':
                                filename = templine[8].split('/')[-2] + ' ' + templine[8].split('/')[-1]
                                l = line
                                if filename:
                                    print 'initialize IO file:' + filename

                                if any(s not in templine[8] for s in [r'/proc/', r'/sys/', '.apk', '.jar']):
                                    key = '   '.join([pid, proc, templine[8]])
                                    if ioresult.has_key(key):
                                        ioresult[key] += 1
                                    if not ioresult.has_key(key):
                                        ioresult.setdefault(key, 1)

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
                            pidbefore = pid
            with open(dir1 + '\\' + 'ioresult', 'a+') as resultfile:
                ioresult = sorted(ioresult.iteritems(), key=lambda d: d[0].split()[0], reverse=True)
                for lines in ioresult:
                    # info = ('\t' * 3).join([lines, sqlresult[]])
                    resultfile.write(('\t' * 3).join([lines[0], str(lines[1])]))
                    resultfile.write('\n')

        print os.listdir(dir1)
        print '\n'
        print 'Go ' + dir1 + ', check IO opration in mainthread'
        return dir1 + '\\' + 'ioresult'

    def write2excel(self, iotxtfile, sqltxtfile):

        f = xlwt.Workbook()  # 创建工作簿

        font0 = xlwt.Font()
        font0.name = 'Arial'
        font0.colour_index = 0
        font0.bold = True

        font1 = xlwt.Font()
        font1.name = 'Arial'
        font1.colour_index = 0
        font1.bold = False

        barBG = xlwt.Pattern()  # 设置背景
        barBG.pattern = barBG.SOLID_PATTERN
        # 灰色
        barBG.pattern_fore_colour = 23

        style0 = xlwt.XFStyle()
        style0.font = font0
        style0.pattern = barBG

        style1 = xlwt.XFStyle()
        style1.font = font1

        '''
             创建第一个sheet:
             File IO Result
        '''
        sheet1 = f.add_sheet('IO Result', cell_overwrite_ok=True)

        nrow_2 = 1

        sheet1.col(0).width = 256 * 10
        sheet1.col(1).width = 256 * 20
        sheet1.col(2).width = 256 * 100
        sheet1.col(3).width = 256 * 10

        sheet1.write(0, 0, 'PID', style0)
        sheet1.write(0, 1, 'Process Name ', style0)
        sheet1.write(0, 2, 'Opened File Name ', style0)
        sheet1.write(0, 3, 'Count ', style0)

        with open(iotxtfile, 'r') as infile:
            for lines in infile.readlines():
                line = lines.strip('\n').split()
                col_2 = 0
                for i in line:
                    sheet1.write(nrow_2, col_2, i, style1)
                    col_2 += 1
                nrow_2 += 1

        '''
        创建第二个sheet:
        Sql Result
        '''
        sheet2 = f.add_sheet('Sql Result', cell_overwrite_ok=True)

        nrow_2 = 1

        sheet2.col(0).width = 256 * 10
        sheet2.col(1).width = 256 * 20
        sheet2.col(2).width = 256 * 35
        sheet2.col(3).width = 256 * 100
        sheet2.col(4).width = 256 * 10

        sheet2.write(0, 0, 'PID', style0)
        sheet2.write(0, 1, 'Process Name', style0)
        sheet2.write(0, 2, 'Action', style0)
        sheet2.write(0, 3, 'SQL statement ', style0)
        sheet2.write(0, 4, 'Count ', style0)

        with open(sqltxtfile, 'r') as infile:
            for lines in infile.readlines():
                line = lines.strip('\n').split()
                col_2 = 0
                tlist = [line[0], line[1], line[2], line[3:-2], line[-1]]
                for i in tlist:
                    sheet2.write(nrow_2, col_2, i, style1)
                    col_2 += 1
                nrow_2 += 1

        savepath = os.getcwd() + r'\Reuslt.xls'
        f.save(savepath)
        if os.path.exists(savepath):
            print '\n'
            print r'Completed...\n Check result at ' + savepath


a = IODB('M96GAEP5UKV93', 50)
