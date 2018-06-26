import datetime
import uuid
from flask import request
import os 

FOLLOWANALYTICS_API_KEY = os.getenv("FOLLOWANALYTICS_APPLICATION_KEY", None)
FOLLOWANALYTICS_API_TOKEN = os.getenv("FOLLOWANALYTICS_API_TOKEN", None)
FOLLOWANALYTICS_SOR_IDENTIFIER = os.getenv("FOLLOWANALYTICS_SOR_IDENTIFIER", None)
APPNAME = os.getenv("APPNAME", "test-demo-ar")

def str2bool(v):
      return v.lower() in ("yes", "true", "t", "1")

def getCookie():
    import flask
    cookie_exists = True
    cookie_value = flask.request.cookies.get(APPNAME)
    if (cookie_value == None):
        cookie_value = uuid.uuid4().__str__()
        cookie_exists = False

    return cookie_value, cookie_exists

def returnResponse(data, code, cookie_value, cookie_exists):
    from flask import make_response
    resp = make_response(data, code )
    if (cookie_exists == False):
        resp.set_cookie(APPNAME, cookie_value)
    return resp 

      
def __resultToDict(result):
    arrayData =  []
    column_names = [desc[0] for desc in result.cursor.description]

    for entry in result:
        #logger.debug(entry)
        resDic = {}
        for column in column_names:
            #if (isinstance(entry[column], datetime.date)):
            #    print('Date found : ' + entry[column].__str__())
            resDic[column] = entry[column]

            
        arrayData.append(resDic)
    return {'data' : arrayData, 'columns': column_names}


def get_debug_all(request):
    str_debug = '* url: {}\n* method:{}\n'.format(request.url, request.method)
    str_debug += '* Args:\n'
    for entry in request.args:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry, request.args[entry])
    str_debug += '* Headers:\n'
    for entry in request.headers:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry[0], entry[1])
    str_debug += '* Form:\n'
    for entry in request.form:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry, request.form[entry])        
    str_debug += '* Files:\n'        
    for entry in request.files :
        str_debug = str_debug +  '\t* {} = {}\n'.format(entry, request.files[entry])        
    return str_debug    