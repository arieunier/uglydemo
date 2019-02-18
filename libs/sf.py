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