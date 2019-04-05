from libs import rabbitmq
import datetime , ujson 
import uuid
for i in range(30):
        currentDate = datetime.datetime.now()
        dataStr =  {"id" : uuid.uuid4().__str__(), 
        "Data" : "Content " + currentDate.__str__() + " - " + str(i),
        "UPLOAD_IN_REDIS" : False}
        dataJson = ujson.dumps(dataStr)
        rabbitmq.sendMessage(dataJson,  "WTF")