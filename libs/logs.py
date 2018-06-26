import os, logging, psycopg2 

LOG_LEVEL = os.getenv('LOG_LEVEL','INFO')

logger = None
# log activation
def logger_init(loggername='app', filename='', debugvalue=LOG_LEVEL, flaskapp=None):
    global logger
    if (logger == None):
        from logging.handlers import TimedRotatingFileHandler

        logger = logging.getLogger(loggername)

        # création d'un formateur qui va ajouter le temps, le niveau
        # de chaque message quand on écrira un message dans le log
        format_string = "{'%(asctime)s.%(msecs)03d','%(levelname)s',%(process)s,%(filename)s:%(lineno)s-%(funcName)s:-->%(message)s}"
        log_formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')

        numeric_level = getattr(logging, debugvalue.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: {}' % debugvalue)

        logger.setLevel(numeric_level)
        if (flaskapp != None):
            flaskapp.logger.setLevel(numeric_level)

        file_handler = TimedRotatingFileHandler(filename, when="midnight", backupCount=10)
        # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
        # créé précédement et on ajoute ce handler au logger
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
        if (flaskapp != None):
            flaskapp.logger.addHandler(file_handler)
        # now stdout
        steam_handler = logging.StreamHandler()
        steam_handler.setLevel(logging.DEBUG)
        steam_handler.setFormatter(log_formatter)
        logger.addHandler(steam_handler)
        if (flaskapp != None):
            flaskapp.logger.addHandler(steam_handler)
            # and UDP
    
    return logger


