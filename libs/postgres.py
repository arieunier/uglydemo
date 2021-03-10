from sqlalchemy import create_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime 
import os , ujson, json
import uuid
from libs import utils , logs , rediscache

DATABASE_URL = os.getenv('DATABASE_URL','')
MANUAL_ENGINE_POSTGRES = None
SALESFORCE_SCHEMA = os.getenv("POSTGRES_SCHEMA", "salesforce")
HEROKU_LOGS_TABLE = os.getenv("HEROKU_LOGS_TABLE", "heroku_logs__c") 
SECURITY_USER= os.getenv("SECURITY_USER")
dbSession_postgres=None
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

def __getSFUsers():
    key = {"sqlRequest" : "getSFUsers"}
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):

        logger.info("Data not found in cache : heroku log data not known")
        sql ="select name, sfid from salesforce.user where CanAcceptGuest__c = 'True' order by name ASC"
        data = __execRequest(sql, {})  
        
        rediscache.__setCache(key, utils.jsonencode(data), 60)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    logger.debug(data)
    return data   

def _test_transaction():
    global dbSession_postgres
    isolatedsession = dbSession_postgres()
    try:
        # performs something
        update =  """ update salesforce.heroku_logs__c set useragent__c=useragent__c || ' ';  """
        isolatedsession.execute(update)
        getRows =  """ select count(*) as nbRows, _hc_lastop from salesforce.heroku_logs__c group by  _hc_lastop """
        results = isolatedsession.execute(getRows)
        for result in results:
            print(result)
        isolatedsession.commit()
    except Exception as e:
        import traceback
        traceback.print_exc()
        isolatedsession.rollback()
    finally:
        isolatedsession.close()

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
        rediscache.__setCache(key, utils.jsonencode(data), 60)
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
        rediscache.__setCache(key, utils.jsonencode(data), 60)
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
        rediscache.__setCache(key, utils.jsonencode(data), 60)
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
        rediscache.__setCache(key, utils.jsonencode(data), 60)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    return data

def __insertBadge(id, guest_id, guest_firstname, guest_lastname, guest_company, host_firstname, host_lastname, badge_status, badge_url,
picture_url):
    sqlRequest = """
    insert into public.badge(id, guest_id, guest_firstname, guest_lastname, guest_company, host_firstname, host_lastname, badge_status, badge_url, creation_date, picture_url) values
    (%(id)s, %(guest_id)s, %(guest_firstname)s, %(guest_lastname)s, %(guest_company)s, %(host_firstname)s, %(host_lastname)s, %(badge_status)s, %(badge_url)s, NOW(), %(picture_url)s)
    """
    if (MANUAL_ENGINE_POSTGRES != None):
        MANUAL_ENGINE_POSTGRES.execute(sqlRequest, {
            'id': id,
            'guest_id': guest_id,
            'guest_firstname': guest_firstname,
            'guest_lastname': guest_lastname,
            'guest_company': guest_company,
            'host_firstname': host_firstname,
            'host_lastname': host_lastname,
            'badge_status': badge_status,
            'badge_url': badge_url,
            'picture_url' : picture_url
        })

def __insertCase(cookieid, subject, description, typeCase, reason):
    # gets the securit user
    security  = __execRequest("""
    select * from salesforce.user where 
    name=%(security_username)s 
    order by createddate DESC limit 1 
    """, {'security_username':SECURITY_USER})

    # gets the Contact ID from GUEST ID
    contact = __execRequest("""
    select * from salesforce.guest__c where 
    webuser__r__userid__c=%(cookieid)s 
    order by createddate DESC limit 1 
    """, {'cookieid':cookieid})
    #contact = __execRequest("Select contact__c from salesforce.guest__c where id=%(guestId)s", {'id':guestId})
    # gets the business hour Id
    businessHour = __execRequest("Select id, sfid, name from salesforce.BusinessHours", None)
    # now lets go yellow
    externalid = uuid.uuid4().__str__()
    
    insertCase = """
        insert into salesforce.case(priority, origin, contactid, subject, description, reason, type, external_id__c, businesshoursid ) values
        ('High', 'Web', %(contactid)s, %(subject)s, %(description)s, %(reason)s, %(type)s, %(externalid)s, %(businesshourid)s )
        """
    
    CaseAttributes =  { 'contactid' : contact['data'][0]['contact__c'],
        'subject':subject,
        'description' : description,
        'reason' : reason,
        'type' : typeCase,
        'externalid' : externalid,
        'businesshourid':businessHour['data'][0]['sfid']
        }
    if (len(security['data']) > 0):
        # change the ownership of the case
        insertCase = """
        insert into salesforce.case(ownerid, priority, origin, contactid, subject, description, reason, type, external_id__c, businesshoursid ) values
        (%(ownerid)s, 'High', 'Web', %(contactid)s, %(subject)s, %(description)s, %(reason)s, %(type)s, %(externalid)s, %(businesshourid)s )
        """
        CaseAttributes['ownerid']= security['data'][0]['sfid']
    __execRequestWithNoResult(insertCase,CaseAttributes)    
    return ""

def __execRequestWithNoResult(strReq, attributes=None):
    if (MANUAL_ENGINE_POSTGRES != None):
        result = MANUAL_ENGINE_POSTGRES.execute(strReq, attributes)

def getBadgeById(badgeId):
    return __execRequest('Select * from public.badge where id=%(id)s', {'id':badgeId})

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
        rediscache.__setCache(key, utils.jsonencode(data), 120)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    return data

def __getObjectsDescribe(tableName):
    key = {"sqlRequest" : "__getObjectsDescribe", "tableName" : tableName}
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
        logger.info("Data not found in cache : data not known")
        concat = SALESFORCE_SCHEMA + "." + tableName
        data = __execRequest("select * from {} limit 1".format(concat), {})
        logger.info("Data Returned")
        logger.info(data)
        rediscache.__setCache(key, utils.jsonencode(data), 30)
    else:
        logger.info("Data found in redis, using it directly")
        data = ujson.loads(tmp_dict)

    return data
        
def __getObjects(tableName):
    key = {"sqlRequest" : "__getObjects", "tableName" : tableName}
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
        logger.info("Data not found in cache : data not known")
        concat = SALESFORCE_SCHEMA + "." + tableName
        data = __execRequest("select * from {}".format(concat), {})
        logger.info("Data Returned")
        logger.info(data)
        rediscache.__setCache(key, utils.jsonencode(data), 30)
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
        
        rediscache.__setCache(key, utils.jsonencode(data), 30)
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

def __saveGuestEntry(Firstname, Lastname, Email, Company, PhoneNumber, Host, cookie, picture):
    if (MANUAL_ENGINE_POSTGRES != None):
        externalid = uuid.uuid4().__str__()
        creationdate  = datetime.now()
        sqlRequest = """ insert into salesforce.guest__c(Firstname__c, Lastname__c, Email__c, Company__c, Phone_Number__c, Host__c, webuser__r__userid__c, External_Picture_URL__c) values 
         (%(Firstname)s, %(Lastname)s, %(Email)s, %(Company)s, %(PhoneNumber)s, %(Host)s, %(cookie)s, %(picture)s)   """

        MANUAL_ENGINE_POSTGRES.execute(sqlRequest,
            {
            'Firstname' : Firstname,
            'Lastname' : Lastname,
            'Company' : Company,
            'Email' : Email,
            'PhoneNumber' : PhoneNumber,
            'Host' : Host ,'cookie' : cookie ,
            'picture':picture})    

def __savePackagingReviewEntry(Name, Email, Brand, Grip, Plug, Portability, FreeText, Picture):
    if (MANUAL_ENGINE_POSTGRES != None):
        id = uuid.uuid4().__str__()
        sqlRequest = """ insert into public.packagingreviews(id, ParticipantName,
        ParticipantEmail, BrandEvaluated, GripReview, PlugReview, PortabilityReview, FreeText, image_url, creation_date)
        values (%(id)s, %(Name)s, %(Email)s, %(Brand)s, %(Grip)s, %(Plug)s, %(Portability)s, %(FreeText)s, %(Picture)s, NOW() )  """

        MANUAL_ENGINE_POSTGRES.execute(sqlRequest,
            {
            'id' : id,
            'Name' : Name,
            'Email' : Email,
            'Brand' : Brand,
            'Grip' : Grip,
            'Plug' : Plug,
            'Portability' : Portability ,
            'FreeText' : FreeText ,
            'Picture':Picture})    

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
        
        creationdate  = datetime.now()


        sqlRequestUserId = """
            insert into salesforce.webusers__c(name, userid__c, useragent__c) values 
            (%(userid)s, %(userid)s, %(useragent)s)
                ON CONFLICT (userid__c) DO NOTHING"""
        MANUAL_ENGINE_POSTGRES.execute(sqlRequestUserId,
                    {'useragent':useragent,
                    'userid' : userid})    
        
        sqlRequest = """insert into salesforce.heroku_logs__c (userid__c, name, url__c, creationdate__c, externalid__c, useragent__c, method__c, webuser__r__userid__c) values 
            ( %(userid)s, %(name)s, %(url)s, %(creationdate)s, %(externalid)s, %(useragent)s , %(method)s , %(userid)s ) """
        externalid = uuid.uuid4().__str__()
        MANUAL_ENGINE_POSTGRES.execute(sqlRequest,
                    {'tablename' : SALESFORCE_SCHEMA + '.' + HEROKU_LOGS_TABLE,
                    'url' : url,
                    'name' : externalid,
                    'creationdate':creationdate,
                    'externalid' : externalid,
                    'useragent':useragent,
                    'method' : request.method,
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
    


_test_transaction()