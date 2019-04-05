import requests
result = requests.get('https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=%27www.google.fr%27')
print(result)