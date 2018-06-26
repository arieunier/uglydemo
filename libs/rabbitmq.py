import pika, os, urllib.parse
import datetime  
import ujson 
from libs import logs, rediscache, aws, faceapi, postgres
from appsrc import logger 
import uuid
from datetime import datetime 
from libs import logs , utils


PATH_TO_TEST_IMAGES_DIR = "./images/"
CLOUDAMQP_QUEUE =  os.getenv('CLOUDAMQP_QUEUE','web-to-workers')
CLOUDAMQP_URL = os.environ.get('CLOUDAMQP_URL', '')
UPLOAD_IN_REDIS=utils.str2bool(os.getenv("UPLOAD_IN_REDIS", "false"))


connection = None
channel = None

logger = logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue=logs.LOG_LEVEL,
            flaskapp=None)


def init():
    global connection, channel, CLOUDAMQP_QUEUE
    if (connection == None or channel == None ):
        if (CLOUDAMQP_URL != ''):
            connection = pika.BlockingConnection(params) # Connect to CloudAMQP
            channel = connection.channel() # start a channel
            channel.queue_declare(queue=CLOUDAMQP_QUEUE, durable=True) # Declare a queue
            channel.basic_qos (prefetch_count=1)
            logger.debug("Initialized : isOpen={}".format(channel.is_open))


# Parse CLODUAMQP_URL (fallback to localhost)
if (CLOUDAMQP_URL != ''):
    url = urllib.parse.urlparse(CLOUDAMQP_URL)
    params = pika.ConnectionParameters(host=url.hostname, virtual_host=url.path[1:],
    credentials=pika.PlainCredentials(url.username, url.password))
    init()
    logger.info("{}  - Initialization done RabbitMq" .format(datetime.now()))


def __checkQueue():
    global channel, connection, CLOUDAMQP_QUEUE
    if (channel == None or connection == None or channel.is_open == False):
        connection = None
        channel = None
        init()


def _retrySendData(data, queue):
    global channel, CLOUDAMQP_QUEUE
    try:
        # reinit
        __checkQueue()
        channel.basic_publish(exchange='',
                                     routing_key=queue,
                                         body=data,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
        #logger.debug("[x] sent")
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(e.__str__())
        logger.error("{} - ERROR while trying to connect to RabbitMQ. Data are lost ! #FIXME #TODO - {}".format(datetime.now(), e.__str__()))



def sendMessage(data, queue):
    # send a message
    global channel
    try:
        __checkQueue()

        channel.basic_publish(exchange='',
                                     routing_key=queue,
                                         body=data,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
        logger.debug("[x] sent")
    except pika.exceptions.ConnectionClosed as e:
        try:
            logger.error("Error with Rabbit MQ Connection. Trying to reinit it")
            init()
            channel.basic_publish(exchange='',
                                     routing_key=queue,
                                         body=data,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
        except Exception as e:
            init()
            _retrySendData(data, queue)
    except Exception as e:
        init()
        _retrySendData(data, queue)

def floatToBool(dictEntry, keywords, data, alternatekeywords, threshold):
    
    datakeywords = keywords
    if (alternatekeywords != ''):
        datakeywords = alternatekeywords

    if (dictEntry[keywords] >= threshold):
            data[datakeywords] = True
    else:
            data[datakeywords] = False
    

def floatToString(dictEntry, keywords,  threshold, data, alternatekeyword, keywordsvalue):
    
    if (dictEntry[keywords] >= threshold):
        data[alternatekeyword] = keywords
        data[keywordsvalue] = dictEntry[keywords]
    #return ""
    

def stringToBool(dictEntry, keywords, data,alternatekeywords, values):
    datakeywords = keywords
    if (alternatekeywords != ''):
        datakeywords = alternatekeywords

    if (dictEntry[keywords] in values):
            data[datakeywords] = True
    else:
            data[datakeywords] = False

# create a function which is called on incoming messages
def FACE_API_CALLBACK(ch, method, properties, body):
    try:
        # transforms body into dict
        body_dict = ujson.loads(body)
        logger.info(body_dict)
        logger.info(" [x] Received id=%r" % (body_dict['id']))
        # gets the id of the image to retrieve in Redis
        image_id = body_dict['id']
        if (body_dict['UPLOAD_IN_REDIS'] == True):
            image_binary_data = rediscache.__getCache(image_id)
            # write binary data   into a file
            logger.debug("Writing file to disk")
            localfilename = '%s/%s' % (PATH_TO_TEST_IMAGES_DIR, "/rab_"  + image_id + ".jpg")
            remotefilename =image_id + ".jpg"
            file = open(localfilename, "wb")
            file.write(image_binary_data)
            file.close()
            # sends data to AWS
            logger.debug("Starting AWS Upload")
            awsFilename = aws.uploadData(localfilename, remotefilename)
            logger.debug("uploaded file to amazon : {}".format(awsFilename))
            # deletes from redis
            rediscache.__delCache(image_id)
            # deletes local file 
            os.remove(localfilename)
        else:
            awsFilename = body_dict['remote_url']
        # now detection !!
        logger.debug("Starting Face API")
        result, code  = faceapi.face_http(awsFilename)
        logger.debug("Face API Result : {}".format(result))
        if (code != 200):
            logger.error("Can't  treat entry.")
            return
        else:
            img_width = body_dict['image_width']
            img_height = body_dict["image_height"] 

            # now treats each result
            for entry in result:
                try:
        
                    personid = uuid.uuid4().__str__()
                    data = {
                            'MediaId__c' : image_id, 
                            'image__c' : awsFilename, 
                            'UserAgent__c' : body_dict['user-agent'], 
                            'URL__c' : body_dict['url'], 
                            'Name' : personid,
                            'PersonId__c' : personid ,
                            'Gender__c': entry['faceAttributes']['gender'], 
                            'Age__c' : int(entry['faceAttributes']['age']), 
                            'Smile_value__c' : entry['faceAttributes']['smile'],
                            'eyemakeup__c' : entry['faceAttributes']['makeup']['eyeMakeup'], 
                            'lipmakeup__c':entry['faceAttributes']['makeup']['lipMakeup'],
                            'Emotion_Value__c':0.000}
                    # now let's treat things in the right order ..
                    floatToBool(entry['faceAttributes'], 'smile', data,  'Smile__c', 0.5)
                    stringToBool(entry['faceAttributes'], 'glasses',data,'Glasses__c', ["ReadingGlasses"])
                    floatToBool(entry['faceAttributes']['hair'], 'bald',data, 'Bald__c', 0.5)
                    
                    # face square
                    data['ImageWidth__c'] = img_width
                    data['ImageHeight__c'] = img_height
                    data['FaceTop__c'] = int((entry['faceRectangle']['top'] / img_height)  * 100)
                    data['FaceLeft__c'] = int((entry['faceRectangle']['left'] / img_width)  * 100)
                    data['FaceWidth__c'] = int((entry['faceRectangle']['width'] / img_width)  * 100)
                    data['FaceHeight__c'] = int((entry['faceRectangle']['height'] / img_height)  * 100)

                    if (entry['faceAttributes']['hair']['bald'] > 0.49):
                        data['Hair__c'] = "bald"

                    data['Haircolor__c'] = ''
                    if ('hairColor' in entry['faceAttributes']['hair']):
                        if (len(entry['faceAttributes']['hair']['hairColor']) >= 1):
                            data['Haircolor__c'] = entry['faceAttributes']['hair']['hairColor'][0]['color']
                            data['Hair__c'] = entry['faceAttributes']['hair']['hairColor'][0]['color']
                        else:
                            data['Hair__c'] = "bald"
                    else:
                        data['Hair__c'] = "bald"
                    
                    FacialHair = "None"
                    if (entry['faceAttributes']['facialHair']['moustache'] > 0.49):
                        FacialHair = 'moustache'
                    if (entry['faceAttributes']['facialHair']['beard'] > 0.49):
                        if (FacialHair != "None"):
                            FacialHair += ' or beard'
                        else:
                            FacialHair += 'beard'
                    data['FacialHair__c'] = FacialHair

                    data['Emotion__c'] = "neutral"
                    floatToBool(entry['faceAttributes']['facialHair'], 'moustache',data, 'Moustache__c', 0.5)
                    floatToBool(entry['faceAttributes']['facialHair'], 'beard', data, 'Beard__c', 0.5)


                    floatToBool(entry['faceAttributes']['emotion'], 'anger', data, 'Anger__c', 0.01)
                    floatToBool(entry['faceAttributes']['emotion'], 'contempt', data, 'Contempt__c',0.01)
                    floatToBool(entry['faceAttributes']['emotion'], 'disgust', data,'Disgust__c', 0.01)
                    floatToBool(entry['faceAttributes']['emotion'], 'fear', data,'Fear__c', 0.01)
                    floatToBool(entry['faceAttributes']['emotion'], 'happiness', data,'Happiness__c',0.01)
                    floatToBool(entry['faceAttributes']['emotion'], 'neutral',data, 'Neutral__c', 0.01)
                    floatToBool(entry['faceAttributes']['emotion'], 'sadness',data, 'Sadness__c', 0.01)
                    floatToBool(entry['faceAttributes']['emotion'], 'surprise',data, 'Surprise__c', 0.01)


                    data['Emotion_Value__c'] = 0.0
                    data['Emotion__c'] = 'neutral'

                    floatToString(entry['faceAttributes']['emotion'], 'anger',  data['Emotion_Value__c'], data, 'Emotion__c', 'Emotion_Value__c')
                    floatToString(entry['faceAttributes']['emotion'], 'contempt',  data['Emotion_Value__c'], data, 'Emotion__c', 'Emotion_Value__c')
                    floatToString(entry['faceAttributes']['emotion'], 'disgust',  data['Emotion_Value__c'], data, 'Emotion__c', 'Emotion_Value__c')
                    floatToString(entry['faceAttributes']['emotion'], 'fear',  data['Emotion_Value__c'], data, 'Emotion__c', 'Emotion_Value__c')
                    floatToString(entry['faceAttributes']['emotion'], 'happiness',  data['Emotion_Value__c'], data, 'Emotion__c', 'Emotion_Value__c')
                    floatToString(entry['faceAttributes']['emotion'], 'neutral',  data['Emotion_Value__c'], data, 'Emotion__c', 'Emotion_Value__c')
                    floatToString(entry['faceAttributes']['emotion'], 'sadness',  data['Emotion_Value__c'], data, 'Emotion__c', 'Emotion_Value__c')
                    floatToString(entry['faceAttributes']['emotion'], 'surprise',  data['Emotion_Value__c'], data, 'Emotion__c', 'Emotion_Value__c')

                    data['Description__c'] = ujson.dumps(entry)


                    logger.debug(data)

                    postgres.__saveImageAnalysisEntry(data)
                except Exception as e:
                    import traceback
                    traceback.print_exc()                
                    logger.error("Error treating entry, going to the next")
            logger.info(" [x] Finished id=%r" % (body_dict['id']))
    except Exception as e:
        import traceback
        traceback.print_exc()


def receiveMessage(queue):
    global channel
    __checkQueue()
    # set up subscription on the queue
    channel.basic_consume(FACE_API_CALLBACK,
        queue=queue,
        no_ack=True)

    channel.start_consuming() # start consuming (blocks)

    connection.close()


init()




