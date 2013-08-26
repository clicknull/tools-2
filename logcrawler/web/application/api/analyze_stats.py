import logging

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, JSONPRenderer
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, JSONPRenderer
# from rest_framework.authentication import BasicAuthentication
# from rest_framework.permissions import IsAuthenticatedOrReadOnly

from application.models.analyze_stat import AnalyzeStatus


@api_view(['GET'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def get(request):
    params = request.QUERY_PARAMS.dict()
    trans_params = {}
    for key in params:
        trans_key = key
        if key == "start_timestamp":
            trans_key = "start_timestamp__gte"
        elif key == "end_timestamp":
            trans_key = "end_timestamp__lte"
        elif key == "path_include":
            trans_key = "path__contains"
        trans_params[trans_key] = params[key]
    try:
        objs = AnalyzeStatus.objects.filter(**trans_params).order_by("-start_timestamp", "-end_timestamp")
        analyzes = [obj.render_json() for obj in objs]
    except Exception, err:
        logging.error(msg="[get]%s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err), "analyze": []})
    return Response({"status": "ok", "detail": str(params), "analyze": analyzes})


@api_view(['POST'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def create(request):
    params = request.DATA
    try:
        logging.info(msg="create %s" % str(params))
        id = AnalyzeStatus.objects.create(**params).id
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
        logging.info(msg="update analyze: %s" % str(params))
        del params["id"]
        AnalyzeStatus.objects.filter(**primary).update(**params)
    except Exception, err:
        logging.error(msg="update %s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err)})
    return Response({"status": "ok", "detail": str(params)})


@api_view(['GET'])
@renderer_classes((JSONRenderer, JSONPRenderer))
def delete(request):
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
                logging.warn(msg="delete all analyze tasks")
                AnalyzeStatus.objects.all().delete()
            else:
                logging.warn(msg="delete analyze: %s" % str(params))
                AnalyzeStatus.objects.filter(**trans_params).delete()
        else:
            return Response({"status": "nok", "detail": "parametre lacked"})
    except Exception, err:
        logging.error(msg="[delete]%s error occur: %s" % (str(params), err))
        return Response({"status": "nok", "detail": str(err)})
    return Response({"status": "ok", "detail": str(params)})


class AnalyzeStatsView(APIView):

    renderer_classes = (JSONRenderer, JSONPRenderer)
    # authentication_classes = (BasicAuthentication, )
    # permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request):
        """Read"""
        pass

    def post(self):
        """Create"""
        pass

    def put(self):
        """Update"""
        pass

    def delete(self):
        """Delete"""
        pass

