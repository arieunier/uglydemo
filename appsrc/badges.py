from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache, notification, kafka_utils
from appsrc import app, logger
from flask import make_response
import traceback
import urllib
from uuid import uuid4

# badge content
# uid 
# guest id
# guest name
# guest firstname
# guest company
# host firstname
# host lastname
# status
# badge image url

BADGE_FILE="badgesmanagement.html"

#functions
# add

APP_CLIENT_ID = os.getenv("APP_CLIENT_ID", "ChangeMe")
APP_CLIENT_SECRET =  os.getenv("APP_CLIENT_SECRET", "ChangeMe")
SF_REQUEST_TOKEN_URL= os.getenv("SF_REQUEST_TOKEN_URL",'https://login.salesforce.com/services/oauth2/token')
SF_AUTHORIZE_TOKEN_URL= os.getenv("SF_AUTHORIZE_TOKEN_URL",'https://login.salesforce.com/services/oauth2/authorize?')
REDIRECT_URI_CODE = os.getenv("REDIRECT_URI_CODE", "http://localhost:5000/sfconnectedapp")
SF_INSTANCE_URL = ""
API_URL = '/services/data/v44.0'



@app.route("/initBadges", methods=['GET'])
def initBadges():
    try:

        # sqlRequestDrop = "drop table public.badge";
        #postgres.__execRequestWithNoResult(sqlRequestDrop)
        sqlRequestCreate = """
        create table public.badge(id varchar(255) not null primary key, guest_id varchar(255) not null, guest_firstname varchar(255) not null, guest_lastname varchar(255) not null,
        guest_company varchar(255), host_firstname varchar(255) not null, host_lastname varchar(255) not null, badge_status varchar(255), badge_url varchar(255), creation_date timestamp not null)

        """
        
        postgres.__execRequestWithNoResult(sqlRequestCreate)
        return "{'Result':'Ok'}"
    except Exception as e :
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 403, cookie, cookie_exists) 


@app.route('/badgesmanagement', methods=['GET', 'POST'])
def badgesmanagement():
    try:
        logger.debug(utils.get_debug_all(request))
        cookie, cookie_exists =  utils.getCookie()
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
            return utils.returnResponse(data, 200, cookie, cookie_exists)
        else:
            if request.method == 'POST':
                logger.info("post detected")
                actionform = request.form['action']
                actiontype = actionform.split('.')[0]
                actionvalue = actionform.split('.')[1]
                sqlUpdate = "update public.badge set badge_status=%(status)s where id=%(id)s"
                postgres.__execRequestWithNoResult(sqlUpdate, {'status':actiontype, 'id':actionvalue})
            
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
        

@app.route('/badges', methods=['POST', 'GET'])
def badges():
    try:
        if (request.method =='POST'):
            logger.error(utils.get_debug_all(request))
            # gets all the data required to save the badge object
            guest_id = request.args.get('guest_id')
            guest_firstname = request.args.get('guest_firstname')
            guest_lastname = request.args.get('guest_lastname')
            guest_company = request.args.get('guest_company')
            host_firstname = request.args.get('host_firstname')
            host_lastname = request.args.get('host_lastname')
            # id is auto generated
            uid = uuid.uuid4().__str__()
            badge_status = 'ACTIVE'
            badge_url = "FIXME"
            # status is set to default -> INACTIVE (status are inactive / active )
            # url will be calculated
            
            # gets new city
        
            if (guest_id == '' or guest_id == None):
                return utils.returnResponse("Please provide a guest_id", 403, None, None) 
            # check if siren__c exits
 
            postgres.__insertBadge(uid, guest_id, guest_firstname, guest_lastname, guest_company, host_firstname, host_lastname, badge_status, badge_url)

            return "{'Result':'Ok'}"
        elif (request.method == 'GET'):
            logger.error(utils.get_debug_all(request))
            cookie, cookie_exists =  utils.getCookie()
            sqlRequest = sqlRequest = "select * from public.badge"
            attributes = None
            if ('badge_id' in request.args):
                sqlRequest += " where id = %(badge_id)s"
                attributes = {"badge_id": request.args.get('badge_id')}
            data = postgres.__execRequest(sqlRequest, attributes)
            return utils.returnResponse(ujson.dumps(data), 200, cookie, cookie_exists) 

    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 403, cookie, cookie_exists) 

# with user identity management

# revoke

