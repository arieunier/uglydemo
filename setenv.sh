APPNAME='infinite-escarpment-68092'

export PYTHONPATH=.:./libs/:./appsrc/:./pyutils
export BUCKETEER_AWS_ACCESS_KEY_ID=`heroku config:get BUCKETEER_AWS_ACCESS_KEY_ID --app $APPNAME`
export BUCKETEER_AWS_REGION=`heroku config:get BUCKETEER_AWS_REGION --app $APPNAME`
export BUCKETEER_AWS_SECRET_ACCESS_KEY=`heroku config:get BUCKETEER_AWS_SECRET_ACCESS_KEY --app $APPNAME`
export BUCKETEER_BUCKET_NAME=`heroku config:get BUCKETEER_BUCKET_NAME --app $APPNAME`
export CLOUDINARY_URL=`heroku config:get CLOUDINARY_URL --app $APPNAME`
export DATABASE_URL=`heroku config:get DATABASE_URL --app $APPNAME`
export LOGDNA_KEY=`heroku config:get LOGDNA_KEY --app $APPNAME`
export NEW_RELIC_APP_NAME=`heroku config:get NEW_RELIC_APP_NAME --app $APPNAME`
export NEW_RELIC_CONFIG_FILE=`heroku config:get NEW_RELIC_CONFIG_FILE --app $APPNAME`
export NEW_RELIC_LICENSE_KEY=`heroku config:get NEW_RELIC_LICENSE_KEY --app $APPNAME`
export NEW_RELIC_LOG=`heroku config:get NEW_RELIC_LOG --app $APPNAME`
export NEW_RELIC_LOG_LEVEL=`heroku config:get NEW_RELIC_LOG_LEVEL --app $APPNAME`
export REDIS_URL=`heroku config:get REDIS_URL --app $APPNAME`
export STAGING_DATABASE_URL=`heroku config:get STAGING_DATABASE_URL --app $APPNAME`
export CLOUDAMQP_APIKEY=`heroku config:get CLOUDAMQP_APIKEY --app $APPNAME`
export CLOUDAMQP_URL=`heroku config:get CLOUDAMQP_URL --app $APPNAME`
export PUSHER_SOCKET_URL=`heroku config:get PUSHER_SOCKET_URL --app $APPNAME`
export PUSHER_URL=`heroku config:get PUSHER_URL --app $APPNAME`
#oauth flow
export APP_CLIENT_ID="3MVG9TSaZ8P6zP1oXkMT5WIwgzXQZXKdG560bpIt_.O7NGAwNDcr1b1WS_3EG7Hi9JBgSvcdcqr4E.N5gP8Yi"
export APP_CLIENT_SECRET="youcantknow"
# kafka part
export KAFKA_CLIENT_CERT=`heroku config:get KAFKA_CLIENT_CERT  --app $APPNAME`
export KAFKA_CLIENT_CERT_KEY=`heroku config:get KAFKA_CLIENT_CERT_KEY  --app $APPNAME`
export KAFKA_PREFIX=`heroku config:get KAFKA_PREFIX  --app $APPNAME`
export KAFKA_TRUSTED_CERT=`heroku config:get KAFKA_TRUSTED_CERT  --app $APPNAME`
export KAFKA_URL=`heroku config:get KAFKA_URL  --app $APPNAME`
export KAFKA_TOPIC_READ="topicRead"
export KAFKA_TOPIC_WRITE="topicWrite"
# logs
export LOG_LEVEL=debug
# blower$
export BLOWERIO_URL=`heroku config:get BLOWERIO_URL  --app $APPNAME`