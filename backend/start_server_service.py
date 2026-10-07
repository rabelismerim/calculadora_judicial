import datetime

import win32service
import win32serviceutil
import win32event
import subprocess
import sys
import os
import servicemanager

import shlex
import logging
from multiprocessing import Queue, Process

from decouple import config

# Inicio variáveis de edição por Ambiente
CURRENT_DIR = config('SERVICE_CURRENT_DIR', cast=str, default='')
APP_NAME = config('SERVICE_APP_NAME', cast=str, default='config')
POOL = config('SERVICE_POOL', cast=str, default='threads')
LOGLEVEL = config('SERVICE_LOGLEVEL', cast=str, default='INFO')
QUEUE = config('SERVICE_QUEUE', cast=str, default='')
CONCURRENCY = config('SERVICE_CONCURRENCY', cast=str, default='12')

# Fim variáveis de edição por Ambiente

PYTHON_PATH = f"{CURRENT_DIR}/venv/Scripts/python.exe"
exists = os.path.exists(PYTHON_PATH)
FOLDER_LOG = f"{CURRENT_DIR}/log"
os.makedirs(FOLDER_LOG, exist_ok=True)
FILE_LOG_PATH = os.path.join(FOLDER_LOG, f'{datetime.datetime.now().date()}_service.log')
CELERY_LOG_PATH = f'{FOLDER_LOG}/celery_{datetime.datetime.now().date()}.log'

logging.basicConfig(
    filename=FILE_LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)
logging.critical(FOLDER_LOG)
logging.critical(CURRENT_DIR)


def target_func(cmd, out_queue):
    try:
        args = shlex.split(cmd)
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            close_fds=True
        )

        out_queue.put(proc.pid)
        for line in iter(proc.stdout.readline, ''):
            logging.debug(line.strip())
        proc.stdout.close()
        proc.wait()
    except Exception as f:
        logging.error(f'Error in target_func for cmd: {cmd}')
        logging.error(f, exc_info=True)


class PythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CalculadoraJudicialStartServiceCelery"
    _svc_display_name_ = "CalculadoraJudicial Start Service Celery"
    _svc_description_ = "Service to start and stop CalculadoraJudicial Celery"
    timeout = 3000

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.run = True

    def SvcStop(self):
        logging.info(f'Stopping {self._svc_name_} service ...')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        self.run = False
        sys.exit()

    def run_command(self, command):

        try:
            output_queue = Queue()
            process = Process(target=target_func, args=(command, output_queue))
            process.start()
            pid = output_queue.get()
            logging.info(f'Command started: {command} with PID: {pid}')
            return process
        except Exception as e:
            logging.error(f'Error starting command: {command}')
            logging.error(e, exc_info=True)

    def logging_proc(self, proc):
        stdout, stderr = proc.communicate()
        logging.info('pid file append: {pid}'.format(pid=proc.pid))
        logging.info(f'stdout: {stdout}')
        logging.error(f'stderr: {stderr}')

    def shutdown_celery(self):
        logging.info(f'Stopping celery server...')
        celery_shutdown_command = f'{PYTHON_PATH} -m celery -A {APP_NAME} control shutdown'
        celery_shutdown_proc = self.run_command(celery_shutdown_command)
        celery_shutdown_proc.join(timeout=30)

    def run_celery(self):
        celery_command = f'{PYTHON_PATH} -m celery -A {APP_NAME} worker --pool={POOL} --loglevel={LOGLEVEL} -E -Q {QUEUE} --logfile={CELERY_LOG_PATH} --concurrency {CONCURRENCY}'
        self.shutdown_celery()

        logging.info(f'Starting celery server...')
        if self.run_command(celery_command):
            logging.info(f'Started celery server')
        else:
            logging.info(f'Unable to start celery server')

    def main(self):
        self.run_celery()

    def SvcDoRun(self):
        logging.info(f'Starting {self._svc_name_} service ...')
        os.chdir(CURRENT_DIR)
        logging.info('cwd: ' + os.getcwd())
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main()

    def await_stop(self):
        while self.run:
            try:
                win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

                servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                      servicemanager.PYS_SERVICE_STARTED,
                                      (self._svc_name_, ''))

                self.shutdown_celery()
                break
            except Exception as e:
                logging.error(e, exc_info=True)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PythonService)
