#Grab the latest alpine image
FROM alpine:latest

# Install python and pip
RUN apk add --no-cache --update python3 python3 python-dev py-setuptools py-yaml && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache
RUN apk add --no-cache --update postgresql-dev gcc python3-dev musl-dev openssl libffi-dev zlib zlib-dev jpeg jpeg-dev
RUN apk add --no-cache --update ffmpeg

ADD ./requirements.txt /tmp/requirements.txt

# Install dependencies
run echo "pip update"
RUN pip install --upgrade pip
run pip install -U cffi
run pip install -U pillow 

run echo "installing pip requirements"
run pip install -U  --no-cache-dir Flask gunicorn Jinja2 psycopg2  SQLAlchemy urllib3 psycopg2-binary ujson redis newrelic uuid flask-bootstrap boto3 pika cognitive_face pillow
run pip install -U --no-cache-dir -U -r /tmp/requirements.txt --upgrade 
#kafka-python
#heroku-kafka
#RUN pip install --no-cache-dir -q -r /tmp/requirements.txt

# Add our code
ADD ./ /opt/app/
WORKDIR /opt/app

# Expose is NOT supported by Heroku
# EXPOSE 5000 		

# Run the image as a non-root user
RUN adduser -D myuser
USER myuser

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku			
CMD gunicorn --bind 0.0.0.0:$PORT run:app 