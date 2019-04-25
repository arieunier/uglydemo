import os
import requests

def sendMessage(Message, Phone):
    #resp  = requests.post(os.environ['BLOWERIO_URL'] + '/messages', data={'to': Phone, 'message': Message})
    #response = resp.json()
    #print(resp.status_code)
    #print(response)
    hugue_url = "http://smssenddemo-knmf.us-e2.cloudhub.io/smssend"
    resp  = requests.post(hugue_url, data={'numgsm': Phone, 'message': Message})
    response = resp.json()
    print(resp.status_code)
    print(response)
    

sendMessage("This is a test", "+33643395652")