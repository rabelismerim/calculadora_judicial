@echo off

set "celery_log_filename=log\celery_%date:/=-%.txt"

c:
cd C:\inetpub\wwwroot\juca

start venv\Scripts\python -m celery -A config control shutdown

echo Aguardar alguns segundos para permitir que os processo antigos do celery seja finalizado
timeout /t 5

start /b venv\Scripts\python -m celery -A config worker --pool=threads --loglevel=INFO -Q default,save-file -E --logfile=%celery_log_filename% --concurrency 12
