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

echo "Adding Cloudinary"
heroku addons:create cloudinary:starter

echo "Adding Bucketeer"
heroku addons:create bucketeer:hobbyist
echo "Adding CloudAMQP"
heroku addons:create cloudamqp:tiger

echo "Adding Pusher"
heroku addons:create pusher:sandbox

# updates: all below addons are now used by accessing variables from another application.
# they'll be attached during the app creation

echo "Attaching Buckeeter addon from another application"

echo "adding blowerio"
heroku addons:create blowerio:starter


echo "adding CF env"
heroku config:set CF_KEY='UPDATE_WITH_OWN_KEY'
echo "adding other environment variables"
heroku config:set CF_KEY='LOG_LEVEL=DEBUG'
heroku config:set CF_KEY='KAFKA_TOPIC_READ=topicRead'
heroku config:set CF_KEY='KAFKA_TOPIC_WRITE=topicWrite '
heroku config:set CF_KEY='KAFKA_TOPIC_BROWSERNOTIFICATION=salesforce.push_notification__e'
heroku config:set CF_KEY='KAFKA_TOPIC_SMSGUEST=salesforce.host_accept_guest__e'
heroku config:set CF_KEY='KAFKA_TOPIC_SMSGENERIC=salesforce.send_smss__e'
heroku config:set CF_KEY='APP_CLIENT_ID='
heroku config:set CF_KEY='APP_CLIENT_SECRET='
heroku config:set CF_KEY='REDIRECT_URI_CODE=https://yourdemo.herokuapp.com/sfconnectedapp'
heroku config:set CF_KEY='SF_REQUEST_TOKEN_URL=https://login.salesforce.com/services/oauth2/token'
heroku config:set CF_KEY='SF_AUTHORIZE_TOKEN_URL=https://login.salesforce.com/services/oauth2/authorize?'
#heroku releases --app $APPLICATION_NAME
#heroku config --app $APPLICATION_NAME
#heroku info --app $APPLICATION_NAME
#heroku restart --app $APPLICATION_NAME
#heroku kafka:topics:create `heroku config:get KAFKA_PREFIX`web-to-kafka