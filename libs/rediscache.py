import redis 
import os
import ujson
from datetime import datetime 
from libs import logs   

REDIS_URL = os.getenv('REDIS_URL','')
REDIS_CONN = None 

logger = logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue=logs.LOG_LEVEL,
            flaskapp=None)


if (REDIS_URL != ''):
    REDIS_CONN = redis.from_url(REDIS_URL)
    REDIS_CONN.set('key','value')
    REDIS_CONN.expire('key', 300) # 5 minutes
    logger.info("{}  - Initialization done Redis" .format(datetime.now()))

def __display_RedisContent():
    if (REDIS_CONN != None):
        for keys in REDIS_CONN.scan_iter():
            logger.info(keys)
    cacheData = __getCache('keys *')
    if cacheData != None:
        for entry in cacheData:
            logger.info(entry)

def __setCache(key, data, ttl):
    key_str = ujson.dumps(key)
    if (REDIS_CONN != None):
        logger.debug('Storing in Redis')
        REDIS_CONN.set(key_str, data)
        REDIS_CONN.expire(key_str, ttl)

def __getCache(key):
    key_str = ujson.dumps(key)
    if (REDIS_CONN != None):
        logger.debug('Reading in Redis')
        return REDIS_CONN.get(key_str)
    return None 

def __delCache(key):
    key_str = ujson.dumps(key)
    if (REDIS_CONN != None):
        logger.debug('Deleting in Redis')
        REDIS_CONN.delete(key_str)
    