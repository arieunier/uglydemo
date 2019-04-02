from libs import rabbitmq
import os 

import pika
""" 
connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get('CLOUDAMQP_URL', '')))
channel = connection.channel()
 
 
 
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
 
channel.basic_consume(callback,
                      queue='web-to-workers',
                      no_ack=True)
 
print(' [*] Waiting for messages. To exit press CTRL+C')

"""

rabbitmq.receiveMessage(rabbitmq.CLOUDAMQP_QUEUE)