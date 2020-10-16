import uuid
import requests
import ujson 
from libs import sf
from simple_salesforce import Salesforce, SalesforceLogin
import time


"""
how to use
#init
sfbulkv2.initSFconnection(username, password, security_token)
#insert data
sfbulkv2.Bulkv2_INSERT(100000)
#query all
files = sfbulkv2.Bulkv2_QUERY()
# now deletes everything
sfbulkv2.Bulkv2_delete(files)
"""
session_id = ''
instance = ''
sfurl = ''
SF_RECORD_NAME="Account"
CSV_HEADER="Name,textField__c\n"


import jwt
import requests
import datetime
from simple_salesforce.exceptions import SalesforceAuthenticationFailed

def jwt_login(consumer_id, username, private_key, sandbox=False):
    global session_id, instance, sfurl

    endpoint = 'https://test.salesforce.com' if sandbox is True else 'https://login.salesforce.com'
    jwt_payload = jwt.encode(
        { 
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30),
            'iss': consumer_id,
            'aud': endpoint,
            'sub': username
        },
        private_key,
        algorithm='RS256'
    )

    result = requests.post(
        endpoint + '/services/oauth2/token',
        data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': jwt_payload
        }
    )
    body = result.json()
    print(body)
    
    if result.status_code != 200:
        raise SalesforceAuthenticationFailed(body['error'], body['error_description'])
    # now set things properly
    session_id = body['access_token']
    instance = body['instance_url']
    sfurl = instance
    
    sf = Salesforce(instance_url=body['instance_url'], session_id=body['access_token'])
    return sf

def initSFconnection(username, password, security_token):
    global session_id, instance, sfurl

    session_id, instance = SalesforceLogin(
    username=username,
    password=password,
    security_token=security_token
    )
    
    sfurl = "https://" + instance
    print(session_id)
    print(instance)
    print(sf)

def Bulkv2_CheckJobCompletion(jobId, jobType):
    # now waits for the job to finish
    isFinished = False
    while (isFinished == False):
        result = sf.bulkv2Ingest_CheckJobCompletion(sfurl, session_id, jobId, jobType)
        if (result['state'] == 'JobComplete'):
            print("Job is complete, stopping")
            isFinished = True
        else:
            print("Job is not complete, sleeping for 10s and trying again")
            time.sleep(10)
    if (jobType == 'query'):
        return result['numberRecordsProcessed']
    return ""

def Bulkv2_INSERT(nbRecords):
    bulkv2_batch = sf.bulkv2Ingest_CreateJob(sfurl,session_id, SF_RECORD_NAME)
    bulkid = bulkv2_batch['id']
    data = CSV_HEADER
    for i in range (0, nbRecords, 1):
        unique_name=uuid.uuid4().__str__()
        data += unique_name + ",text field content " + i.__str__() + "\n"
    sf.bulkv2Ingest_InsertData(sfurl, session_id, bulkid, data)
    sf.bulkv2Ingest_CloseJob(sfurl, session_id, bulkid)
    Bulkv2_CheckJobCompletion(bulkid, "ingest")

def Bulkv2_QUERY():
    # now gets everything
    bulkv2_query_id = sf.bulkv2Query_CreateJob(sfurl, session_id, "select id from account")['id']
    nbRecordProcessed = Bulkv2_CheckJobCompletion(bulkv2_query_id, "query")
    return sf.bulkv2Query_GetResult(sfurl, session_id, bulkv2_query_id, nbRecordProcessed)

def Bulkv2_delete(CSVFiles):
    for CSVFile in CSVFiles:
        bulkv2_batch = sf.bulkv2Delete_CreateJob(sfurl,session_id, SF_RECORD_NAME)
        bulkid = bulkv2_batch['id']
        freader = open(CSVFile, 'r')
        data = freader.read()
        freader.close()
        sf.bulkv2Delete_InsertData(sfurl, session_id, bulkid, data)
        sf.bulkv2Delete_CloseJob(sfurl, session_id, bulkid)



