# start celery server
#python manage.py celery worker
celery -A mysite worker -l info

