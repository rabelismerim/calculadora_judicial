@echo off

set "celery_log_filename=log\celery_%date:/=-%.txt"

e:
cd E:\wwwroot\fadigitallab.deloitte.com.br\juca

start venv\Scripts\celery -A config control shutdown

echo Aguardar alguns segundos para permitir que os processo antigos do celery seja finalizado
echo O diretório atual é: %CD%
timeout /t 5

start /b venv\Scripts\celery -A config worker --pool=eventlet --loglevel=INFO -Q default,save-file -E --logfile=%celery_log_filename%
