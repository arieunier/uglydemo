import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache, notification, kafka_utils,sf
from appsrc import app, logger
from flask import make_response
import traceback
import urllib
from uuid import uuid4
from libs import signedrequest
import pprint 


CANVAS_FILE="ConnectedApps/main_canvas.html"
CALLBACK_FILE="ConnectedApps/callback.html"
ERROR_FILE="ConnectedApps/500.html"


@app.route('/canvas', methods=['POST', 'GET'])
def canvas_main():
    try:
        logger.debug(utils.get_debug_all(request))
        cookie, cookie_exists =  utils.getCookie()
        key = {'cookie' : cookie, 'fromCanvas':True}
        tmp_dict = None
        
        
        if ('signed_request' not in request.form):
                return utils.returnResponse("This application is only accessible through Salesforce Canvas App technology. Please access it through Salesforce", 200, cookie, cookie_exists)
        consumer_secret =  os.getenv("APP_CLIENT_SECRET", "ChangeMe")
        signed_request = request.form['signed_request']
        sr = signedrequest.SignedRequest(consumer_secret, signed_request)
        request_json = sr.verifyAndDecode()
        struct_json =ujson.loads(request_json) 
            
        rediscache.__setCache(key, ujson.dumps(struct_json), 180)
                     
        # test for chatter api
        #sf_getProducts(struct_json['client']['instanceUrl'] , struct_json['client']['oauthToken'])

        pprint.pprint(struct_json)            
        if ('record' in struct_json['context']['environment']['parameters']):    
            sqlRequest = "select Id, guest_id, guest_firstname, guest_lastname, badge_status, creation_date from public.badge where guest_id = %(guest_id)s order by creation_date"
            sqlResult = postgres.__execRequest(sqlRequest, {'guest_id':struct_json['context']['environment']['parameters']['record']})
        else:
            sqlRequest = "select Id, guest_id,guest_firstname, guest_lastname, badge_status, creation_date from public.badge order by creation_date"
            sqlResult = postgres.__execRequest(sqlRequest, {})
        data = render_template(CANVAS_FILE, request_json=ujson.dumps(struct_json), columns=sqlResult['columns'],
                            entries = sqlResult['data'])

        #return render_template()
        return utils.returnResponse(data, 200, cookie, cookie_exists) 
    except Exception as e :
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An Error Occured, please check LogDNA", 200, cookie, cookie_exists)

@app.route('/callback')
def callback():
    return render_template(CALLBACK_FILE)

@app.errorhandler(500)
def serverError(e):
    return render_template(ERROR_FILE), 500

# should only be allowed within the canvas app
@app.route('/singleguestbadgemanagement', methods=['GET', 'POST'])
def singleguestbadgemanagement():
    try:
        logger.debug(utils.get_debug_all(request))
        cookie, cookie_exists =  utils.getCookie()
        #data_dict = None
        key_fromCanvas = {'cookie' : cookie, 'fromCanvas':True}
        logger.info(key_fromCanvas)
        tmp_dict_fromCanvas = rediscache.__getCache(key_fromCanvas)

        if ((tmp_dict_fromCanvas == None) or (tmp_dict_fromCanvas == '')) :
            logger.info("Data not found in cache")
            logger.debug(utils.get_debug_all(request))
            text = 'User is not coming from canvas app !'
            return utils.returnResponse(text, 200, cookie, cookie_exists)
        else:
            struct_json =ujson.loads(tmp_dict_fromCanvas) 
            guest_id = request.args['guest_id']

            # gest the record id


            if request.method == 'POST':
                logger.info("post detected")
                actionform = request.form['action']
                actiontype = actionform.split('.')[0]
                actionvalue = actionform.split('.')[1]
                sqlUpdate = "update public.badge set badge_status=%(status)s where id=%(id)s"
                postgres.__execRequestWithNoResult(sqlUpdate, {'status':actiontype, 'id':actionvalue})

        
                # now updates the guest status
                # sf_getProducts(struct_json['client']['instanceUrl'] , struct_json['client']['oauthToken'])
                #def sf_updateBadge(sfurl, sftoken, guest, status)
                logger.info('actionType={}'.format(actiontype))
                sfinstanceurl = struct_json['client']['instanceUrl']
                sftoken =  struct_json['client']['oauthToken']
                host_id = sf.sf_getGuestHost( sfinstanceurl, sftoken, guest_id)

                if (actiontype == 'INACTIVE'):
                    sf.sf_updateBadge(sfinstanceurl, sftoken, guest_id, 'SECURITY RISK')      
                elif  (actiontype == 'ACTIVE'):
                    sf.sf_updateBadge(sfinstanceurl, sftoken, guest_id, 'BADGE ISSUED')

                sf.sf_ChatterPost(sfinstanceurl, sftoken, guest_id, host_id, actiontype)

            sqlRequest = "select Id, guest_id, guest_firstname, guest_lastname, badge_status, creation_date from public.badge where guest_id = %(guest_id)s order by creation_date"
            sqlResult = postgres.__execRequest(sqlRequest, {'guest_id':guest_id})
            data = render_template(CANVAS_FILE, request_json=ujson.dumps(struct_json), columns=sqlResult['columns'],
                            entries = sqlResult['data'])
            return utils.returnResponse(data, 200, cookie, cookie_exists) 


    except Exception as e :
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)


