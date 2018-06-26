from libs import rabbitmq
import datetime , ujson 
for i in range(30):
        currentDate = datetime.datetime.now()
        dataStr =  {"Data" : "Content " + currentDate.__str__() + " - " + str(i)}
        dataJson = ujson.dumps(dataStr)
        rabbitmq.sendMessage(dataJson,  rabbitmq.CLOUDAMQP_QUEUE)