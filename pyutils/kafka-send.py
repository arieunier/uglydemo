from libs import kafka_utils
import ujson

kafka_utils.KAFKA_TOPIC_WRITE='topicRead'

for i in range(30):
    data = {'message' : 'value of ' + str(i)}
    print(data)
    kafka_utils.sendToKafka(ujson.dumps(data))