import json
import os
PW_AUTH = os.environ['PUSHWOOSH_API_TOKEN']
PW_APPLICATION_CODE = os.environ['PUSHWOOSH_APPLICATION_CODE']

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.request import Request
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen
    from urllib2 import Request

def pw_call(method, data):
    url = 'https://cp.pushwoosh.com/json/1.3/' + method
    data = json.dumps({'request': data})
    req = Request(url, data.encode('UTF-8'), {'Content-Type': 'application/json'})
    try:
        f = urlopen(req)
        response = f.read()
        f.close()
        print('Pushwoosh response: ' + str(response))
    except Exception as e:
        print ('Request error: ' + str(e))

if __name__ == '__main__':
    pw_call('createMessage', {
        'auth': PW_AUTH,
        'application': PW_APPLICATION_CODE,
        'notifications': [
            {
                'send_date': 'now',
                'content': 'test',
                'data': {"custom": "json data"},
                'link': 'http://pushwoosh.com'
            }
        ]
    }
    )