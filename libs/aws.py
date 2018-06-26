import boto3
import os 
from appsrc import  logger

BUCKETEER_AWS_ACCESS_KEY_ID=  os.getenv('BUCKETEER_AWS_ACCESS_KEY_ID','')
BUCKETEER_AWS_REGION= os.getenv('BUCKETEER_AWS_REGION','')
BUCKETEER_AWS_SECRET_ACCESS_KEY= os.getenv("BUCKETEER_AWS_SECRET_ACCESS_KEY", "")
BUCKETEER_BUCKET_NAME= os.getenv("BUCKETEER_BUCKET_NAME", "") 



#logger.debug(BUCKETEER_AWS_ACCESS_KEY_ID)
#logger.debug(BUCKETEER_AWS_REGION)
#logger.debug(BUCKETEER_AWS_SECRET_ACCESS_KEY)
#logger.debug(BUCKETEER_BUCKET_NAME)


#boto3.set_stream_logger(name='botocore')

s3 = boto3.client('s3',aws_access_key_id=BUCKETEER_AWS_ACCESS_KEY_ID,aws_secret_access_key=BUCKETEER_AWS_SECRET_ACCESS_KEY)

def uploadData(localfilename, remotefilename):
    try:
        bucket_name = BUCKETEER_BUCKET_NAME
        s3.upload_file(localfilename, bucket_name, 'public/' + remotefilename)
        url ="https://"+BUCKETEER_BUCKET_NAME + '.s3.' + BUCKETEER_AWS_REGION + '.amazonaws.com/' + 'public/' + remotefilename
        logger.debug(url)
        return url
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
