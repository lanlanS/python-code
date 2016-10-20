#!/usr/bin/python
# coding=utf-8

import os


class Islargeheap():
    def __init__(self, pname):
        self.pname = pname

    def checkLargeheap(self):

        largeheap = []

        startapp = "adb shell am start " + self.pname.strip()
        os.system(startapp)
        os.system('sleep 3.5')

        dapp = self.pname.split('/')[0]

        cmd = "adb shell dumpsys meminfo " + dapp.strip()

        fd = os.popen(cmd)
        # tempinfo = fd.readlines()
        tempheap = fd.read().strip().split('\n')
        fd.close()

        for temp in tempheap:
            if 'isLargeHeap:' in temp:
                if 'true' in temp.split(':')[1]:
                    largeheap.append(dapp)
                    with open('./' + 'Largeheap_' + dapp, 'w') as appinfo:
                        appinfo.writelines(tempheap)

        os.system('sleep 1.5')


# test
c = Islargeheap('com.meizu.mstore')
c.checkLargeheap()
