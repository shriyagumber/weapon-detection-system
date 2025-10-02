from alertupload_rest.serializers import UploadAlertSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError

from twilio.rest import Client
from threading import Thread
import re
from django.conf import settings
# Create your views here.

# Thread decorator definition
def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target = function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator

# Upload alert
@api_view(['POST'])
# @permission_classes((IsAuthenticated, ))
def post_alert(request):
    serializer = UploadAlertSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        try:
            send_email(serializer)
        except Exception as  e:
            print(f'Email sending failed {e}')
    else:
        return "Error: Unable to process data!"

    return Response(request.META.get('HTTP_AUTHORIZATION'))

# Sends email
@start_new_thread
def send_email(serializer):
    send_mail('Weapon Detected!', 
    prepare_alert_message(serializer), 
    'smit.kadvani@gmail.com',
    [serializer.data['alert_receiver']],
    fail_silently=True,)

# Prepares the alert message
def prepare_alert_message(serializer):
    uuid_with_slashes = split(serializer.data['image'], ".")
    uuid = split(uuid_with_slashes[0], "/")
    print(uuid[1])
    url = 'http://3.12.171.150:8000/alert/' + uuid[1]

    return 'Weapon Detected! View alert at ' + url

def split(value, key):
    return str(value).split(key)
