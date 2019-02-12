import boto3
import os 
from appsrc import  logger
import uuid 

BUCKETEER_AWS_ACCESS_KEY_ID=  os.getenv('BUCKETEER_AWS_ACCESS_KEY_ID','')
BUCKETEER_AWS_REGION= os.getenv('BUCKETEER_AWS_REGION','')
BUCKETEER_AWS_SECRET_ACCESS_KEY= os.getenv("BUCKETEER_AWS_SECRET_ACCESS_KEY", "")
BUCKETEER_BUCKET_NAME= os.getenv("BUCKETEER_BUCKET_NAME", "") 



#logger.debug(BUCKETEER_AWS_ACCESS_KEY_ID)
#logger.debug(BUCKETEER_AWS_REGION)
#logger.debug(BUCKETEER_AWS_SECRET_ACCESS_KEY)
#logger.debug(BUCKETEER_BUCKET_NAME)

import mimetypes 


#boto3.set_stream_logger(name='botocore')

s3 = boto3.client('s3',aws_access_key_id=BUCKETEER_AWS_ACCESS_KEY_ID,aws_secret_access_key=BUCKETEER_AWS_SECRET_ACCESS_KEY)

def uploadData(localfilename, remotefilename):
    try:

        mimetype, _ = mimetypes.guess_type(localfilename)
        if mimetype is None:
            raise Exception("Failed to guess mimetype")
    
        bucket_name = BUCKETEER_BUCKET_NAME
        s3.upload_file(localfilename, bucket_name, 'public/' + remotefilename, ExtraArgs={'ContentType': mimetype})
        url ="https://"+BUCKETEER_BUCKET_NAME + '.s3.' + BUCKETEER_AWS_REGION + '.amazonaws.com/' + 'public/' + remotefilename
        logger.debug(url)
        return url
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None


# saves a file into a bucket in AWS
def AWS_upload(file, request):
    from PIL import Image, ExifTags
    from libs import aws  
    
    PATH_TO_TEST_IMAGES_DIR = './images'
    i = file  # get the image
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
        try:
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
        except Exception as e:
            import traceback
            traceback.print_exc()
 
        image.close()

        remotefilename = imageid + ".jpg"
        logger.info("RemoteFilename = " + remotefilename)
        logger.info("completeFilename = " + completeFilename)
        awsFilename = aws.uploadData(completeFilename, remotefilename)
        os.remove(completeFilename)
        logger.info("File saved in AWS as " + awsFilename)

        rabbitdata = {
            'id' : imageid,
            'user-agent' : request.headers['User-Agent'],
            'url' : request.url,
            'image_width' : img_width,
            "image_height" : img_height,
            'cookie' : ""
        } 


        return awsFilename, rabbitdata
    except Exception as e:
        import traceback
        traceback.print_exc()
        return "", {}