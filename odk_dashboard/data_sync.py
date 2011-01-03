import re
from django.utils import simplejson
from django.shortcuts import render_to_response
from djangomako import shortcuts
from django.db.models import Avg, Max, Min, Count
from django.http import HttpResponse
from odk_dropbox import utils
from odk_dropbox.models import Form
from .models import ParsedInstance, Phone
import datetime

def map_data(request, stamp):
    """
    Returns JSON with a stamp to ensure most recent data is sent.
    pis = ParsedInstance.objects.exclude(location__gps=None)
    for ps in pis:
        pcur = {}
        if ps.location.gps:
            pcur['images'] = [x.image.url for x in ps.instance.images.all()]
            pcur['phone'] = ps.phone.__unicode__()
            pcur['date'] = ps.end.strftime("%Y-%m-%d %H:%M")
            pcur['survey_type'] = ps.survey_type.name
            pcur['gps'] = ps.location.gps.to_dict()
            pcur['title'] = ps.survey_type.name
        psubs.append(pcur)
    cur_stamp = model_stamp(ParsedInstance)
    """
    psubs = []
    return stamped_json_output(cur_stamp, psubs, True)

from ipdb import set_trace as debug

def activity_list(request, stamp):
    if stamp_up_to_date(ParsedInstance, stamp):
        return HttpResponse(simplejson.dumps("OK"))
    else:
        try:
            stamp_data = simplejson.loads(stamp)
            latest = stamp_data['latest']
            instance_list = ParsedInstance.objects.exclude(location__gps=None).filter(id__gte=latest)
            flush = False
        except:
            instance_list = ParsedInstance.objects.exclude(location__gps=None)
            flush = True

        return stamped_json_output(stamp=model_stamp(ParsedInstance), \
                data=[pi.to_dict() for pi in instance_list], \
                flush=flush)

def stamp_up_to_date(model, stamp):
    return model_stamp(model)==stamp

def model_stamp(model):
    latest_id = model.objects.order_by('-id')[0].id
    count = model.objects.count()
    return "{'count':%s,'latest':%s}" % (count, latest_id)

def stamped_json_output(stamp, data, flush):
    return HttpResponse(simplejson.dumps({'stamp':stamp, \
                        'data':data, 'flush':flush }))