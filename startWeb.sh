#!/bin/sh
cp newrelic.ini.template newrelic.ini
newrelic-admin generate-config $NEW_RELIC_LICENSE_KEY newrelic.ini
env
newrelic-admin run-program gunicorn --workers=4 run:app