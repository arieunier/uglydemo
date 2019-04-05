from libs import rabbitmq
import datetime , ujson 
import uuid
for i in range(1):
        currentDate = datetime.datetime.now()
        dataStr =  {"id" : uuid.uuid4().__str__(), 
        "Data" : "Content " + currentDate.__str__() + " - " + str(i),
        "UPLOAD_IN_REDIS" : False}
        dataStr = {'id': '876327f6-35a1-43e6-8d46-3dcadab623f7', 
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1', 
        'url': 'https://yourdemo.herokuapp.com/', 'image_width': 2320, 'image_height': 3088, 'cookie': 'f482e8e3-9b64-46b7-9cab-e4fc33ca5f17', 'UPLOAD_IN_REDIS': False, 'remote_url': 'https://bucketeer-ad74aded-29ae-4300-ac4a-2ed34f120de3.s3.eu-west-1.amazonaws.com/public/876327f6-35a1-43e6-8d46-3dcadab623f7.jpg'}
        dataJson = ujson.dumps(dataStr)
        rabbitmq.sendMessage(dataJson, "wtf")


