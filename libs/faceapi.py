

import cognitive_face as CF
import requests, os , random
import time
from libs import logs

logger = logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue=logs.LOG_LEVEL,
            flaskapp=None)



CF_KEYS = os.getenv('CF_KEY', '')
CF_KEYS_ARRAY = CF_KEYS.split(',')

NB_KEYS = len(CF_KEYS.split(','))
#git print("Found %s keys" % (NB_KEYS))
BASE_URL = 'https://westeurope.api.cognitive.microsoft.com/face/v1.0'  # Replace with your regional Base URL
FACE_API_URL = 'https://westeurope.api.cognitive.microsoft.com/face/v1.0/detect'

CF.Key.set(CF_KEYS.split(',')[0])
CF.BaseUrl.set(BASE_URL)

MAX_RETRIES=5

def detect(img_url):
    return CF.face.detect(img_url)

def face_http(img_url):
    key_random = random.randint(0, NB_KEYS - 1)
    #print("key array : %s " %(CF_KEYS_ARRAY))
    #print("key random : %s " % (key_random))
    key_value = CF_KEYS_ARRAY[key_random]
    headers = { 'Ocp-Apim-Subscription-Key': key_value  }
    #print("using : %s " % (key_value))
    params = {
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
    }
    currentRetry = 0
    while currentRetry < MAX_RETRIES:
        response = requests.post(FACE_API_URL, params=params, headers=headers, json={"url": img_url})
        if (response.status_code == 200):
            faces = response.json()
            return faces, response.status_code
        elif (response.status_code == 403): # quota, let's waait a little ..
            logger.warning("Quota limit , sleeping 5s and restarting..")
            currentRetry+=1
            time.sleep(5)
        else:
            logger.error("Error : returning an empty result")
            logger.error(response.json())
            currentRetry=MAX_RETRIES

    return None, 404
