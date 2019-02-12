from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache, notification, rabbitmq, aws
from appsrc import app, logger
from flask import make_response
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask import Flask, render_template, flash, request
from wtforms import Form,TextField, TextAreaField, validators, StringField, SubmitField, FileField
import traceback


#GUESTFILE = "guest_v2.html"
MARKETFILE = "MarketingCampaign.html"
MARKETTHANKS = "MarketingCampaignThanks.html"

BRANDS = [
    {'name':'Evian'},
    {'name':'Volvic'},
    {'name':'Aqua'},
    {'name':'Mizone'},
{'name':'Bonafont'},
{'name':'Font-Vella'},
{'name':'Zywiec-Zdroj'},
{'name':'Villavicencio'},
{'name':'Villa-Del-Sur'},    
{'name':'Salus'},
{'name':'Hayat'}
]
class ReusableForm(Form):
    Name = TextField('Name', validators=[validators.required()])
    Email = TextField('Email', validators=[validators.required()])
    Brand = TextField('Brand', validators=[validators.required()])
    Grip = TextField('Grip', validators=[validators.required()])
    Plug = TextField('Plug', validators=[validators.required()])
    Portability = TextField('Portability', validators=[validators.required()])
    #FreeText = TextField('FreeText')#, validators=[validators.notres])
    fileToUpload=TextField('fileToUpload',validators=[validators.required()])


@app.route("/initPackagingReviews", methods=['GET'])
def initPackagingReviews():
    try:

        # sqlRequestDrop = "drop table public.badge";
        #postgres.__execRequestWithNoResult(sqlRequestDrop)
        sqlRequestCreate = """
        create table public.packagingreviews(
            id varchar(255) not null primary key, 
            ParticipantName varchar(255) not null, 
            ParticipantEmail varchar(255) not null, 
            BrandEvaluated varchar(255) not null,
            GripReview varchar(255), 
            PlugReview varchar(255) not null, 
            PortabilityReview varchar(255) not null, 
            Freetext varchar(255), 
            image_url varchar(255), 
            creation_date timestamp not null)

        """
        
        postgres.__execRequestWithNoResult(sqlRequestCreate)
        return "{'Result':'Ok'}"
    except Exception as e :
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 403, cookie, cookie_exists) 

@app.route("/brand-blazers", methods=['GET'])
def brandblazers():
    try:
            logger.debug(utils.get_debug_all(request))
            cookie, cookie_exists =  utils.getCookie()
            sql = "select brandevaluated, freetext, image_url, creation_date from public.packagingreviews order by creation_date desc LIMIT 50 "
            data = postgres.__execRequest(sql, None)

            logger.info(data)

            data = render_template("brand-blazers.html",
                            columns=data['columns'],
                            entries = data['data'])

            return utils.returnResponse(data, 200, "cookie", cookie_exists)

            return "ok"
    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)

@app.route('/marketingcampaign', methods=['GET', 'POST'])
def marketingcampaign():
    try:
        cookie, cookie_exists =  utils.getCookie()
        logger.debug(utils.get_debug_all(request))

        form = ReusableForm(request.form)
        
        key = {'url' : request.url}
        tmp_dict = rediscache.__getCache(key)
        data = ""
        
        if request.method == 'POST':
            Name = request.form['Name']
            Email = request.form['Email']
            Brand = request.form['Brand']
            Grip = request.form['Grip']
            Plug = request.form['Plug']
            Portability = request.form['Portability']
            FreeText = request.form['FreeText']
            Picture="https://3.bp.blogspot.com/-KIngJEZr94Q/Wsxoh-8kwuI/AAAAAAAAQyM/YlDJM1eBvzoDAUV79-0v_Us-amsjlFpkgCLcBGAs/s1600/aaa.jpg"
            if ("fileToUpload" in request.files):
                Picture, rabbitData = aws.AWS_upload(request.files['fileToUpload'], request)
                rabbitData['cookie'] = cookie
                rabbitData['UPLOAD_IN_REDIS'] = False
                rabbitData['remote_url'] = Picture
                logger.debug(rabbitData)
                rabbitmq.sendMessage(ujson.dumps(rabbitData), rabbitmq.CLOUDAMQP_QUEUE)


            postgres.__savePackagingReviewEntry(Name, Email, Brand, Grip, Plug, Portability, FreeText, Picture)

            data = render_template(MARKETTHANKS)
            #rediscache.__setCache(key, data.encode('utf-8'), 3600)

  


            return utils.returnResponse(data, 200, cookie, cookie_exists)
        else: 
            if form.validate():
                # Save the comment here.
                flash('Hello ')
            else:
                flash('All the form fields are required. ')
        
            if ((tmp_dict != None) and (tmp_dict != '')):    
                logger.info("form already in redis, retrieving it")
                data = tmp_dict
            else:
                data = render_template(MARKETFILE, 
                    form=form, 
                    brands=BRANDS)
                rediscache.__setCache(key, data.encode('utf-8'), 120)

            return utils.returnResponse(data, 200, cookie, cookie_exists)
    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)

        