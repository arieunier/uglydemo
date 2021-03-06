from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache, notification
from appsrc import app, logger
from flask import make_response
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
 

app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

RENDER_ROOT="Ugly/ugly_main.html"

@app.route("/rabbitmq", methods=['GET'])
def rabbitmqsend():
    from libs import rabbitmq
    dataStr = {'id': '876327f6-35a1-43e6-8d46-3dcadab623f7', 
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1', 
    'url': 'https://yourdemo.herokuapp.com/', 'image_width': 2320, 'image_height': 3088, 'cookie': 'f482e8e3-9b64-46b7-9cab-e4fc33ca5f17', 'UPLOAD_IN_REDIS': False, 'remote_url': 'https://bucketeer-ad74aded-29ae-4300-ac4a-2ed34f120de3.s3.eu-west-1.amazonaws.com/public/876327f6-35a1-43e6-8d46-3dcadab623f7.jpg'}
    dataJson = ujson.dumps(dataStr)
    rabbitmq.sendMessage(dataJson, "wtf")
    return "ok"

@app.route('/<filename>', methods=['GET'])
def static_proxy(filename):
    if (filename == None or filename == ''):
        return root()
    return app.send_static_file(filename)

@app.route('/ugly', methods=['GET'])
def root():
    try:
        cookie, cookie_exists =  utils.getCookie()

        if (postgres.__checkHerokuLogsTable()):
            postgres.__saveLogEntry(request, cookie)
        logger.debug(utils.get_debug_all(request))

        key = {'url' : request.url}
        tmp_dict = None
        #data_dict = None
        tmp_dict = rediscache.__getCache(key)
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")


            data = render_template(RENDER_ROOT, FA_APIKEY=utils.FOLLOWANALYTICS_API_KEY, userid=cookie, PUSHER_KEY=notification.PUSHER_KEY)

            rediscache.__setCache(key, data, 60)
        else:
            logger.info("Data found in redis, using it directly")
            data = tmp_dict
            
        
        return utils.returnResponse(data, 200, cookie, cookie_exists)
    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)


@app.route('/error', methods=['GET'])
def error():
    cookie, cookie_exists =  utils.getCookie()

    if (postgres.__checkHerokuLogsTable()):
        postgres.__saveLogEntry(request, cookie)


    logger.debug(utils.get_debug_all(request))
    logger.error("Generating Error")
    error_code = 500
    if ('error_code' in request.args):
        error_code = int(request.args['error_code'])
    return utils.returnResponse("Error !! ", error_code, cookie, cookie_exists)    

