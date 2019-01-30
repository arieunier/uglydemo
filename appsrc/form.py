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

        