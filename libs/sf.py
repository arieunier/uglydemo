import requests, ujson
from appsrc import app, logger

def sf_getProducts(sfurl, sftoken):
    query =  'SELECT id, name from product2'
    url = sfurl + '/services/data/v45.0/query/'
    attributes = {'q':query}
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1"}

    result = requests.get(url, params=attributes, headers=headers)
    data = result.json()
    ids = []
    for entry in data['records']:
        logger.debug(entry)

def sf_getGuestHost(sfurl, sftoken, guestid):
    query =  "SELECT host__r.id from guest__c where id='{}'".format(guestid)
    url = sfurl + '/services/data/v45.0/query/'
    attributes = {'q':query}
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1"}

    logger.info("url={}".format(url))
    logger.info("headers={}".format(headers))
    logger.info("attributes={}".format(attributes))

    result = requests.get(url, params=attributes, headers=headers)
    data = result.json()
    logger.info(data)
    return data['records'][0]['Host__r']['Id']

def sf_ChatterPost(sfurl, sftoken, guestid, hostid, status):
    url = sfurl + '/services/data/v45.0/chatter/feed-elements'
    
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1", "Content-Type" : "application/json"}
    attributes = {'feedElementType':'FeedItem',
    "subjectId":hostid,
    'text': 'Badge status has been updated to {}'.format(status)}
    body = { 
            "body" : {
                "messageSegments" : [
                    {
                        "type" : "Text",
                        "text" : "Your guest's badge status has been updated to {}." .format(status)
                    },
                    {   
                        "type" : "Mention",
                        "id" : hostid
                    }]
                },
            "feedElementType" : "FeedItem",
            "subjectId" : guestid
            }
    data=ujson.dumps(body)
    logger.info(data)
    result = requests.post(url, data=data , headers=headers, params=attributes)
    logger.info(result)
    

    #/services/data/v45.0/chatter/feed-elements?feedElementType=FeedItem&subjectId=a041t000003oLm4AAE&text=New+post

def startBulkV2Job(sfurl, sftoken, sfobject):

    url = sfurl + "/services/data/v48.0/jobs/ingest/"
    body = {
         "object" : sfobject,
        "contentType" : "CSV",
        "operation" : "insert"
        }

    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1", "Content-Type" : "application/json"}        
    data=ujson.dumps(body)
    logger.info("##### CREATE JOB #####")
    logger.info(data)
    logger.info(url)        
    logger.info(headers)
    result = requests.post(url, data=data , headers=headers)
    logger.info(result.json())
    return result.json()

def uploadBulkv2Data(sfurl, sftoken, jobid, data):
    url = sfurl + "/services/data/v48.0/jobs/ingest/" + jobid + "/batches/"
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1", "Content-Type" : "text/csv","Accept": "application/json"}        
    logger.info("##### UPLOAD DATA #####")
    logger.info(url)        
    logger.info(headers)
    result = requests.put(url, data=data , headers=headers)
    logger.info(result.status_code)
    logger.info(result.text)

def closeBulkV2Job(sfurl, sftoken, jobid):
    url = sfurl + "/services/data/v48.0/jobs/ingest/" + jobid
    body = {
      "state" : "UploadComplete"
        }
    data=ujson.dumps(body)
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1", "Content-Type" : "application/json", "Accept": "application/json"}            
    logger.info("##### CLOSE JOB #####")
    logger.info(url)        
    logger.info(headers)
    result = requests.patch(url, data=data , headers=headers)
    logger.info(result.status_code)
    logger.info(result.json())
    return result.json()


def sf_updateBadge(sfurl, sftoken, guest, status):
    url = sfurl + '/services/data/v45.0/sobjects/guest__c/{}?_HttpMethod=PATCH'.format(guest) 
    #attributes = {'q':query}
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1", "Content-Type" : "application/json"}

    logger.info("url={}".format(url))
    logger.info("headers={}".format(headers))
    data=ujson.dumps({"Status__c":status})
    logger.info(data)
    result = requests.post(url, data=data , headers=headers)
    logger.info(result)