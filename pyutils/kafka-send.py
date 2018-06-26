"""
from libs import kafka_utils
import ujson 

def dict_to_binary(the_dict):
    str = ujson.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary


i=0
while i < 1:
    dataStr =  {"Data" : "Content " + str(i)}
    print(dataStr)
    dataJson = ujson.dumps(dataStr)
    print(dataJson.encode("UTF-8"))

    kafka_utils.sendToKafka(dataJson.encode("UTF-8"))
    i+=1
    print(i)
"""

from kafka import KafkaProducer,KafkaConsumer
from kafka.errors import KafkaError
#Consumer, KafkaError, Producer
from libs import kafka_utils
import ujson 
import datetime


def producer():
    producer = KafkaProducer(
            bootstrap_servers =kafka_utils.KAFKA_URL.replace('kafka+ssl://','').split(','),
            security_protocol ='SSL',
            ssl_check_hostname=False,
            ssl_cafile ='static/kafka_ca',
            ssl_certfile ='static/kafka_client_cert',
            ssl_keyfile= 'static/kafka_client_key'

            )

    try:
        for i in range(30):
            currentDate = datetime.datetime.now()

            dataStr =  {"Data" : "Content " + currentDate.__str__() + " - " + str(i)}
            print(dataStr)
            dataJson = ujson.dumps(dataStr)
            print(dataJson.encode("UTF-8"))
            producer.send(kafka_utils.KAFKA_COMPLETE_TOPIC, dataJson.encode("UTF-8"))
            producer.flush()


    except KeyboardInterrupt:
        pass

    producer.flush(30)
    
producer()

