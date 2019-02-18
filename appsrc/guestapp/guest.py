from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache, notification, aws, rabbitmq
from appsrc import app, logger
from flask import make_response
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, FileField
 
#GUESTFILE = "guest_v2.html"
GUESTFILE = "GuestApp/GuestApp.html"
GUESTTHANKS = "GuestApp/GuestThanks.html"


class ReusableForm(Form):
    Firstname = TextField('Firstname', validators=[validators.required()])
    Lastname = TextField('Lastname', validators=[validators.required()])
    Email = TextField('Email', validators=[validators.required()])
    Company = TextField('Company', validators=[validators.required()])
    PhoneNumber = TextField('PhoneNumber', validators=[validators.required()])
    Host = TextField('Host', validators=[validators.required()])
    fileToUpload=TextField('fileToUpload',validators=[validators.required()])



@app.route('/guest', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def guest():
    try:
        cookie, cookie_exists =  utils.getCookie()

        if (postgres.__checkHerokuLogsTable()):
            postgres.__saveLogEntry(request, cookie)

        logger.debug(utils.get_debug_all(request))

        form = ReusableForm(request.form)
        
        hosts = postgres.__getSFUsers()
        key = {'url' : request.url, 'cookie' : cookie}
        tmp_dict = rediscache.__getCache(key)
        data = ""
        if ((tmp_dict != None) and (tmp_dict != '')):    
            #means user has already registered, forwarding him to the guest thanks
            data = render_template(GUESTTHANKS, registered=True, userid=cookie, PUSHER_KEY=notification.PUSHER_KEY)
            #rmeturn utils.returnResponse(data, 200, cookie, cookie_exists)

        if request.method == 'POST':
            Firstname=request.form['Firstname']
            Lastname=request.form['Lastname']
            Email=request.form['Email']
            Company=request.form['Company']
            PhoneNumber=request.form['PhoneNumber']
            Host=request.form['Host']
            Picture="https://3.bp.blogspot.com/-KIngJEZr94Q/Wsxoh-8kwuI/AAAAAAAAQyM/YlDJM1eBvzoDAUV79-0v_Us-amsjlFpkgCLcBGAs/s1600/aaa.jpg"
            if ("fileToUpload" in request.files):
                Picture, rabbitData  =aws.AWS_upload(request.files['fileToUpload'], request)
                rabbitData['cookie'] = cookie
                rabbitData['UPLOAD_IN_REDIS'] = False
                rabbitData['remote_url'] = Picture
                logger.debug(rabbitData)
                rabbitmq.sendMessage(ujson.dumps(rabbitData), rabbitmq.CLOUDAMQP_QUEUE)


            postgres.__saveGuestEntry(Firstname, Lastname, Email, Company, PhoneNumber, Host, cookie, Picture)
            data = render_template(GUESTTHANKS, registered=True, userid=cookie, PUSHER_KEY=notification.PUSHER_KEY)
            rediscache.__setCache(key, data.encode('utf-8'), 3600)
            return utils.returnResponse(data, 200, cookie, cookie_exists)
        
        if form.validate():
            # Save the comment here.
            flash('Hello ' + Firstname)
        else:
            flash('All the form fields are required. ')
        
        data = render_template(GUESTFILE, form=form, hosts=hosts['data'],userid=cookie,PUSHER_KEY=notification.PUSHER_KEY)

        return utils.returnResponse(data, 200, cookie, cookie_exists)
    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)

        