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
heroku config:add STAGING_DATABASE_URL=`heroku config:get DATABASE_URL --app $APPLICATION_NAME` --app $APPLICATION_NAME

echo "######### Adding New relic"
heroku addons:create newrelic:hawke --app $APPLICATION_NAME
NEW_RELIC_LICENSE_KEY=`heroku config:get NEW_RELIC_LICENSE_KEY --app $APPLICATION_NAME`
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
heroku pg:psql -f createTables.sql --app $APPLICATION_NAME

echo "adding CF env"
heroku config:set CF_KEY='UPDATE_WITH_OWN_KEY' --app $APPLICATION_NAME
echo "adding other environment variables"
heroku config:set LOG_LEVEL='DEBUG' --app $APPLICATION_NAME
heroku config:set KAFKA_TOPIC_READ='topicRead' --app $APPLICATION_NAME
heroku config:set KAFKA_TOPIC_WRITE='topicWrite ' --app $APPLICATION_NAME
heroku config:set KAFKA_TOPIC_BROWSERNOTIFICATION='salesforce.push_notification__e' --app $APPLICATION_NAME
heroku config:set KAFKA-CONSUMERGRP="my-consumer-group" --app $APPLICATION_NAME
heroku config:set KAFKA_TOPIC_SMSGUEST='salesforce.host_accept_guest__e' --app $APPLICATION_NAME
heroku config:set KAFKA_TOPIC_SMSGENERIC='salesforce.send_smss__e' --app $APPLICATION_NAME
heroku config:set APP_CLIENT_ID='' --app $APPLICATION_NAME
heroku config:set APP_CLIENT_SECRET='' --app $APPLICATION_NAME
heroku config:set REDIRECT_URI_CODE='https://'$APPLICATION_NAME'.herokuapp.com/sfconnectedapp' --app $APPLICATION_NAME
heroku config:set SF_REQUEST_TOKEN_URL='https://login.salesforce.com/services/oauth2/token' --app $APPLICATION_NAME
heroku config:set SF_AUTHORIZE_TOKEN_URL='https://login.salesforce.com/services/oauth2/authorize?' --app $APPLICATION_NAME

echo "Configuring Kafka"
#echo "######### Adding Heroku Kafka "
#heroku addons:create heroku-kafka:basic-2 --app connect-events-arieunier
#heroku kafka:wait  --app connect-events-arieunier
#heroku kafka:consumer-groups:create my-consumer-group --app connect-events-arieunier
#heroku kafka:topics:create topicRead --app connect-events-arieunier
#heroku kafka:topics:create topicWrite --app connect-events-arieunier

#heroku addons:attach kafka-cylindrical-19303
heroku addons:attach kafka-trapezoidal-94989 --app $APPLICATION_NAME
heroku config:set APPNAME=$APPLICATION_NAME --app $APPLICATION_NAME
heroku config:set CF_KEY='dfe1fc69d77842a9af25bfa7ac45caee,ba2c1b8f0a4845e080eb87268fae177d' --app $APPLICATION_NAME


#heroku config:set APP_CLIENT_SECRET='D6BDACE02D28D91D649958806AE16E06F8E71F8F8A93FE0AFA3904B604945554' --app $APPLICATION_NAME
#heroku config:set APP_CLIENT_ID='3MVG9fTLmJ60pJ5Ly8BJZfP0UwVJGodBblEuztZjVetqEGo6aPEeaB.jAf8VmHs_jQnAgvi7iYm4mxcoY72pn' --app $APPLICATION_NAME
# For schneider
heroku config:set APP_CLIENT_ID='3MVG91BJr_0ZDQ4tlpqUmI7PTwD1uhuHlY3oLCCi6vZMxjoovmfJCwghkTrR0c5zwNL329kcfB1HFj2lYrsXh' --app $APPLICATION_NAME
heroku config:set APP_CLIENT_SECRET='FA97AC7D521EA087E61208BC575B2D619EAE53468E272C3324C1B877197661D7' --app $APPLICATION_NAME

heroku config:set SECURITY_USER='Sly Resident' --app $APPLICATION_NAME

#heroku config:set DEMOSCENARIO='Wall'

