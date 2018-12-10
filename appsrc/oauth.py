from flask import request, abort 
import urllib
from flask import Flask
from appsrc import app, logger
from libs import  utils, rediscache
from uuid import uuid4
import urllib
import requests
import ujson, os

APP_CLIENT_ID = os.getenv("APP_CLIENT_ID")
APP_CLIENT_SECRET =  os.getenv("APP_CLIENT_SECRET")
SF_REQUEST_TOKEN_URL='https://login.salesforce.com/services/oauth2/token'
SF_AUTHORIZE_TOKEN_URL='https://login.salesforce.com/services/oauth2/authorize?'
REDIRECT_URI_CODE = "http://localhost:5000/sfconnectedapp"
SF_INSTANCE_URL = ""
API_URL = '/services/data/v44.0'
##app = Flask(__name__)




@app.route('/sfconnectedapp')
def sfconnectedapp():
    logger.error(utils.get_debug_all(request))
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    print(code)

    data =   {'client_id':APP_CLIENT_ID,
              'client_secret':APP_CLIENT_SECRET,
              "redirect_uri": REDIRECT_URI_CODE,
              "code":code,
              'grant_type':'authorization_code'}
    headers = {
                'content-type': 'application/x-www-form-urlencoded'
            }
    req = requests.post(SF_REQUEST_TOKEN_URL,data=data,headers=headers)
    response = req.json()
    logger.error(response)

    #result = requests.post(url=url, data=data)
    access_token = response['access_token']
    instance_url = response['instance_url']

    url = instance_url + API_URL
    headers = {'Authorization' : "Bearer " + access_token, "X-Prettylogger.debug":"1" }
    result = requests.get(url, headers=headers)
    logger.info("Result Code : {}".format(result.status_code))
    logger.info("Header : {}".format(result.headers))
    logger.info("Content : {}".format(result.json()))

    #now stores everything in redis
    rediscache.__delCache(state)
    cookie, cookie_exists =  utils.getCookie()
    key = {'cookie' : cookie}
    rediscache.__setCache(key, ujson.dumps(response), 3600)


    return "got a code! %s" % response 


@app.route('/oauth')
def homepage():
    cookie, cookie_exists =  utils.getCookie()
    logger.debug(utils.get_debug_all(request))

    key = {'cookie' : cookie}
    tmp_dict = None
    #data_dict = None
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")
            logger.debug(utils.get_debug_all(request))
            text = 'User is not authenticated, please log in ! <a href="%s">Authenticate with Salesforce</a>'
                    
            state = str(uuid4())
            save_created_state(state)
            params = {"client_id": APP_CLIENT_ID,
                    "response_type": "code",
                    "state": state,
                    "redirect_uri": REDIRECT_URI_CODE,
                    "scope": "full refresh_token"}

            url = SF_AUTHORIZE_TOKEN_URL + urllib.parse.urlencode(params)
            logger.info(url)
            data = text % url
    else:
        data = tmp_dict
    

    return utils.returnResponse(data, 200, cookie, cookie_exists)





def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    from uuid import uuid4
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": APP_CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": REDIRECT_URI_CODE,
              "scope": "full refresh_token"}
    import urllib
    url = SF_AUTHORIZE_TOKEN_URL + urllib.parse.urlencode(params)
    logger.error(url)
    return url

def save_created_state(state):
    # saves into redis
    rediscache.__setCache(state, "created", 3600)

def is_valid_state(state):
    val = rediscache.__getCache(state)
    logger.info(val)
    return  val != None and val != '' and val == b'created'


#if __name__ == '__main__':
#    app.run(debug=True, port=65010)