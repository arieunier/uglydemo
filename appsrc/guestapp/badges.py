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


BADGE_DATA="GuestApp/Badge.html"
APPNAME = os.getenv("APPNAME", "yourdemo")
APPURL="https://" + APPNAME + ".herokuapp.com/badge/"
QRCODE_URL="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data="
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


@app.route("/badge/<badge_id>", methods=['GET'])
def badgeById(badge_id):
    # get the badge
    if (badge_id != None and badge_id != ""):
        cookie, cookie_exists =  utils.getCookie()
        badge_content = postgres.__execRequest("Select * from badge where id=%(badge_id)s and badge_status='ACTIVE' " , {'badge_id':badge_id})
        
        if (len(badge_content['data']) > 0):
            logger.info(badge_content)
            if ('output' in request.args):
                if (request.args['output'] == 'json'):
                    return utils.returnResponse(utils.jsonencode(data), 200, cookie, cookie_exists) 
            QRCODE_COMPLETE_URL = QRCODE_URL + "'" + APPURL +  badge_content['data'][0]['id'] + "?output=json'"
            logger.info(QRCODE_COMPLETE_URL)
            data = render_template(BADGE_DATA, 
                GuestFirstname=badge_content['data'][0]['guest_firstname'],
                GuestLastname = badge_content['data'][0]['guest_lastname'], 
                GuestCompany=badge_content['data'][0]['guest_company'], 
                HostFirstname=badge_content['data'][0]['host_firstname'], 
                HostLastname=badge_content['data'][0]['host_lastname'],
                ProfilePicture=badge_content['data'][0]['picture_url'], 
                QRCode=QRCODE_COMPLETE_URL)

            return utils.returnResponse(data, 200, cookie, cookie_exists) 
    return utils.returnResponse(ujson.dumps({'Error' : 'Unknown or incorrect badge id'}), 404, cookie, cookie_exists) 

    

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
            picture_url = request.args.get('picture_url')
            # id is auto generated
            uid = uuid.uuid4().__str__()
            badge_status = 'ACTIVE'
            badge_url = APPURL + uid
            # status is set to default -> INACTIVE (status are inactive / active )
            # url will be calculated
            
            # gets new city
        
            if (guest_id == '' or guest_id == None):
                return utils.returnResponse("Please provide a guest_id", 403, None, None) 
            # check if siren__c exits
 
            postgres.__insertBadge(uid, guest_id, guest_firstname, guest_lastname, guest_company, host_firstname, host_lastname, badge_status, badge_url,picture_url)


            # generates now the data
            #data = render_template(BADGE_DATA, GuestFirstname=guest_firstname,
            #GuestLastname = guest_lastname, GuestCompany=guest_company, HostFirstname=host_firstname, HostLastname=host_lastname,
            #ProfilePicture=picture_url, QRCode="")

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
