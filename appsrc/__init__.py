from flask import Flask, request, redirect, url_for, render_template
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache


TEMPLATES_URL = "../templates"
STATIC_URL = "../static"
# environment variable
WEBPORT = os.getenv('PORT', '5000')



app = Flask(__name__, template_folder=TEMPLATES_URL, static_folder=STATIC_URL) 
Bootstrap(app)

logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue=logs.LOG_LEVEL,
            flaskapp=app)

logger = logs.logger 

from appsrc import connectedapp, marketingapp,guestapp,  misc, uglyapp

from connectedapp import canvas, oauth, badgesmanagement
from guestapp import badges, guest
from marketingapp import marketingcampaign
from misc import notifications
from uglyapp import photo, tables, ugly, votes 

#, guestapp.badges, guestapp.guest, marketingapp.marketingcampaign,  misc.form, misc.notifications, uglyapp.photo, uglyapp.tables, uglyapp.ugly, uglyap.votes




#root, votes, tables, photo, oauth, guest, form, notifications, badges, canvas, marketingcampaign


"""
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=int(WEBPORT))
"""



