import base64
import hashlib
import hmac

class SignedRequest:
    def __init__(self, secret, sr):
        self.secret = secret
        self.sr = sr

    #validates the signed request by verifying the key, then returns a json string
    def verifyAndDecode(self):
        #validate the consumer secret and the signed request
        if self.secret == None:
            raise Exception('Secret is null')
        if self.sr == None:
            raise Exception('Signed request is null')

        #split the request into signature and payload
        array = self.sr.split('.')
        if len(array) != 2:
            raise Exception('Signed request is formatted incorrectly')
        signature = array[0]
        payload = array[1]
        print("signature="+signature)
        print("payload="+payload)
        #verify the contents of the payload
        decodedSignature = base64.b64decode(signature)
        print("decodedSignature")
        print(decodedSignature)
        h = hmac.new(self.secret.encode(), msg=payload.encode(), digestmod=hashlib.sha256).digest()
        print("h")
        print(h)
        if decodedSignature != h:
            raise Exception('the request has been tampered with')

        #decode the base64 encoded payload
        return base64.b64decode(payload)
