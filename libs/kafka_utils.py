from heroku_kafka import HerokuKafkaProducer, HerokuKafkaConsumer
from kafka import  TopicPartition
from kafka.structs import OffsetAndMetadata
from libs import postgres
import os 
import uuid, ujson

from libs import logs

logger = logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue=logs.LOG_LEVEL,
            flaskapp=None)



KAFKA_URL=  os.getenv('KAFKA_URL','')
KAFKA_CLIENT_CERT=  os.getenv('KAFKA_CLIENT_CERT','')
file = open('static/kafka_client_cert', "w")
data = file.write(KAFKA_CLIENT_CERT)
file.close()


KAFKA_CLIENT_CERT_KEY=  os.getenv('KAFKA_CLIENT_CERT_KEY','')
file = open('static/kafka_client_key', "w")
data = file.write(KAFKA_CLIENT_CERT_KEY)
file.close()


KAFKA_TRUSTED_CERT=  os.getenv('KAFKA_TRUSTED_CERT','')
file = open('static/kafka_ca', "w")
data = file.write(KAFKA_TRUSTED_CERT)
file.close()

KAFKA_PREFIX=  os.getenv('KAFKA_PREFIX')
KAFKA_TOPIC_READ= os.getenv('KAFKA_TOPIC_READ', "topicRead") #"salesforce.syncaccount__e"
KAFKA_TOPIC_WRITE= os.getenv('KAFKA_TOPIC_WRITE', "topicWrite") #"ple2"

KAFKA_GROUP_ID=os.getenv('KAFKA_CONSUMERGRP', KAFKA_PREFIX + 'my-consumer-group')




logger.debug("KAFKA_PREFIX="+KAFKA_PREFIX)
logger.debug("KAKFA_TOPIC_READ="+KAFKA_TOPIC_READ)
logger.debug("KAKFA_TOPIC_WRITE="+KAFKA_TOPIC_WRITE)
logger.debug("KAFKA_GROUP_ID="+KAFKA_GROUP_ID)

"""
    All the variable names here match the heroku env variable names.
    Just pass the env values straight in and it will work.
"""

def testKafkaHelperSND():
    import kafka_helper
    producer = kafka_helper.get_kafka_producer()
    producer.send('ple2', key='my key', value={'k': 'v'})

def testKafkaHelperRCV():
    import kafka_helper
    consumer = kafka_helper.get_kafka_consumer(topic='ple2')
    for message in consumer:
        logger.debug(message)

def sendToKafka(data):
    producer = HerokuKafkaProducer(
        url= KAFKA_URL, # Url string provided by heroku
        ssl_cert= KAFKA_CLIENT_CERT, # Client cert string
        ssl_key= KAFKA_CLIENT_CERT_KEY, # Client cert key string
        ssl_ca= KAFKA_TRUSTED_CERT, # Client trusted cert string
        prefix= KAFKA_PREFIX# Prefix provided by heroku,       
        #,partitioner="0"
    )
    """
    The .send method will automatically prefix your topic with the KAFKA_PREFIX
    NOTE: If the message doesn't seem to be sending try `producer.flush()` to force send.
    """
    logger.debug("about to send {} to topic {}".format(data, KAFKA_TOPIC_WRITE))
    producer.send(KAFKA_TOPIC_WRITE, data.encode())
    producer.flush()
    logger.debug("done")


def receiveFromKafka(mode):

    consumer = HerokuKafkaConsumer(
        #KAKFA_TOPIC, # Optional: You don't need to pass any topic at all
        url= KAFKA_URL, # Url string provided by heroku
        ssl_cert= KAFKA_CLIENT_CERT, # Client cert string
        ssl_key= KAFKA_CLIENT_CERT_KEY, # Client cert key string
        ssl_ca= KAFKA_TRUSTED_CERT, # Client trusted cert string
        prefix= KAFKA_PREFIX, # Prefix provided by heroku,
        auto_offset_reset="smallest",
        max_poll_records=10,
        enable_auto_commit=True,
        auto_commit_interval_ms=100,
        group_id=KAFKA_GROUP_ID,
        api_version = (0,9)
    )

    """
    To subscribe to topic(s) after creating a consumer pass in a list of topics without the
    KAFKA_PREFIX.
    """
    partition=1
    
    tp = TopicPartition(KAFKA_PREFIX + KAFKA_TOPIC_READ, partition)
    if (mode == "subscribe"):
        consumer.subscribe(topics=(KAFKA_TOPIC_READ))
    elif (mode == "assign"):
        consumer.assign([tp])

    # display list of partition assignerd
    assignments = consumer.assignment()
    for assignment in assignments:
        logger.debug(assignment)
    
    partitions=consumer.partitions_for_topic(KAFKA_PREFIX + KAFKA_TOPIC_READ)
    if (partitions):
        for partition in partitions:
            logger.debug("Partition="+str(partition))
    
    
    topics=consumer.topics()
    if (topics):
        for topic in topics:
            logger.debug("Topic:"+topic)
    #exit(1)
    logger.debug('waiting ..')
    """
    .assign requires a full topic name with prefix
    """
    

    """
    Listening to events it is exactly the same as in kafka_python.
    Read the documention linked below for more info!
    """
    i=0
    for message in consumer:
        try:
            logger.debug ("%i %s:%d:%d: key=%s value=%s" % (i, message.topic, message.partition,
                                              message.offset, message.key,
                                              message.value))

            dictValue = ujson.loads(message.value)
            logger.debug(dictValue)
            
            consumer.commit()
        except Exception as e :
            import traceback
            traceback.print_exc()
            #consumer.commit()

        i += 1


#receiveFromKafka("subscribe")
#import ujson
#data = ujson.dumps({'key':'value'})
#print(data)
#sendToKafka_HardCoded(data)
#testKafkaHelperRCV()