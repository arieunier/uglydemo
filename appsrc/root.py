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

RENDER_INDEX_BOOTSTRAP="index_bootstrap.html"
RENDER_ROOT="index_root.html"
class ReusableForm(Form):
    name = TextField('name:', validators=[validators.required()])
    email = TextField('email:', validators=[validators.required(), validators.Length(min=3, max=35)])
    formvalue = TextField('formvalue:', validators=[validators.required(), validators.Length(min=3, max=35)])
 

# poc function

@app.route('/contact', methods=['GET'])
def contact():
    try:
        cookie, cookie_exists =  utils.getCookie()

        if (postgres.__checkHerokuLogsTable()):
                postgres.__saveLogEntry(request, cookie)
        logger.debug(utils.get_debug_all(request))
        if ('phone' not in request.args):
            return utils.returnResponse("Please provide a phone number", 403, cookie, cookie_exists)
        entry_phone = request.args['phone']
        if (entry_phone == '' or entry_phone == None):
            return utils.returnResponse("Please provide a phone number", 403, cookie, cookie_exists)
        


        key = {'url' : request.url}
        tmp_dict = None
        #data_dict = None
        tmp_dict = rediscache.__getCache(key)
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")
            data_dict = postgres.__execRequest('select name, mobilephone, phone, email, sfid from salesforce.contact where phone = %(phone)s or mobilephone=%(phone)s', {'phone':entry_phone} )
            logger.info(data_dict)
            rediscache.__setCache(key, data_dict, 60)

            data = ujson.dumps(data_dict)
        else:
            logger.info("Data found in redis, using it directly")
            data = tmp_dict


        
        return utils.returnResponse(data, 200, cookie, cookie_exists)
    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 403, cookie, cookie_exists)



@app.route('/oauth2', methods=['GET'])
def oauth():
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


            data = render_template("oauth.html", FA_APIKEY=utils.FOLLOWANALYTICS_API_KEY, userid=cookie)

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


@app.route('/send_notification', methods=['POST'])
def pushNotification():
    try:
        message = request.args['message']
        userid = request.args['userid']
        notification.sendNotification(userid, message)

        return ujson.dumps({'status':'OK'}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return ujson.dumps({'status':'KO'}), 404


@app.route('/<filename>', methods=['GET'])
def static_proxy(filename):
    if (filename == None or filename == ''):
        return root()
    return app.send_static_file(filename)

@app.route('/', methods=['GET'])
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

@app.route('/form', methods=['GET', 'POST'])
def form():
    try:
        cookie, cookie_exists =  utils.getCookie()
        logger.debug(utils.get_debug_all(request))

        form = ReusableForm(request.form)
 
        print(form.errors)
        if request.method == 'POST':
            name=request.form['name']
            formvalue=request.form['formvalue']
            email=request.form['email']
            postgres.__saveLeadEntry(name, email, formvalue)
            data = render_template('form.html', form=form, registered=True)
            return utils.returnResponse(data, 200, cookie, cookie_exists)
        
        print(form)
        if form.validate():
            # Save the comment here.
            flash('Hello ' + name)
        else:
            flash('All the form fields are required. ')
        
        data = render_template('form.html', form=form)
        
        return utils.returnResponse(data, 200, cookie, cookie_exists)
    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)

        