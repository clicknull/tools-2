#coding: UTF-8

import glob
import gzip
import json
import logging
import os
import re
import socket
import time
import urllib2
import uuid
from datetime import datetime

from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.renderers import JSONRenderer, JSONPRenderer
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

#from celerytest.tasks import analyze_process_by_regexp
from application.models.analyze_rule import AnalyzeRule

DOWNLOAD_URL = "http://traceall.funshion.com/_logcrawler/all_merged_gz/"
KAFKA_URL = "kafka://192.168.111.215:9092/"


@api_view(['GET'])
@renderer_classes((JSONRenderer, JSONPRenderer))
@authentication_classes((BasicAuthentication, ))
@permission_classes((IsAuthenticatedOrReadOnly, ))
def get(request):
    params = request.QUERY_PARAMS.dict()
    try:
        objs = AnalyzeRule.objects.filterX(**params)
        rules = [obj.render_json() for obj in objs]
    except Exception, err:
        logging.error(msg="[get]%s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err), "rule": []})
    return Response({"status": "ok", "detail": str(params), "rule": rules})


@api_view(['POST'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def create(request):
    params = request.DATA
    try:
        if not support_regexp(params["regexp"]):
            return Response({"status": "nok", "detail": "regexp not support", "id": 0})
        if "dealwith_manner" not in params:
            params["dealwith_manner"] = "onserver"
        parametersdict = calculate_parameters(params)
        params["parameters"] = json.dumps(obj=parametersdict)
        logging.info(msg="create analyze rule: %s" % str(params))

        id = AnalyzeRule.objects.createX(**params).id
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

        if not support_regexp(params["regexp"]):
            return Response({"status": "nok", "detail": "regexp not support", "id": 0})
        if "dealwith_manner" not in params:
            params["dealwith_manner"] = "onserver"
        parametersdict = calculate_parameters(params)
        params["parameters"] = json.dumps(obj=parametersdict)
        logging.info(msg="update analyze rule: %s" % str(params))

        del params["id"]
        # DateTimeField(auto_now=True) only works when use save()
        # The update() method does not call any save() methods on your models
        # Thus, datetime_now should be valued when use update() instead of save()
        params["timestamp"] = datetime.now()
        AnalyzeRule.objects.updateX(coordinate=primary, **params)
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
                logging.warn(msg="delete all analyze rules")
                Analyze_rule.objects.deleteX(coordinate={})
            else:
                logging.warn(msg="delete analyze rule: %s" % str(params))
                AnalyzeRule.objects.deleteX(coordinate=params)
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
        else:
            options = AnalyzeRule.objects.get_value_list(key)
            options.sort()
    except Exception, err:
        logging.error(msg="[getoptions]%s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err), "options": []})
    return Response({"status": "ok", "detail": str(params), "options": options})


def support_regexp(reg):
    checktag = ".*"
    str_before_checktag = reg.split(checktag)[0]
    for char in str_before_checktag:
        if char.isalnum():
            return True
    return False


def calculate_parameters(params):
    if "topic" in params:
        topic = params["topic"]
        del params["topic"]
    else:
        topic = "%(service_name)s_%(IDC_name)s_" % params
        regexp = params["regexp"]
        topic += "".join(char if char.isalnum() else "_" for char in list(regexp))  # hash here

    if "download_url" in params:
        download_url = params["download_url"]
        del params["download_url"]
    else:
        download_url = DOWNLOAD_URL

    if "kafka_url" in params:
        kafka_url = params["kafka_url"]
        del params["kafka_url"]
    else:
        kafka_url = KAFKA_URL

    parametersdict = {"topic": topic}
    if params["dealwith_manner"].find("onserver") != -1:
        parametersdict["download_url"] = download_url + topic + "/"
    if params["dealwith_manner"].find("sendtokafka") != -1:
        parametersdict["kafka_url"] = kafka_url
    return parametersdict


@api_view(['GET'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def verify_get(request):
    """
    EXP:
    params = {
        "pid": 12345,
        "file_offset": 0,
        "request_lines" 30
    }
    """
    params = request.QUERY_PARAMS.dict()
    try:
        pid = params["pid"]
        fid = open("/tmp/%s" % (pid,), 'r')
        file_offset = int(params["file_offset"])
        result_lines = []
        response_lines = 0
        request_lines = int(params["request_lines"])
        counter = 0
        for line in fid:
            counter += 1
            if counter >= file_offset:
                response_lines += 1
                result_lines.append(line)
                if request_lines == response_lines:
                    break
        result = {
            "pid": pid,
            "current_offset": counter + 1,  # 本次读完日志之后当前的文件偏移量
            "response_lines": response_lines,  # 本次实际读取到的条数
            "lines": result_lines
        }

        result["status"] = "ok"
        result["detail"] = str(params)
    except Exception, err:
        logging.error(msg="verify_get %s error occur: %s" % (str(params), err))
        result = {"status": "nok", "detail": str(err)}
    finally:
        return Response(result)


@api_view(['POST'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def verify_create(request):
    """
    EXP:
    params = {
        "IDC_name": "HeNan_ZhengZhou_CNC",
        "IDC_ip_address_port": "182.118.38.15:80",
        "service_name": "haproxy_access",
        "regexp": "sso.funshion.com*"
    }
    """
    params = request.DATA
    try:
        pid = uuid.uuid1().hex
        celerytask = analyze_process_by_regexp.delay(params["IDC_name"],params["service_name"],params["regexp"],pid)
        result = {
            "pid": pid,
            "celerytaskid": celerytask.id
        }
        result["status"] = "ok"
        result["detail"] = str(params)
    except Exception, err:
        logging.error(msg="verify_create %s error occur: %s" % (str(params), err))
        result = {"status": "nok", "detail": str(err)}
    finally:
        return Response(result)

