# stop celery
ps auxww | grep -e 'celery' -e 'Celery' | awk '{print $2}' | xargs kill -9
