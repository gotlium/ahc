#-- coding: utf-8 --#
__author__ = 'gotlium'

import os

from libraries.helpers import *
from libraries.fs import delFile


# TODO: backup, migrate, imports - methods
class Vbox(object):
    methods = ('add', 'delete',)

    def __init__(self, base):
        self.base = base
        self.configs = dict(base.vbox)

    def __getIfName(self):
        vms = system('VBoxManage list vms')
        host_only_if = 'vboxnet0'
        if not vms:
            check_cmd = str('VBoxManage hostonlyif ipconfig '
                            'vboxnet0 --ip 192.168.57.1 >& /dev/null')
            if os.system(check_cmd) != 0:
                host_only_if = system(
                    "VBoxManage hostonlyif create ipconfig vboxnet0 "
                    "--ip 192.168.57.1 --netmask 255.255.255.0 "
                    "2>&1|tail -1|cut -d\\' -f2",
                    True)
        return host_only_if

    def __getDrivePath(self):
        return system(
            "VBoxManage list systemproperties | "
            "awk '/^Default.machine.folder/ { print $4 }'",
            True)

    def __checkAll(self, vm, remove=False):
        if not vm:
            error_message('VM is not set!')
        if not fileExists(self.configs['iso']):
            error_message('ISO is not set!')
        if not system('which VBoxManage'):
            error_message('VirtualBox is not installed!')
        if not remove and fileExists(self.configs['vm_path']):
            error_message('VM is installed!')
        elif remove and not fileExists(self.configs['vm_path']):
            error_message('VM is not installed!')

    def __initConfig(self, vm):
        self.configs['vm'] = vm
        self.configs['hdd_size'] = int(self.configs['hdd_size']) * 1024
        self.configs['host_only_if'] = self.__getIfName()
        self.configs['drive_path'] = self.__getDrivePath()
        self.configs['hdd'] = '%s/%s/%s.vdi' % (
            self.configs['drive_path'], vm, vm)
        self.configs['vm_path'] = '%s/%s' % (self.configs['drive_path'], vm)

    def __createDataDir(self):
        os.makedirs(self.configs['vm_path'])

    def __configureNewVM(self):
        commands = [
            'createvm --name %(vm)s --ostype %(ostype)s --register',
            'createhd --filename "%(hdd)s" --size %(hdd_size)d',
            'modifyvm %(vm)s --memory %(memory)s ',
            'modifyvm %(vm)s --acpi on',
            'modifyvm %(vm)s --boot1 dvd',
            'modifyvm %(vm)s --nic1 nat',
            'modifyvm %(vm)s --cpus %(number_of_cpu)s',
            'modifyvm %(vm)s --nic2 hostonly',
            'modifyvm %(vm)s --hostonlyadapter2 %(host_only_if)s',
            'storagectl %(vm)s --name "IDE Controller" --add '
            'ide --controller PIIX4',
            'storageattach %(vm)s --storagectl "IDE Controller" --port 0 '
            '--device 0 --type hdd --medium "%(hdd)s"',
            'storageattach %(vm)s --storagectl "IDE Controller" --port 0 '
            '--device 1 --type dvddrive --medium %(iso)s',
        ]
        for cmd in commands:
            system_by_code(
                str('VBoxManage ' + cmd + ' >& /dev/null') % self.configs
            )

    def __runVMWithVNC(self):
        system(
            'nohup VBoxHeadless -s %(vm)s -n -o %(vnc_password)s '
            '>& /dev/null &' % self.configs)

    def __removeVM(self):
        system_by_code('VBoxManage modifyvm %(vm)s –hda none' % self.configs)
        system_by_code('VBoxManage unregistervm %(vm)s –delete' % self.configs)

    def __createInitFile(self):
        init_name = 'vbox.%(vm)s' % self.configs
        init_path = '/etc/init.d/%s' % init_name
        putFile(init_path, getTemplate('vbox-init') % self.configs)
        os.system('chmod +x %s' % init_path)
        os.system('update-rc.d %s defaults >& /dev/null' % init_name)

    def __removeInitFile(self):
        init_name = 'vbox.%(vm)s' % self.configs
        os.system('update-rc.d -f %s remove >& /dev/null' % init_name)
        delFile('/etc/init.d/%s' % init_name)

    def __showMessage(self):
        info_message('VM successful added!')
        info_message('VNC listening on TCP port 5900')
        info_message(
            'You can manage Guest OS by following command: '
        )
        info_message(
            'service vbox.%(vm)s [stop|start]' % self.configs, 'cyan'
        )

    def add(self, vm):
        self.__initConfig(vm)
        self.__checkAll(vm)
        self.__createDataDir()
        self.__configureNewVM()
        self.__createInitFile()
        self.__runVMWithVNC()
        self.__showMessage()

    def delete(self, vm):
        self.__initConfig(vm)
        self.__checkAll(vm, True)
        self.__removeInitFile()
        self.__removeVM()

        info_message('Successful!')
