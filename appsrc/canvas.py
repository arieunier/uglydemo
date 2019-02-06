import os
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
from libs import signedrequest



@app.route('/canvas', methods=['POST', 'GET'])
def canvas_main():
    try:
        logger.debug(utils.get_debug_all(request))
        cookie, cookie_exists =  utils.getCookie()
        key = {'cookie' : cookie}
        tmp_dict = None
        #data_dict = None
        
        tmp_dict = rediscache.__getCache(key)
        consumer_secret =  os.getenv("APP_CLIENT_SECRET", "ChangeMe")
        if ('signed_request' not in request.form):
             return utils.returnResponse("This application is only accessible through Salesforce Canvas App technology. Please access it through Salesforce", 200, cookie, cookie_exists)
        signed_request = request.form['signed_request']
        sr = signedrequest.SignedRequest(consumer_secret, signed_request)
        request_json = sr.verifyAndDecode()
        logger.debug(ujson.loads(request_json))
        return render_template('main_canvas.html', request_json=request_json)
    except Exception as e :
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An Error Occured, please check LogDNA", 200, cookie, cookie_exists)


@app.route('/callback')
def callback():
    return render_template('callback.html')

@app.errorhandler(500)
def serverError(e):
    return render_template('500.html'), 500
