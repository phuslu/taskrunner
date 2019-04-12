#!/usr/bin/env python
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


def do_job(name: str, command: str, timeout: object):
    """call a shell command"""
    filename = name + '.log'
    with open(filename, 'ab') as file:
        returncode = subprocess.call(command, stdout=file, stderr=subprocess.STDOUT, shell=True, timeout=timeout)
    logging.info('job=%r run command=%r return %r', name, command, returncode)
    if os.path.getsize(filename) >= CONFIG['default']['log_size']:
        os.rename(filename, filename+'.1')


def start_background_scheduler():
    """start a background scheduler"""
    for key, value in CONFIG.get('enviroment', {}).items():
        os.environ[key] = value
        os.environ[key.upper()] = value
    scheduler = apscheduler.schedulers.background.BackgroundScheduler()
    for name, kwargs in CONFIG['job'].items():
        minute, hour, day, month, day_of_week = kwargs['cron'].split()
        scheduler.add_job(do_job, 'cron', args=(name, kwargs['command'], kwargs.get('timeout')),
                          minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week)
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

