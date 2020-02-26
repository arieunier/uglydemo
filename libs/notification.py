
from pusher import Pusher
import os 



PUSHER_SOCKET_URL = os.getenv('PUSHER_SOCKET_URL', '')
PUSHER_URL = os.getenv('PUSHER_URL', '')
PUSHER_KEY=None
CLUSTER = ""
APP_ID=""
SECRET = ""

if (PUSHER_URL != ''):
      PUSHER_KEY=PUSHER_URL.replace('http://', '').split('@')[0].split(':')[0]
      SECRET = PUSHER_URL.replace('http://', '').split('@')[0].split(':')[1]
      APP_ID = PUSHER_URL.split('/apps/')[1]
      CLUSTER= PUSHER_URL.split('@api-')[1].split('.')[0]

print("key={} | secret={} | app_id={} | cluster={}".format(PUSHER_KEY, SECRET, APP_ID, CLUSTER))

def sendNotification(channel, message):
  if (PUSHER_URL != ''):
  
      pusher = Pusher(
      app_id=APP_ID, 
      key=PUSHER_KEY,
      secret=SECRET,
      cluster=CLUSTER,
      )

      pusher.trigger(channel, u'my-event', {u'message': message})

if __name__ == "__main__":
    sendNotification('af8dfc4e-2a37-4cf7-b028-b01ebedff9d9', 'huhu')

"""
<script src="https://js.pusher.com/4.2/pusher.min.js"></script>

    <script>
      var pusher = new Pusher({{ key }} , {
      cluster: 'eu'
      });
      var channel = pusher.subscribe( {{ userid }});
      channel.bind('my-event', function(data) {
      alert('An event was triggered with message: ' + data.message);
    });
      </script>
"""