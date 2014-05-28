import logging

from rest_framework.decorators import api_view, renderer_classes, parser_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, JSONPRenderer, XMLRenderer
from rest_framework.parsers import JSONParser, XMLParser
# from rest_framework.authentication import BasicAuthentication
# from rest_framework.permissions import IsAuthenticatedOrReadOnly

from application.models.crawl_stat import CrawlStatus


@api_view(['GET'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def oldget(request):
    params = request.QUERY_PARAMS.dict()
    trans_params = {}
    for key in params:
        trans_key = key
        if key == "start_timestamp":
            trans_key = "start_timestamp__gte"
        elif key == "end_timestamp":
            trans_key = "end_timestamp__lte"
        elif key == "url_include":
            trans_key = "url__contains"
        trans_params[trans_key] = params[key]
    try:
        objs = CrawlStatus.objects.filter(**trans_params).order_by("-start_timestamp", "-end_timestamp")
        downloads = [obj.render_json() for obj in objs]
    except Exception, err:
        logging.error(msg="[get]%s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err), "download": []})
    return Response({"status": "ok", "detail": str(params), "download": downloads})


@api_view(['POST'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def oldcreate(request):
    params = request.DATA
    try:
        logging.info(msg="create %s" % str(params))
        id = CrawlStatus.objects.create(**params).id
    except Exception, err:
        logging.error(msg="create %s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err), "id": 0})
    return Response({"status": "ok", "detail": str(params), "id": id})


@api_view(['POST'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def oldupdate(request):
    params = request.DATA
    try:
        primary = {
            "id": params["id"],
        }
        logging.info(msg="update download: %s" % str(params))
        del params["id"]
        CrawlStatus.objects.filter(**primary).update(**params)
    except Exception, err:
        logging.error(msg="update %s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err)})
    return Response({"status": "ok", "detail": str(params)})


@api_view(['GET'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def olddelete(request):
    params = request.QUERY_PARAMS.dict()
    trans_params = {}
    for key in params:
        trans_key = key
        if key == "start_timestamp":
            trans_key = "start_timestamp__gte"
        elif key == "end_timestamp":
            trans_key = "end_timestamp__lte"
        trans_params[trans_key] = params[key]
    try:
        if trans_params:
            if "all" in trans_params and trans_params["all"] == "true":
                logging.warn(msg="delete all download tasks")
                CrawlStatus.objects.all().delete()
            else:
                logging.warn(msg="delete download: %s" % str(params))
                CrawlStatus.objects.filter(**trans_params).delete()
        else:
            return Response({"status": "nok", "detail": "parametre lacked"})
    except Exception, err:
        logging.error(msg="[delete]%s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err)})
    return Response({"status": "ok", "detail": str(params)})


# --
# new REST
# --

class CrawlStatuses(APIView):

    # for all supported renderer of this class, to render response
    # according to HTTP-HEAD-Accept or url.suffix.
    # use url.suffix first, then Accept.
    # if the two not match, raise exception(use first of renderer_classes).
    # if url.suffix empty, use Accept in renderer_classes or raise exception(use first of renderer_classes).
    # if both empty, use default Accept in first of renderer_classes or raise exception.
    renderer_classes = (JSONRenderer, JSONPRenderer, XMLRenderer)

    # parser class used to parse request
    # if empty, use default in rest_framework.settings
    # if HTTP-HEAD-content_type not in parser_classes, raise exception
    parser_classes = (JSONParser, XMLParser)

    # authentication_classes = (BasicAuthentication, )
    # permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request, format=None):
        """Read"""
        return Response({"status": "ok", "detail": "not support yet"})

    def post(self, request, format=None):
        """Create"""
        return Response({"status": "ok", "detail": "not support yet"})

    def put(self, request, format=None):
        """Update"""
        return Response({"status": "ok", "detail": "not support yet"})

    def delete(self, request, format=None):
        """Delete"""
        return Response({"status": "ok", "detail": "not support yet"})


@api_view(['GET'])
@renderer_classes((JSONRenderer, JSONPRenderer, XMLRenderer))
@parser_classes((JSONParser, XMLParser))
def show(request, format=None):
    return Response({"status": "ok", "detail": "not support yet"})
