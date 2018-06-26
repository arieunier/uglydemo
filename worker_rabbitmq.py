from libs import rabbitmq, logs
from appsrc import logger

logger = logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue=logs.LOG_LEVEL,
            flaskapp=None)

rabbitmq.receiveMessage(rabbitmq.CLOUDAMQP_QUEUE)