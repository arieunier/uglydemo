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

echo "######### Adding Redis addon"
heroku addons:create heroku-redis:premium-0 --app $APPLICATION_NAME

echo "######### Updating environment variables"
heroku config:add STAGING_DATABASE_URL=`heroku config:get DATABASE_URL --app $APPLICATION_NAME`

echo "######### Adding New relic"
heroku addons:create newrelic:hawke --app $APPLICATION_NAME
NEW_RELIC_LICENSE_KEY=`heroku config:get NEW_RELIC_LICENSE_KEY --app $APPLICATION_NAME --team arieunier-cdo`
newrelic-admin generate-config $NEW_RELIC_LICENSE_KEY newrelic.ini
heroku config:add NEW_RELIC_CONFIG_FILE='/app/newrelic.ini'  --app $APPLICATION_NAME 
heroku config:add NEW_RELIC_LOG_LEVEL=debug --app $APPLICATION_NAME 
heroku config:set NEW_RELIC_APP_NAME="$APPLICATION_NAME" --app $APPLICATION_NAME 

echo "Adding Cloudinary"
heroku addons:create cloudinary:starter --app $APPLICATION_NAME 

echo "Adding Bucketeer"
heroku addons:create bucketeer:hobbyist --app $APPLICATION_NAME
echo "Adding CloudAMQP"
heroku addons:create cloudamqp:tiger --app $APPLICATION_NAME 

echo "Adding Pusher"
heroku addons:create pusher:sandbox --app $APPLICATION_NAME

# updates: all below addons are now used by accessing variables from another application.
# they'll be attached during the app creation

echo "adding blowerio"
heroku addons:create blowerio:starter --app $APPLICATION_NAME 

echo "Creates the badge db "
heroku pg:psql -f createTables.sql

echo "adding CF env"
heroku config:set CF_KEY='UPDATE_WITH_OWN_KEY'
echo "adding other environment variables"
heroku config:set LOG_LEVEL='DEBUG'
heroku config:set KAFKA_TOPIC_READ='topicRead'
heroku config:set KAFKA_TOPIC_WRITE='topicWrite '
heroku config:set KAFKA_TOPIC_BROWSERNOTIFICATION='event_push_Notification__e'
heroku config:set KAFKA-CONSUMERGRP="my-consumer-group"
heroku config:set KAFKA_TOPIC_SMSGUEST='event_host_accept_guest__e'
heroku config:set KAFKA_TOPIC_SMSGENERIC='event_send_smss__e'
heroku config:set APP_CLIENT_ID=''
heroku config:set APP_CLIENT_SECRET=''
heroku config:set REDIRECT_URI_CODE='https://'$APPLICATION_NAME'.herokuapp.com/sfconnectedapp'
heroku config:set SF_REQUEST_TOKEN_URL='https://login.salesforce.com/services/oauth2/token'
heroku config:set SF_AUTHORIZE_TOKEN_URL='https://login.salesforce.com/services/oauth2/authorize?'

echo "Configuring Kafka"
#echo "######### Adding Heroku Kafka "
#heroku addons:create heroku-kafka:basic-2 --app connect-events-arieunier
#heroku kafka:wait  --app connect-events-arieunier
#heroku kafka:consumer-groups:create my-consumer-group --app connect-events-arieunier
#heroku kafka:topics:create topicRead --app connect-events-arieunier
#heroku kafka:topics:create topicWrite --app connect-events-arieunier

heroku addons:attach kafka-cylindrical-19303
heroku config:set APPNAME=$APPLICATION_NAME
heroku config:set CF_KEY='dfe1fc69d77842a9af25bfa7ac45caee,ba2c1b8f0a4845e080eb87268fae177d'
heroku config:set APP_CLIENT_ID='3MVG9fTLmJ60pJ5Ly8BJZfP0UwVJGodBblEuztZjVetqEGo6aPEeaB.jAf8VmHs_jQnAgvi7iYm4mxcoY72pn'
heroku config:set APP_CLIENT_SECRET='D6BDACE02D28D91D649958806AE16E06F8E71F8F8A93FE0AFA3904B604945554'
heroku config:set SECURITY_USER='Sly Resident'

heroku config:set DEMOSCENARIO=''
heroku stack:set heroku-18