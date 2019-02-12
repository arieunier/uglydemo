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

