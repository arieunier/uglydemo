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
