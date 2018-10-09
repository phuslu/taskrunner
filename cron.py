#!/usr/bin/env python
#coding:utf-8
# pylint: disable=too-many-statements, line-too-long

import logging
import os
import time
import subprocess
import sys

import apscheduler.schedulers.background
import apscheduler.triggers.cron
import toml

sys.dont_write_bytecode = True
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['PATH'] = os.path.dirname(sys.executable) + os.pathsep + os.environ['PATH']
CONFIG = toml.load(os.getenv('ENV', 'development') + '.toml')
logging.basicConfig(format=CONFIG['default']['log_format'], level=getattr(logging, CONFIG['default']['log_level'].upper()))


def make_job(cmd):
    """make a shell job"""
    func = lambda: subprocess.call(cmd, shell=True)
    func.__qualname__ = cmd
    return func


def start_background_scheduler():
    """start a background scheduler"""
    for key, value in CONFIG.get('enviroment', {}).items():
        os.environ[key] = value
        os.environ[key.upper()] = value
    lines = [x.strip() for x in open(CONFIG['default']['crontab']) if x.strip() and not x.strip().startswith('#')]
    scheduler = apscheduler.schedulers.background.BackgroundScheduler()
    for line in lines:
        minute, hour, day, month, day_of_week, cmd = line.split(sep=None, maxsplit=5)
        scheduler.add_job(make_job(cmd), 'cron', minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week)
    scheduler.start()
    return scheduler


def main():
    """main scheduler"""
    scheduler = start_background_scheduler()
    crontab = CONFIG['default']['crontab']
    last_mtime = os.path.getmtime(crontab)
    while True:
        time.sleep(1)
        mtime = os.path.getmtime(crontab)
        if mtime == last_mtime:
            continue
        logging.info('%r updated, restart scheduler.', crontab)
        scheduler.shutdown(wait=False)
        scheduler = start_background_scheduler()
        last_mtime = mtime


if __name__ == '__main__':
    main()
