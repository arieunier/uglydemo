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
SF_RECORD_NAME="bulkv2__c"
CSV_HEADER="Name,textField__c\n"



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
    bulkv2_query_id = sf.bulkv2Query_CreateJob(sfurl, session_id, "select id from bulkv2__c")['id']
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



