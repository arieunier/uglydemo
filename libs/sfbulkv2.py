import uuid
import requests
import ujson 
from libs import sf
from simple_salesforce import Salesforce, SalesforceLogin


username=""
password=""
security_token=""

SF_RECORD_NAME="bulkv2__c"
CSV_HEADER="Name,textField__c\n"


session_id, instance = SalesforceLogin(
    username=username,
    password=password,
    security_token=security_token
    )
sfurl = "https://" + instance

bulkv2_batch = sf.startBulkV2Job(sfurl,session_id, SF_RECORD_NAME)
bulkid = bulkv2_batch['id']
data = CSV_HEADER
for i in range (0, 100, 1):
    unique_name=uuid.uuid4().__str__()
    data += unique_name + ",text field content " + i.__str__() + "\n"
sf.uploadBulkv2Data(sfurl, session_id, bulkid, data)
sf.closeBulkV2Job(sfurl, session_id, bulkid)
