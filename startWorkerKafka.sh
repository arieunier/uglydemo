#!/bin/sh
PYTHONPATH=.:./libs
export PYTHONPATH
python3 worker_kafka.py $KAFKA_TOPIC_READ