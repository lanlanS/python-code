#!/usr/bin/evn python
# -*- coding:utf-8 -*-

# FileName adbtools.py
# Created Time: 2016/9/13
"""
adb 工具类
"""

import os
import platform
import re
import time


class AdbTools(object):
    def __init__(self, device_id=''):
        self.system = platform.system()
        self.find = ''
        self.command = ''
        self.device_id = device_id
        self.__get_find()
        self.__check_adb()
        self.__connection_devices()

    def __get_find(self):
        """
        判断系统类型，windows使用findstr，linux使用grep
        :return:
        """
        if self.system is "Windows":
            self.find = "findstr"
        else:
            self.find = "grep"

    def __check_adb(self):
        """
        检查adb
        判断是否设置环境变量ANDROID_HOME
        :return:
        """
        if "ANDROID_HOME" in os.environ:
            if self.system == "Windows":
                path = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb.exe")
                if os.path.exists(path):
                    self.command = path
                else:
                    raise EnvironmentError(
                            "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])
            else:
                path = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb")
                if os.path.exists(path):
                    self.command = path
                else:
                    raise EnvironmentError(
                            "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])
        else:
            raise EnvironmentError(
                    "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])

    def __connection_devices(self):
        """
        连接指定设备，单个设备可不传device_id
        :return:
        """
        if self.device_id == "":
            return
        self.device_id = "-s %s" % self.device_id

    def adb(self, args):
        """
        执行adb命令
        :param args:参数
        :return:
        """
        cmd = "%s %s %s" % (self.command, self.device_id, str(args))
        return os.popen(cmd)

    def shell(self, args):
        """
        执行adb shell命令
        :param args:参数
        :return:
        """
        cmd = "%s %s shell %s" % (self.command, self.device_id, str(args))
        return os.popen(cmd)

    def get_devices(self):
        """
        获取设备列表
        :return:
        """
        l = self.adb('devices').readlines()
        return (i.split()[0] for i in l if 'devices' not in i and len(i) > 5)

    def get_package(self):
        """
        获取当前运行app包名
        :return:
        """
        result = self.shell('dumpsys window w | %s \/ | %s name=' % (self.find, self.find)).read()
        reg = re.compile(r'name=(.+?)/')
        return re.findall(reg, result)[0]

    def get_pid(self, package_name):
        """
        获取pid
        :return:
        """
        if self.system is "Windows":
            pid_command = self.shell("ps | %s %s$" % (self.find, package_name)).read()
        else:
            pid_command = self.shell("ps | %s -w %s" % (self.find, package_name)).read()

        if pid_command == '':
            return "the process doesn't exist."

        req = re.compile(r"\d+")
        result = str(pid_command).split()
        result.remove(result[0])
        return req.findall(" ".join(result))[0]

    def get_uid(self, pid):
        """
        获取uid
        :param pid:
        :return:
        """
        result = self.shell("cat /proc/%s/status" % pid).readlines()
        for i in result:
            if 'uid' in i.lower():
                return i.split()[1]

    @staticmethod
    def dump_apk(path):
        """
        dump apk文件
        :param path: apk路径
        :return:
        """
        # 检查build-tools是否添加到环境变量中
        # 需要用到里面的aapt命令
        l = os.environ['PATH'].split(';')
        build_tools = False
        for i in l:
            if 'build-tools' in i:
                build_tools = True
        if not build_tools:
            raise EnvironmentError("ANDROID_HOME BUILD-TOOLS COMMAND NOT FOUND.\nPlease set the environment variable.")
        return os.popen('aapt dump badging %s' % (path,))

    def pull(self, source, target):
        """
        从手机端拉取文件到电脑端
        :param target: string target address
        :param source: string source address
        :return:
        """
        self.adb('pull %s %s' % (source, target))

    def remove(self, path):
        """
        从手机端删除文件
        :return:
        """
        self.shell('rm %s' % (path,))

    def clear_app_data(self, package):
        """
        清理应用数据
        :return:
        """
        self.shell('pm clear %s' % (package,))

    def install(self, path):
        """
        安装apk文件
        :return:
        """
        # adb install 安装错误常见列表
        errors = {'INSTALL_FAILED_ALREADY_EXISTS': '程序已经存在',
                  'INSTALL_FAILED_INVALID_APK': '无效的APK',
                  'INSTALL_FAILED_INVALID_URI': '无效的链接',
                  'INSTALL_FAILED_INSUFFICIENT_STORAGE': '没有足够的存储空间',
                  'INSTALL_FAILED_DUPLICATE_PACKAGE': '已存在同名程序',
                  'INSTALL_FAILED_NO_SHARED_USER': '要求的共享用户不存在',
                  'INSTALL_FAILED_UPDATE_INCOMPATIBLE': '版本不能共存',
                  'INSTALL_FAILED_SHARED_USER_INCOMPATIBLE': '需求的共享用户签名错误',
                  'INSTALL_FAILED_MISSING_SHARED_LIBRARY': '需求的共享库已丢失',
                  'INSTALL_FAILED_REPLACE_COULDNT_DELETE': '需求的共享库无效',
                  'INSTALL_FAILED_DEXOPT': 'dex优化验证失败',
                  'INSTALL_FAILED_OLDER_SDK': '系统版本过旧',
                  'INSTALL_FAILED_CONFLICTING_PROVIDER': '存在同名的内容提供者',
                  'INSTALL_FAILED_NEWER_SDK': '系统版本过新',
                  'INSTALL_FAILED_TEST_ONLY': '调用者不被允许测试的测试程序',
                  'INSTALL_FAILED_CPU_ABI_INCOMPATIBLE': '包含的本机代码不兼容',
                  'CPU_ABIINSTALL_FAILED_MISSING_FEATURE': '使用了一个无效的特性',
                  'INSTALL_FAILED_CONTAINER_ERROR': 'SD卡访问失败',
                  'INSTALL_FAILED_INVALID_INSTALL_LOCATION': '无效的安装路径',
                  'INSTALL_FAILED_MEDIA_UNAVAILABLE': 'SD卡不存在',
                  'INSTALL_FAILED_INTERNAL_ERROR': '系统问题导致安装失败',
                  'DEFAULT': '未知错误'
                  }
        print('Installing...')
        l = self.adb('install %s' % (path,)).read()
        if 'Success' in l:
            print('Install Success')
        if 'Failure' in l:
            reg = re.compile('\\[(.+?)\\]')
            key = re.findall(reg, l)[0]
            print('Install Failure >> %s' % (errors[key],))

    def uninstall(self, package):
        """
        卸载apk
        :param package: 包名
        :return:
        """
        print('Uninstalling...')
        l = self.adb('uninstall %s' % (package,)).read()
        print(l)

    def screenshot(self, target_path=''):
        """
        手机截图
        :param target_path: 目标路径
        :return:
        """
        format_time = self.timestamp('%Y%m%d%H%M%S')
        self.shell('screencap -p /sdcard/%s.png' % (format_time,))
        time.sleep(1)
        if target_path == '':
            self.adb('pull /sdcard/%s.png %s' % (format_time, os.path.expanduser('~')))
        else:
            self.adb('pull /sdcard/%s.png %s' % (format_time, target_path))
        self.shell('rm /sdcard/%s.png' % (format_time,))

    @staticmethod
    def timestamp(format_time):
        """
        获取当前时间
        :return:
        """
        return time.strftime(format_time, time.localtime(time.time()))


if __name__ == '__main__':
    pass
