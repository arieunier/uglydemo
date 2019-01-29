from libs import kafka_utils
import ujson

kafka_utils.KAFKA_TOPIC_WRITE='topicWrite'

for i in range(30):
    data = {'key' : i, 'value' : 'value of ' + str(i)}
    print(data)
    kafka_utils.sendToKafka(ujson.dumps(data))