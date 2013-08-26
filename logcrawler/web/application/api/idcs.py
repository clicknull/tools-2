import logging
from datetime import datetime

from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.renderers import JSONRenderer, JSONPRenderer
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# from rest_framework.views import APIView
# from django.shortcuts import render_to_response

from application.models.idc import IDCConfig


@api_view(['GET'])
@renderer_classes((JSONRenderer, JSONPRenderer))
@authentication_classes((BasicAuthentication, ))
@permission_classes((IsAuthenticatedOrReadOnly, ))
def get(request):
    ## To fix bug of connection in django1.5
    # import django
    # django.db.connection.close()
    ##
    params = request.QUERY_PARAMS.dict()
    try:
        objs = IDCConfig.objects.filter(**params)
        idc_collects = [obj.render_json() for obj in objs]
    except Exception, err:
        logging.error(msg="[get]%s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err), "idc_collect": []})
    return Response({"status": "ok", "detail": str(params), "idc_collect": idc_collects})


@api_view(['POST'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def create(request):
    params = request.DATA
    try:
        logging.info(msg="create %s" % str(params))
        id = IDCConfig.objects.create(**params).id
    except Exception, err:
        logging.error(msg="create %s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err), "id": 0})
    return Response({"status": "ok", "detail": str(params), "id": id})


@api_view(['POST'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def update(request):
    params = request.DATA
    try:
        primary = {
            "id": params["id"],
        }
        logging.info(msg="update idc_collect: %s" % str(params))
        del params["id"]
        # DateTimeField(auto_now=True) only works when use save()
        # The update() method does not call any save() methods on your models
        # Thus, datetime_now should be valued when use update() instead of save()
        params["timestamp"] = datetime.now()
        IDCConfig.objects.filter(**primary).update(**params)
    except Exception, err:
        logging.error(msg="update %s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err)})
    return Response({"status": "ok", "detail": str(params)})


@api_view(['GET'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def delete(request):
    params = request.QUERY_PARAMS.dict()
    try:
        if params:
            if "all" in params and params["all"] == "true":
                logging.warn(msg="delete all idc_collect settings")
                IDCConfig.objects.all().delete()
            else:
                logging.warn(msg="delete idc_collect setting: %s" % str(params))
                IDCConfig.objects.filter(**params).delete()
        else:
            return Response({"status": "nok", "detail": "parametre lacked"})
    except Exception, err:
        logging.error(msg="[delete]%s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err)})
    return Response({"status": "ok", "detail": str(params)})


@api_view(['GET'])
@renderer_classes((JSONRenderer, JSONPRenderer))
@authentication_classes((BasicAuthentication, ))
@permission_classes((IsAuthenticatedOrReadOnly, ))
def getoptions(request):
    params = request.QUERY_PARAMS.dict()
    try:
        key = params["type"]
        if key == "status":
            options = ["active", "inactive"]
        elif key == "current_status":
            options = ["online", "offline"]
        else:
            options = list(IDCConfig.objects.values_list(key, flat=True).distinct())
            options.sort()
    except Exception, err:
        logging.error(msg="[getoptions]%s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err), "options": []})
    return Response({"status": "ok", "detail": str(params), "options": options})
