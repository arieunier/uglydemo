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
    #attributes = {'feedElementType':'FeedItem',
    #"subjectId":hostid,
    #'text': 'Badge status has been updated to {}'.format(status)}
    attributes={}
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

def bulkv2Ingest_CreateJob(sfurl, sftoken, sfobject):

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

def bulkv2Ingest_InsertData(sfurl, sftoken, jobid, data):
    url = sfurl + "/services/data/v48.0/jobs/ingest/" + jobid + "/batches/"
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1", "Content-Type" : "text/csv","Accept": "application/json"}        
    logger.info("##### UPLOAD DATA #####")
    logger.info(url)        
    logger.info(headers)
    result = requests.put(url, data=data , headers=headers)
    logger.info(result.status_code)
    logger.info(result.text)

def bulkv2Ingest_CloseJob(sfurl, sftoken, jobid):
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

def bulkv2Ingest_CheckJobCompletion(sfurl, sftoken, jobid, jobtype):
    url = sfurl + "/services/data/v48.0/jobs/" + jobtype + "/" + jobid
    body = {
      "state" : "UploadComplete"
        }
    data=ujson.dumps(body)
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1", "Content-Type" : "application/json", "Accept": "application/json"}            
    logger.info("##### CHECK JOB #####")
    logger.info(url)        
    logger.info(headers)
    result = requests.get(url, data=data , headers=headers)
    logger.info(result.status_code)
    logger.info(result.json())
    return result.json()

def bulkv2Query_CreateJob(sfurl, sftoken, soqlrequest):
    url = sfurl + "/services/data/v48.0/jobs/query"
    body = {
        "operation" : "query",
        "query" : soqlrequest
        }
    data=ujson.dumps(body)
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1", "Content-Type" : "application/json", "Accept": "application/json"}            
    logger.info("##### CREATE QUERY JOB #####")
    logger.info(url)        
    logger.info(headers)
    result = requests.post(url, data=data , headers=headers)
    resultJson =result.json() 
    logger.info(resultJson)
    return resultJson

def bulkv2Query_GetResult(sfurl, sftoken, jobid, nbRecords):
    url = sfurl + "/services/data/v48.0/jobs/query/" + jobid + "/results"
    body = {
      "state" : "UploadComplete"
        }
    data=ujson.dumps(body)
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1", "Content-Type" : "application/json", "Accept": "application/json"}            
    logger.info("##### GET QUERY RESULT  #####")
    logger.info(url)        
    logger.info(headers)
    recordProcessed = 0
    params = {}
    files = []
    i = 0
    while recordProcessed < nbRecords:
        result = requests.get(url, data=data , headers=headers, params=params)
        logger.info(result.headers)
        logger.info(result.status_code)
        recordProcessed += int(result.headers['Sforce-NumberOfRecords'])
        f = open('bulkv2_' + i.__str__() + '.csv','w')
        files.append('bulkv2_' + i.__str__() + '.csv')
        f.write(result.text)
        f.close()
        i+=1
        params['locator'] = result.headers['Sforce-Locator']
        logger.info("{} / {} - loop {} ".format(recordProcessed, nbRecords, i))

    return files

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

def bulkv2Delete_CreateJob(sfurl, sftoken, sfobject):

    url = sfurl + "/services/data/v48.0/jobs/ingest/"
    body = {
         "object" : sfobject,
        "contentType" : "CSV",
        "operation" : "delete"
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

def bulkv2Delete_InsertData(sfurl, sftoken, jobid, data):
    url = sfurl + "/services/data/v48.0/jobs/ingest/" + jobid + "/batches/"
    headers = {'Authorization': "Bearer " + sftoken, "X-Prettylogger.debug": "1", "Content-Type" : "text/csv","Accept": "application/json"}        
    logger.info("##### UPLOAD DATA #####")
    logger.info(url)        
    logger.info(headers)
    result = requests.put(url, data=data , headers=headers)
    logger.info(result.status_code)
    logger.info(result.text)

def bulkv2Delete_CloseJob(sfurl, sftoken, jobid):
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
