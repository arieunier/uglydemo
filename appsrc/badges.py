from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache, notification, kafka_utils
from appsrc import app, logger
from flask import make_response

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

"""
    create table public.badge(id varchar(35) not null, guest_id varchar(35) not null, guest_firstname varchar(255) not null, guest_lastname varchar(255) not null,
    guest_company varchar(255), host_firstname varchar(35) not null, host_lastname varchar(35) not null, badge_status varchar(35), badge_url varchar(255))

    insert into public.badge(id, guest_id, guest_firstname, guest_lastname, guest_company, host_firstname, host_lastname, badge_status, badge_url) values
    ('123', 'a0E0E000001sXBkUAM', 'test', 'test', 'test', 'first', 'last', 'status', 'www.google.fr')
"""

#functions
# add


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
            badge_status = 'INACTIVE'
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
            # gets inseeid
            sqlRequest = "select * from public.badge"
            data = postgres.__execRequest(sqlRequest, None)
            return utils.returnResponse(ujson.dumps(data), 200, cookie, cookie_exists) 

    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 403, cookie, cookie_exists) 




# with user identity management

# revoke

# get

