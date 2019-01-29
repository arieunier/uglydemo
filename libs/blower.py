import os
import requests

def sendMessage(Message, Phone):
    requests.post(os.environ['BLOWERIO_URL'] + '/messages', data={'to': Phone, 'message': Message})


#sendMessage("This is a test", "+33643395652")