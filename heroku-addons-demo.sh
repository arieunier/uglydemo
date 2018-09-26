#!/bin/bash

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
# set me
if [ $# -ne 1 ]
then
    echo "Usage : heroku-addons-add.sh APPLICATION_NAME"
    exit 1
fi

APPLICATION_NAME=$1

echo "######### Adding Redis addon"
heroku addons:create heroku-redis:premium-0 --app $APPLICATION_NAME

echo "######### Adding redismonitor"
heroku addons:create redismonitor:free --app $APPLICATION_NAME

echo "######### Adding Heroku Connect addon"
heroku addons:create herokuconnect --app $APPLICATION_NAME

echo "######### Updating environment variables"
heroku config:add STAGING_DATABASE_URL=`heroku config:get DATABASE_URL --app $APPLICATION_NAME` --app $APPLICATION_NAME

echo "######### Adding New relic"
heroku addons:create newrelic:hawke --app $APPLICATION_NAME
NEW_RELIC_LICENSE_KEY=`heroku config:get NEW_RELIC_LICENSE_KEY --app $APPLICATION_NAME`
newrelic-admin generate-config $NEW_RELIC_LICENSE_KEY newrelic.ini
heroku config:add NEW_RELIC_CONFIG_FILE='/app/newrelic.ini'  --app $APPLICATION_NAME
heroku config:add NEW_RELIC_LOG_LEVEL=debug --app $APPLICATION_NAME
heroku config:set NEW_RELIC_APP_NAME="$APPLICATION_NAME" --app $APPLICATION_NAME

echo "Adding Bucketeer"
heroku addons:create bucketeer:hobbyist
echo "Adding Cloudinary"
heroku addons:create cloudinary:starter
echo "Adding CloudAMQP"
heroku addons:create cloudamqp:tiger

echo "Adding Pusher"
heroku addons:create pusher:sandbox


echo "adding CF env"
heroku config:set CF_KEY='UPDATE_WITH_OWN_KEY'
#heroku releases --app $APPLICATION_NAME
#heroku config --app $APPLICATION_NAME
#heroku info --app $APPLICATION_NAME
#heroku restart --app $APPLICATION_NAME


#heroku kafka:topics:create `heroku config:get KAFKA_PREFIX`web-to-kafka