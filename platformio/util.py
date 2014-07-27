# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import getcwd, listdir, utime
from os import name as os_name
from os.path import dirname, expanduser, isfile, join, realpath
from platform import architecture, system
from subprocess import PIPE, Popen
from time import sleep

from platformio.exception import NotPlatformProject
from serial import Serial

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


def get_system():
    return (system() + architecture()[0][:-3]).lower()


def get_home_dir():
    return expanduser("~/.platformio")


def get_source_dir():
    return dirname(realpath(__file__))


def get_project_dir():
    return getcwd()


def get_project_config():
    path = join(get_project_dir(), "platformio.ini")
    if not isfile(path):
        raise NotPlatformProject()
    cp = ConfigParser()
    cp.read(path)
    return cp


def get_platforms():
    platforms = []
    for p in listdir(join(get_source_dir(), "platforms")):
        if p.startswith("_") or not p.endswith(".py"):
            continue
        platforms.append(p[:-3])
    return platforms


def change_filemtime(path, time):
    utime(path, (time, time))


def exec_command(args):
    use_shell = get_system() == "windows32"
    p = Popen(args, stdout=PIPE, stderr=PIPE, shell=use_shell)
    out, err = p.communicate()
    return dict(out=out.strip(), err=err.strip())


def reset_serialport(port):
    s = Serial(port)
    s.flushInput()
    s.setDTR(False)
    s.setRTS(False)
    sleep(0.1)
    s.setDTR(True)
    s.setRTS(True)
    s.close()


def get_serialports():
    if os_name == "nt":
        from serial.tools.list_ports_windows import comports
    elif os_name == "posix":
        from serial.tools.list_ports_posix import comports
    else:
        raise GetSerialPortsError(os_name)
    return[{"port": p, "description": d, "hwid": h} for p, d, h in comports()]
