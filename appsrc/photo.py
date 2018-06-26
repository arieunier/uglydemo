from flask import Flask, request, redirect, url_for, render_template
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache, aws, rabbitmq, notification
from appsrc import app, logger
import time 
from PIL import Image, ExifTags


RENDER_PHOTOS_DISPLAY='photos_display.html'
RENDER_PHOTO_DISPLAY='photo_display.html'
RENDER_ROOT_PHOTO="photo_main.html"
PATH_TO_TEST_IMAGES_DIR = './images'
UPLOAD_IN_REDIS=utils.str2bool(os.getenv("UPLOAD_IN_REDIS", "false"))



logger.info('Upload In Redis = {}'.format(UPLOAD_IN_REDIS))
def bench(completeFilename):
    random_id= uuid.uuid4.__str__()
    aws_filename = random_id + '.jpg'
    amazon_start = datetime.now()
    awsFilename = aws.uploadData(completeFilename, aws_filename)
    amazon_end = datetime.now()
    length_aws = amazon_end - amazon_start

     # Save the image into redis 
    redis_start = datetime.now()
    file = open(completeFilename, "rb")
    data = file.read()
    file.close()
    rediscache.__setCache(random_id, data, 3600)
    redis_end = datetime.now()
    length_redis = redis_end - redis_start
    logger.warning("AWS/REDIS:{}/{}".format(length_aws, length_redis))


@app.route('/photo_display', methods=['GET'])
def photo_display():
    try: 
        cookie , cookie_exists=  utils.getCookie()
        if (postgres.__checkHerokuLogsTable()):
                postgres.__saveLogEntry(request, cookie)
        
        output='html'
        if 'output' in request.args:
            output = request.args['output'].lower()
          
        # logs all attributes received
        logger.debug(utils.get_debug_all(request))
        # gets object name
        object_name='ImageAnalysis__c'

        name = request.args['name']
        key = {'url' : request.url, 'output' : output}
        tmp_dict = None
        data_dict = None
        
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")
            data_dict  = postgres.__getImageAnalysis(object_name, name) 

            if (output == 'html'):
                logger.info("Treating request as a web request, output to Web page")
                if ('image__c' in data_dict['columns']):
                            data = render_template(RENDER_PHOTO_DISPLAY,
                            columns=data_dict['columns'],
                            object_name=object_name,
                            entries = data_dict['data'])
            else:
                logger.info("Treating request as an API request, output to Json only")
                data = ujson.dumps(data_dict)

            #if (postgres.HEROKU_LOGS_TABLE not in request.url): # we don't want to cache these logs
            #    rediscache.__setCache(key, data.encode('utf-8'), 60)

        else:
            logger.info("Data found in redis, using it directly")
            #logger.info(tmp_dict)
            if (output == 'html'):
            #data_dict = ujson.loads(tmp_dict)
                data = tmp_dict.decode('utf-8')
            else:
                #data = ujson.loads(tmp_dict)
                data = tmp_dict

        logger.info("returning data")
        return data, 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "An error occured, check logDNA for more information", 200


@app.route('/photos_display', methods=['GET'])
def photos_display():
    try: 
        cookie , cookie_exists=  utils.getCookie()

        if (postgres.__checkHerokuLogsTable()):
                postgres.__saveLogEntry(request, cookie)
        # output type
        output='html'
        if 'output' in request.args:
            output = request.args['output'].lower()
        
        # logs all attributes received
        logger.debug(utils.get_debug_all(request))
        # gets object name
        object_name='ImageAnalysis__c'
            
        key = {'url' : request.url, 'output' : output}
        tmp_dict = None
        data_dict = None
        tmp_dict = rediscache.__getCache(key)
        data = ""
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")
            data_dict  = postgres.__getObjects(object_name) 

            if (output == 'html'):
                logger.info("Treating request as a web request, output to Web page")
                if ('image__c' in data_dict['columns']):
                            data = render_template(RENDER_PHOTOS_DISPLAY,
                            columns=data_dict['columns'],
                            object_name=object_name,
                            entries = data_dict['data'], FA_APIKEY=utils.FOLLOWANALYTICS_API_KEY, userid=cookie, PUSHER_KEY=notification.PUSHER_KEY)
            else:
                logger.info("Treating request as an API request, output to Json only")
                data = ujson.dumps(data_dict)

            #if (postgres.HEROKU_LOGS_TABLE not in request.url): # we don't want to cache these logs
            #    rediscache.__setCache(key, data.encode('utf-8'), 60)

        else:
            logger.info("Data found in redis, using it directly")
            #logger.info(tmp_dict)
            if (output == 'html'):
            #data_dict = ujson.loads(tmp_dict)
                data = tmp_dict.decode('utf-8')
            else:
                #data = ujson.loads(tmp_dict)
                data = tmp_dict

        logger.info("returning data")
        return utils.returnResponse(data, 200, cookie, cookie_exists)

    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)

@app.route('/photos_post', methods=['POST'])
def image():
    try:
        
        logger.debug(utils.get_debug_all(request))

        i = request.files['fileToUpload']  # get the image
        imageid = uuid.uuid4().__str__()
        f = ('%s.jpeg' % (imageid))
        i.save('%s/%s' % (PATH_TO_TEST_IMAGES_DIR, f))
        completeFilename = '%s/%s' % (PATH_TO_TEST_IMAGES_DIR, f)
        
        
        try:
            filepath = completeFilename
            image=Image.open(filepath)

            img_width = image.size[0]
            img_height = image.size[1]

            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            exif=dict(image._getexif().items())
            logger.debug(exif[orientation])
            if exif[orientation] == 3:
                image=image.rotate(180, expand=True)
                image.save(filepath , quality=50, subsampling=0,)
            elif exif[orientation] == 6:
                image=image.rotate(270, expand=True)
                image.save(filepath , quality=50, subsampling=0,)
            elif exif[orientation] == 8:
                image=image.rotate(90, expand=True)
                image.save(filepath , quality=50, subsampling=0,)
            
            img_width = image.size[0]
            img_height = image.size[1]
            image.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
       
        

        # ok the entry is correct let's add it in our db
        cookie , cookie_exists=  utils.getCookie()
        if (postgres.__checkHerokuLogsTable()):
            postgres.__saveLogEntry(request, cookie)
        
    
        # now upload
        logger.debug(completeFilename)

        #prepare rabbitmq data
        rabbitdata = {
            'id' : imageid,
            'user-agent' : request.headers['User-Agent'],
            'url' : request.url,
            'image_width' : img_width,
            "image_height" : img_height,
            'cookie' : cookie
        } 

        if (UPLOAD_IN_REDIS == True):
            # Save the image into redis 
            file = open(completeFilename, "rb")
            data = file.read()
            file.close()
            rediscache.__setCache(imageid, data, 3600)       
            os.remove(completeFilename)
            logger.info("File saved in Redis")
            rabbitdata['UPLOAD_IN_REDIS'] = True
        else:
            # saves into AWS
            rabbitdata['UPLOAD_IN_REDIS'] = False
            remotefilename = imageid + ".jpg"
            awsFilename = aws.uploadData(completeFilename, remotefilename)
            os.remove(completeFilename)
            logger.info("File saved in AWS")
            rabbitdata['remote_url'] = awsFilename

        # Sends data to RabbitMQ 
        logger.debug(rabbitdata)
        rabbitmq.sendMessage(ujson.dumps(rabbitdata), rabbitmq.CLOUDAMQP_QUEUE)
        #awsFilename = aws.uploadData(completeFilename, f)

        key = {'url' : request.url, 
                'status_upload' : 'Thanks for participating',
                'error_upload' : None}
        
        tmp_dict = None
        #data_dict = None
        tmp_dict = rediscache.__getCache(key)
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")
            data = render_template(RENDER_ROOT_PHOTO, 
              status_upload= "Thanks for participating",
                error_upload=None, FA_APIKEY=utils.FOLLOWANALYTICS_API_KEY, userid=cookie, PUSHER_KEY=notification.PUSHER_KEY)
            #rediscache.__setCache(key, data, 60)
        else:
            logger.info("Data found in redis, using it directly")
            data = tmp_dict            

        return utils.returnResponse(data, 200, cookie, cookie_exists)

    except Exception as e:
        import traceback
        cookie, cookie_exists =  utils.getCookie()  
        data = render_template(RENDER_ROOT_PHOTO, 
            status_upload= None,
            error_upload= "An error occured while saving your file, please try again", FA_APIKEY=utils.FOLLOWANALYTICS_API_KEY, userid=cookie , PUSHER_KEY=notification.PUSHER_KEY)

        return utils.returnResponse(data, 200, cookie, cookie_exists)
        
            

@app.route('/photos', methods=['GET'])
def root_photo():
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
            data = render_template(RENDER_ROOT_PHOTO, FA_APIKEY=utils.FOLLOWANALYTICS_API_KEY, userid=cookie, PUSHER_KEY=notification.PUSHER_KEY)
            #rediscache.__setCache(key, data, 60)
        else:
            logger.info("Data found in redis, using it directly")
            data = tmp_dict            

        return utils.returnResponse(data, 200, cookie, cookie_exists)

    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)

