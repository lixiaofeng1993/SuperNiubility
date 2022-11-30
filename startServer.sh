# !/bin/sh
PROCESS=`ps -e | grep gunicorn | awk '{printf "%d\n", $1}'`

echo $PROCESS

for i in $PROCESS

do
        echo "Kill the gunicorn process [ $i ]"
        sudo kill -9 $i
done

echo 'stop server finish!'

cd /www/wwwroot/SuperNiubility

gunicorn -c /www/wwwroot/SuperNiubility/gunicorn.py SuperNiubility.wsgi:application

echo 'start 0 finish！'
sleep 2s

cd /www/wwwroot/webserver/SuperNiubility

gunicorn -c /www/wwwroot/webserver/SuperNiubility/gunicorn.py SuperNiubility.wsgi:application

echo 'start 1 finish！'