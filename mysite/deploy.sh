# deploy commands

# git pull
echo "git pull..."
git pull

# migrate
echo "making migrations..."
python manage.py makemigrations
echo "apply migrations..."
python manage.py migrate

# collect static
echo "collect statics..."
python manage.py collectstatic

# kill crun
echo "stop celery..."
./stopcrun.sh

# restart apache
echo "restart apachce"
sudo apache2ctl restart

# start crun
echo "starting celery..."
./crun.sh &
echo "starting celeryBeats..."
./cbeat.sh &
