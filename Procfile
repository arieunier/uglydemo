worker-defaultkafka: export PYTHONPATH=.:./libs:./appsrc; python worker_kafka.py  -t $KAFKA_TOPIC_READ
worker-imagesanalysis: export PYTHONPATH=.:./libs:./appsrc; python worker_rabbitmq.py 
worker-browsernotification: export PYTHONPATH=.:./libs:./appsrc; python worker_kafka.py -t  $KAFKA_TOPIC_BROWSERNOTIFICATION
worker-smsguestmessage: export PYTHONPATH=.:./libs:./appsrc; python worker_kafka.py -t $KAFKA_TOPIC_SMSGUEST
worker-smsgenericmessage: export PYTHONPATH=.:./libs:./appsrc; python worker_kafka.py -t  $KAFKA_TOPIC_SMSGENERIC
release: echo "This command will be executed BEFORE starting the program newrelic-admin run-program"
web: cp newrelic.ini.template newrelic.ini; newrelic-admin generate-config $NEW_RELIC_LICENSE_KEY newrelic.ini; export PYTHONPATH=.:./libs:./appsrc; env;  gunicorn --workers=4 run:app


