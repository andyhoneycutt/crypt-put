from django.shortcuts import render
from django.shortcuts import get_object_or_404 as go404
from django.http import JsonResponse
from rest_framework.response import Response
from cryptography.fernet import MultiFernet, Fernet
import base64
from base64 import b64decode as bd, b64encode as be, urlsafe_b64encode as ube, urlsafe_b64decode as ubd
from crypt_put.models import *
from crypt_account.models import *
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import (
    api_view, throttle_classes, authentication_classes, permission_classes,
    parser_classes
)
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django.views.decorators.csrf import csrf_exempt
import uuid

class OneThousandPerDay(UserRateThrottle):
    rate = '1000/day'

class OncePerDayUserThrottle(UserRateThrottle):
    rate = '1/day'

class OncePerHourUserThrottle(UserRateThrottle):
    rate = '1/hour'

class OncePerMinuteUserThrottle(UserRateThrottle):
    rate = '1/min'


@api_view(['GET',])
@throttle_classes([OncePerHourUserThrottle,])
@authentication_classes([JSONWebTokenAuthentication,])
@permission_classes([IsAuthenticated,])
def key(request):
    return Response({'key': base64.urlsafe_b64encode(Fernet.generate_key()).decode('utf-8')})

@api_view(['POST',])
@parser_classes([JSONParser,])
@throttle_classes([UserRateThrottle,])
@authentication_classes((BasicAuthentication, SessionAuthentication, JSONWebTokenAuthentication))
@permission_classes([IsAuthenticated,])
def get(request):
    salt = request.user.account.salt.encode('ascii')
    pepper = request.data['i'].encode('ascii')
    key = request.user.account.secret.encode('ascii')
    uid = make_uid(salt, pepper, key)
    r = go404(Record, pk=uid)
    data = r.data

    try:
        if( request.data['d'] == '1' ):
            fkeys = [Fernet(key.key) for key in Key.objects.filter(account=request.user.account)]
            data = MultiFernet(fkeys).decrypt(r.data)
    except Exception:
        pass

    return Response({'data': data.decode('utf-8')})

@api_view(['POST',])
@parser_classes([JSONParser,])
@throttle_classes([UserRateThrottle,])
@authentication_classes((BasicAuthentication, SessionAuthentication, JSONWebTokenAuthentication))
@permission_classes([IsAuthenticated,])
def put(request):
    salt = request.user.account.salt.encode('ascii')
    uuid_pepper = uuid.uuid4()
    pepper = str(uuid_pepper).encode('ascii')
    keys = [k.key for k in request.user.account.key_set.all()]
    data = request.data['d'].encode('ascii')
    key = request.user.account.secret.encode('ascii')
    uid = make_uid(salt, pepper, key)
    # if there is a collision, create a new pepper / uid
    while Record.objects.filter(uid=uid).count() > 0:
        uuid_pepper = uuid.uuid4()
        pepper = str(uuid_pepper).encode('ascii')
        uid = make_uid(salt, pepper, key)
    r = Record(uid=uid, data=data)
    r.save(keys=keys)
    return Response({'id': pepper.decode('utf-8')})
