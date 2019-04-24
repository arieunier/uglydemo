import os
import requests

def sendMessage(Message, Phone):
    resp  = requests.post(os.environ['BLOWERIO_URL'] + '/messages', data={'to': Phone, 'message': Message})
    print(resp.status_code)
    response = resp.json()
    print(response)


#sendMessage("This is a test", "+33643395652")