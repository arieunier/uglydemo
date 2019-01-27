worker-rabbitmq: export PYTHONPATH=.:./libs; python worker_rabbitmq.py 
worker-kafka: export PYTHONPATH=.:./libs; python worker_kafka.py 
release: echo "This command will be executed BEFORE starting the program"
web: cp newrelic.ini.template newrelic.ini; newrelic-admin generate-config $NEW_RELIC_LICENSE_KEY newrelic.ini; env; newrelic-admin run-program gunicorn --workers=4 run:app