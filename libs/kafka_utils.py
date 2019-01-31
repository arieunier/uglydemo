from heroku_kafka import HerokuKafkaProducer, HerokuKafkaConsumer
from kafka import  TopicPartition
from kafka.structs import OffsetAndMetadata
import os 
import uuid, ujson

from libs import logs,blower, encode, notification

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

def sendToKafka(data, topic=None):
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
    if topic==None:
        topic=KAFKA_TOPIC_WRITE
    logger.debug("about to send {} to topic {}".format(data, topic))
    producer.send(topic, data.encode())
    producer.flush()
    logger.debug("done")


def receiveFromKafka(mode, topic_override=None):

    TOPIC = KAFKA_TOPIC_READ
    if (topic_override != None):
        TOPIC = topic_override

    logger.info("Will use topic = {}".format(TOPIC))
    consumer = HerokuKafkaConsumer(
        #KAKFA_TOPIC, # Optional: You don't need to pass any topic at all
        url= KAFKA_URL, # Url string provided by heroku
        ssl_cert= KAFKA_CLIENT_CERT, # Client cert string
        ssl_key= KAFKA_CLIENT_CERT_KEY, # Client cert key string
        ssl_ca= KAFKA_TRUSTED_CERT, # Client trusted cert string
        prefix= KAFKA_PREFIX, # Prefix provided by heroku,
        auto_offset_reset="smallest",
        max_poll_records=100,
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
    
    tp = TopicPartition(KAFKA_PREFIX + TOPIC, partition)
    if (mode == "subscribe"):
        consumer.subscribe(topics=(TOPIC))
    elif (mode == "assign"):
        consumer.assign([tp])

    # display list of partition assignerd
    assignments = consumer.assignment()
    for assignment in assignments:
        logger.debug(assignment)
    
    partitions=consumer.partitions_for_topic(KAFKA_PREFIX + TOPIC)
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
            
            if ('channel' in  dictValue): # means it's coming from a Platform EVENT
                if ('host_accept_guest__e'  in dictValue['channel'].lower()): 
                    logger.info("about to send a SMS using BLOWER")
                    message = "Dear {} {} , {} {} is aware of your arrival and will be here shortly".format(
                        dictValue['data']['payload']['Guest_Firstname__c'],
                        dictValue['data']['payload']['Guest_Lastname__c'],
                        dictValue['data']['payload']['Host_Firstname__c'],
                        dictValue['data']['payload']['Host_Lastname__c'],
                    )
                    blower.sendMessage(message, dictValue['data']['payload']['Guest_Phone_Number__c'])
                elif ('send_smss__e' in dictValue['channel'].lower()):
                    logger.info("about to send a SMS using BLOWER")
                    message = dictValue['data']['payload']['message__c']
                    phone_Number = dictValue['data']['payload']['phone_Number__c'],
                    blower.sendMessage(message, phone_Number)   
                elif ('push_notification__e' in dictValue['channel'].lower()):
                    logger.info("about to send a BROWSER NOTIFICATION using PUSHER")
                    message = dictValue['data']['payload']['message__c']
                    userid = dictValue['data']['payload']['userid__c'],
                    notification.sendNotification(userid, message)

            consumer.commit()
        except Exception as e :
            import traceback
            traceback.print_exc()
            consumer.commit()

        i += 1


