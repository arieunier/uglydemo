worker-imagesanalysis: export PYTHONPATH=.:./libs; python worker_rabbitmq.py 
worker-browsernotification: export PYTHONPATH=.:./libs; python worker_kafka.py -t  $KAFKA_TOPIC_BROWSERNOTIFICATION
worker-smsguestmessage: export PYTHONPATH=.:./libs; python worker_kafka.py -t $KAFKA_TOPIC_SMSGUEST
worker-smsgenericmessage: export PYTHONPATH=.:./libs; python worker_kafka.py -t  $KAFKA_TOPIC_SMSGENERIC
release: echo "This command will be executed BEFORE starting the program"
web: cp newrelic.ini.template newrelic.ini; newrelic-admin generate-config $NEW_RELIC_LICENSE_KEY newrelic.ini; env; newrelic-admin run-program gunicorn --workers=4 run:app


