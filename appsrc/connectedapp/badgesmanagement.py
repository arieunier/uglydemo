from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache, notification, kafka_utils, sf
from appsrc import app, logger
from flask import make_response
import traceback
import urllib
from uuid import uuid4
import pprint

BADGE_FILE="ConnectedApps/badgesmanagement.html"

#functions
# add

APP_CLIENT_ID = os.getenv("APP_CLIENT_ID", "ChangeMe")
APP_CLIENT_SECRET =  os.getenv("APP_CLIENT_SECRET", "ChangeMe")
SF_REQUEST_TOKEN_URL= os.getenv("SF_REQUEST_TOKEN_URL",'https://login.salesforce.com/services/oauth2/token')
SF_AUTHORIZE_TOKEN_URL= os.getenv("SF_AUTHORIZE_TOKEN_URL",'https://login.salesforce.com/services/oauth2/authorize?')
REDIRECT_URI_CODE = os.getenv("REDIRECT_URI_CODE", "http://localhost:5000/sfconnectedapp")
SF_INSTANCE_URL = ""
API_URL = '/services/data/v44.0'




@app.route('/badgesmanagement', methods=['GET', 'POST'])
def badgesmanagement():
    try:
        logger.debug(utils.get_debug_all(request))
        cookie, cookie_exists =  utils.getCookie()
        key = {'cookie' : cookie}
        tmp_dict = None
        #data_dict = None
        key_fromCanvas = {'cookie' : cookie, 'fromCanvas':True}

        tmp_dict = rediscache.__getCache(key)
        tmp_dict_fromCanvas = rediscache.__getCache(key_fromCanvas)
        if (tmp_dict != None):
            pprint.pprint(ujson.loads(tmp_dict))
        logger.debug("############")
        if (tmp_dict_fromCanvas != None):
            pprint.pprint(ujson.loads(tmp_dict_fromCanvas))

        if ( ((tmp_dict == None) or (tmp_dict == '')) and ((tmp_dict_fromCanvas == None) or (tmp_dict_fromCanvas == ''))) :
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
            return utils.returnResponse(data, 200, cookie, cookie_exists)
        else:
            if request.method == 'POST':
                struct_json =ujson.loads(tmp_dict) 
                logger.info("post detected")
                actionform = request.form['action']
                actiontype = actionform.split('.')[0]
                actionvalue = actionform.split('.')[1]
                sqlUpdate = "update public.badge set badge_status=%(status)s where id=%(id)s"
                postgres.__execRequestWithNoResult(sqlUpdate, {'status':actiontype, 'id':actionvalue})

                logger.info('actionType={}'.format(actiontype))                
                sfinstanceurl = struct_json['instance_url']
                sftoken = struct_json['access_token']
                guest_id = postgres.getBadgeById(actionvalue)['data'][0]['guest_id']
                host_id = sf.sf_getGuestHost( sfinstanceurl, sftoken, guest_id)

                if (actiontype == 'INACTIVE'):
                    sf.sf_updateBadge(sfinstanceurl, sftoken, guest_id, 'SECURITY RISK')      
                elif  (actiontype == 'ACTIVE'):
                    sf.sf_updateBadge(sfinstanceurl, sftoken, guest_id, 'BADGE ISSUED')

                sf.sf_ChatterPost(sfinstanceurl, sftoken, guest_id, host_id, actiontype)

            logger.info(tmp_dict)
            sqlRequest = "select Id, guest_firstname, guest_lastname, badge_status, creation_date from public.badge order by creation_date"
            sqlResult = postgres.__execRequest(sqlRequest, None)
            data = render_template(BADGE_FILE,
                            columns=sqlResult['columns'],
                            entries = sqlResult['data'])
            return utils.returnResponse(data, 200, cookie, cookie_exists) 


    except Exception as e :
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)

def save_created_state(state):
    # saves into redis
    rediscache.__setCache(state, "created", 3600)
        
