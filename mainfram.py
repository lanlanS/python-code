#!/usr/bin/python
# -*- coding:cp936 -*-

from Tkinter import *
import adbhelper
import os
import phoneinfo
import iodb


def testa():
    print 'testa'


def testb():
    print 'testb'


def initwin(sn, version):
    """初始化窗口Root"""
    root = Tk()
    root.title("Perf Tools Set")
    root.geometry('700x400')
    root.resizable(width=False, height=True)

    """初始化主界面框架"""
    frm = Frame(root)
    # top frame:basic info
    frm_t = Frame(frm)
    frm_tt = Frame(frm_t)
    Label(frm_tt, text='Perf Tools Set', font=('Arial', 15)).pack(side=LEFT)
    Label(frm_t, text='Phone sn number: ' + sn, font=('Arial', 15)).pack(side=BOTTOM)
    Label(frm_t, text='Frameware verson: ' + version, font=('Arial', 15)).pack(side=BOTTOM)
    frm_tt.pack(side=LEFT)
    frm_t.pack(side=TOP)

    # under frame:buttom frame
    frm_mb = Frame(frm)
    Button(frm_mb, text="一键执行".decode('gbk').encode('utf-8'), command=testa, width=20, height=2,
           font=('Arial', 10)).pack(side=TOP)
    Button(frm_mb, text="专项执行".decode('gbk').encode('utf-8'), command=testb, width=20, height=2,
           font=('Arial', 10)).pack(side=BOTTOM)
    frm_mb.pack(side=BOTTOM)

    frm.pack()

    root.mainloop()


def getdevices(i=0):
    sn = None
    # f = subprocess.Popen('adb devices')
    f = os.popen("adb devices")
    tempsn = f.read()
    f.close()

    temp = tempsn.strip().split("\n")
    if len(temp) == 2:
        sn = temp[1].split("\t")[0]
    elif len(temp) == 4:
        sn = temp[3].split("\t")[0]

    i += 1
    while i < 5:
        getdevices(i)

        if sn:
            # print sn
            return sn

        elif sn == None:
            # print i
            print('check usb connection, cannot get sn number.\n ')
            sys.exit(0)


sn = getdevices()
if sn:

    testphone = adbhelper.ADB(sn)
    version = testphone.adbshell('getprop ^|grep ro.build.inside.id').split(':')[1]

    initwin(sn, version)
