from sqlalchemy import create_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime 
import os , ujson
import uuid
from libs import utils , logs , rediscache

DATABASE_URL = os.getenv('DATABASE_URL','')
MANUAL_ENGINE_POSTGRES = None
SALESFORCE_SCHEMA = os.getenv("POSTGRES_SCHEMA", "salesforce")
HEROKU_LOGS_TABLE = os.getenv("HEROKU_LOGS_TABLE", "heroku_logs__c") 

logger = logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue=logs.LOG_LEVEL,
            flaskapp=None)

if (DATABASE_URL != ''):
    Base = declarative_base()
    MANUAL_ENGINE_POSTGRES = create_engine(DATABASE_URL, pool_size=30, max_overflow=0)
    Base.metadata.bind = MANUAL_ENGINE_POSTGRES
    dbSession_postgres = sessionmaker(bind=MANUAL_ENGINE_POSTGRES)
    session_postgres = dbSession_postgres()
    logger.info("{} - Initialization done Postgresql ".format(datetime.now()))


def __getGameActivityById(gameactivity__c):
    key = {"sqlRequest" : "__getGameActivityById", "activityId" : gameactivity__c}
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):

        logger.info("Data not found in cache : heroku log data not known")
        sqlRequestActivityName = """
            select gameactivity__c.name ActivityName
            from 
                salesforce.gameactivity__c  
            where
                 gameactivity__c.sfid = %(gameactivity__c)s """

        data = __execRequest(sqlRequestActivityName, {'gameactivity__c':gameactivity__c}) 
        rediscache.__setCache(key, ujson.dumps(data), 60)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    return data   

def __getMatchsByGameActivityId(gameactivity__c):
    sqlRequest = """select match__c.sfid matchid ,
            match__c.date__c Date,
            match__c.question__c Question,
            participant__c_home.name as Participant_Home,
            participant__c_visitor.name Participant_Visitor
            
            from 
                    salesforce.match__c match__c, 
                    salesforce.participant__c participant__c_home , 
                    salesforce.participant__c participant__c_visitor
                    
            where match__c.gameactivity__c =  %(gameactivity__c)s
            and (participant__c_home.sfid = match__c.participant_home__c)
            and (participant__c_visitor.sfid = match__c.participant_visitor__c)
            
            order by 
            
            match__c.date__c DESC"""

    key = {"sqlRequest" : "__getMatchsByGameActivityById", "activityId" : gameactivity__c}
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
        logger.info("Data not found in cache : heroku log data not known")
        data = __execRequest(sqlRequest, {'gameactivity__c':gameactivity__c})
        rediscache.__setCache(key, ujson.dumps(data), 60)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    return data

def __getMatchs():
    sqlRequest = """
                    select   
                        salesforce.gameactivity__c.name , 
                        salesforce.gameactivity__c.sfid, 
                        (select count(*) from  salesforce.match__c where salesforce.match__c.gameactivity__c = salesforce.gameactivity__c.sfid) as nbMatchs 
                    from salesforce.gameactivity__c 
                    where salesforce.gameactivity__c.active__c = True
                    """
    key = {"sqlRequest" : "__getMatchs" }
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
        logger.info("Data not found in cache : heroku log data not known")
        data = __execRequest(sqlRequest, None)
        rediscache.__setCache(key, ujson.dumps(data), 60)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    return data

def __getMatchById(match_id):
    sqlRequest = """select date__c , 
       match__c.participant_home__c participant_home_id,
       match__c.participant_visitor__c participant_visitor_id,
       match__c.sfid match_id,
       match__c.gameactivity__c gameactivity__c,
       match__c.question__c question__c,
       participant__home.name participant_home_name,
       participant__home.image__c participant_home_image,
       participant__home.description__c participant_home_description,
       participant__visitor.name participant_visitor_name,
       participant__visitor.image__c participant_visitor_image,
       participant__visitor.description__c participant_visitor_description
       
        from salesforce.match__c, 
            salesforce.participant__c participant__home,
            salesforce.participant__c participant__visitor

        where match__c.sfid= %(match_id)s 
        and (participant__home.sfid = match__c.participant_home__c)
        and (participant__visitor.sfid = match__c.participant_visitor__c)"""

    key = {"sqlRequest" : "__getMatchById", "match_id" : match_id}
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
        logger.info("Data not found in cache : heroku log data not known")
        data = __execRequest(sqlRequest, {'match_id':match_id})
        rediscache.__setCache(key, ujson.dumps(data), 60)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    return data


def __execRequest(strReq, Attributes):
    if (MANUAL_ENGINE_POSTGRES != None):
        result = MANUAL_ENGINE_POSTGRES.execute(strReq, Attributes)
        return utils.__resultToDict(result)
    return {'data' : [], "columns": []}

def __getImageAnalysis(tableName, objectName):
    key = {"sqlRequest" : "__getImageAnalysis", "objectName" : objectName}
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
        logger.info("Data not found in cache : heroku log data not known")
        concat = SALESFORCE_SCHEMA + "." + tableName
        data = __execRequest("select * from {} where name='{}' ".format(concat, objectName), {})
        rediscache.__setCache(key, ujson.dumps(data), 120)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    return data


def __getObjects(tableName):
    key = {"sqlRequest" : "__getObjects", "tableName" : tableName}
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
        logger.info("Data not found in cache : heroku log data not known")
        concat = SALESFORCE_SCHEMA + "." + tableName
        data = __execRequest("select * from {}".format(concat), {})
        
        rediscache.__setCache(key, ujson.dumps(data), 30)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    return data
        

def __getTables():
    
    key = {"sqlRequest" : "__getTables"}
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
        logger.info("Data not found in cache : heroku log data not known")
        sqlRequest = "SELECT table_schema, table_name FROM information_schema.tables where table_schema like '%%alesforce' ORDER BY table_schema,table_name"
        data = __execRequest(sqlRequest, {})
        
        rediscache.__setCache(key, ujson.dumps(data), 30)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    return data





def __saveImageAnalysisEntry(attributes):
    if (MANUAL_ENGINE_POSTGRES != None):
        sqlRequest = """
            insert into salesforce.ImageAnalysis__c (Age__c, Anger__c, Bald__c, Beard__c, Contempt__c, Description__c, Disgust__c, Fear__c,
            Gender__c, Glasses__c, Haircolor__c, Happiness__c, image__c, MediaId__c, Moustache__c, Name, Neutral__c, PersonId__c, 
            Sadness__c, Smile__c, Surprise__c, URL__c, UserAgent__c, eyemakeup__c, lipmakeup__c, Hair__c, FacialHair__c, Emotion__c, Emotion_Value__c, Smile_value__c,
            ImageWidth__c, ImageHeight__c, FaceTop__c, FaceLeft__c, FaceWidth__c, FaceHeight__c ) values

            (%(Age__c)s, %(Anger__c)s, %(Bald__c)s, %(Beard__c)s, %(Contempt__c)s, %(Description__c)s, %(Disgust__c)s, %(Fear__c)s,
            %(Gender__c)s, %(Glasses__c)s, %(Haircolor__c)s, %(Happiness__c)s, %(image__c)s, %(MediaId__c)s, %(Moustache__c)s, %(Name)s, %(Neutral__c)s, %(PersonId__c)s, 
            %(Sadness__c)s, %(Smile__c)s, %(Surprise__c)s, %(URL__c)s, %(UserAgent__c)s, %(eyemakeup__c)s, %(lipmakeup__c)s, %(Hair__c)s, %(FacialHair__c)s, %(Emotion__c)s, %(Emotion_Value__c)s, %(Smile_value__c)s,
            %(ImageWidth__c)s, %(ImageHeight__c)s, %(FaceTop__c)s, %(FaceLeft__c)s, %(FaceWidth__c)s, %(FaceHeight__c)s  )
            """
        MANUAL_ENGINE_POSTGRES.execute(sqlRequest,attributes)

def __saveLeadEntry(name, email, formvalue):
    if (MANUAL_ENGINE_POSTGRES != None):
        externalid = uuid.uuid4().__str__()
        creationdate  = datetime.now()
        sqlRequest = """ insert into salesforce.FormContent__c(Name, email__c, FormValue__c, externalid__c, createddate) values 
         (%(name)s, %(email)s, %(formvalue)s, %(externalid)s, %(createddate)s)   """

        MANUAL_ENGINE_POSTGRES.execute(sqlRequest,
            {
            'name' : name,
            'externalid' : externalid,
            'formvalue' : formvalue,
            'email' : email,
            'createddate' : creationdate })    

def __saveLogEntry(request, userid):
    if (MANUAL_ENGINE_POSTGRES != None):
        url = request.url
        useragent = request.headers['user-agent']
        externalid = uuid.uuid4().__str__()
        creationdate  = datetime.now()


        sqlRequest = """insert into salesforce.heroku_logs__c (userid__c, name, url__c, creationdate__c, externalid__c, useragent__c, method__c) values 
            ( %(userid)s, %(name)s, %(url)s, %(creationdate)s, %(externalid)s, %(useragent)s , %(method)s ) """

        MANUAL_ENGINE_POSTGRES.execute(sqlRequest,
                    {'tablename' : SALESFORCE_SCHEMA + '.' + HEROKU_LOGS_TABLE,
                    'url' : url,
                    'name' : externalid,
                    'creationdate':creationdate,
                    'externalid' : externalid,
                    'useragent':useragent,
                    'method' : request.method,
                    'userid' : userid})    

        sqlRequestUserId = """
            insert into salesforce.webusers__c(name, userid__c, useragent__c) values 
            (%(userid)s, %(userid)s, %(useragent)s)
                ON CONFLICT (userid__c) DO NOTHING"""
        MANUAL_ENGINE_POSTGRES.execute(sqlRequestUserId,
                    {'useragent':useragent,
                    'userid' : userid})    


def __checkHerokuLogsTable():
    key = {'checkHerokuLogTables' : "True"}
    tmp_dict = None
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
        logger.info("Data not found in cache : heroku log data not known")
        hasDatabase = False
    
        if (MANUAL_ENGINE_POSTGRES != None):
            sqlRequest = 'SELECT EXISTS( SELECT * FROM information_schema.tables  WHERE table_schema = %(schema)s AND table_name = %(tablename)s ) '
            result = MANUAL_ENGINE_POSTGRES.execute(sqlRequest, {'schema' : SALESFORCE_SCHEMA, 'tablename' : HEROKU_LOGS_TABLE} )
            for entry in result:
                logger.info(entry['exists'])
                hasDatabase = entry['exists']
            if (hasDatabase == True):
                rediscache.__setCache(key, "True", 3600)
        return hasDatabase
    else:
        return True 
    
