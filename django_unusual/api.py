import json
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from django.utils.importlib import import_module
from django.conf import settings
from django.http import HttpResponse
from lib.do_over import do_over
import lib.oakland_weather
import django_unusual.models

import logging
logger = logging.getLogger(__name__)

# wrapper to get session from 'sessionid' for api functions
# from http://djangosnippets.org/snippets/1667/
def session_from_http_header_or_params(view_func):
    @wraps(view_func)
    def decorated(request, *args, **kwargs):
        engine = import_module(settings.SESSION_ENGINE)
        session_key = request.GET.get('sessionid', None)
        if session_key is None:
            session_key = request.POST.get('sessionid', None)
            if session_key is None:
                session_key = request.META.get('HTTP_SESSIONID', None)
        if session_key is not None:
            request.session = engine.SessionStore(session_key)
        return view_func(request, *args, **kwargs)
    return decorated

def add_cross_site_headers(response):
    # from http://stackoverflow.com/questions/1099787/jquery-ajax-post-sending-options-as-request-method-in-firefox
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response['Access-Control-Max-Age'] = 60 * 60 * 4
    # note that '*' is not valid for Access-Control-Allow-Headers
    response['Access-Control-Allow-Headers'] = 'origin, x-csrftoken, content-type, accept, sessionid'

# wrapper for any functions that allow cross-site scripts
def allow_cross_site(view_func):
    @wraps(view_func)
    def decorated(request, *args, **kwargs):
        if request.method == 'OPTIONS':
            # from http://stackoverflow.com/questions/1099787/jquery-ajax-post-sending-options-as-request-method-in-firefox
            response = HttpResponse()
        else:
            response = view_func(request, *args, **kwargs)
        add_cross_site_headers(response)
        return response
    return decorated

####################################### API CALLS #######################################

@csrf_exempt
@session_from_http_header_or_params
@allow_cross_site
def api_get_temperature(request):
    # called with a single parameter "city" which is the name of the city
    # if that's not "oakland" this will return an error

    try:
        getter = request.POST if request.POST else request.GET # i don't care if it's get or post
        city = getter.get('city','?')

        if city != 'oakland':
            ret = { 'code': 1, 'data': 'unknown city' }
        else:
            current_temperature = do_over( lambda x: lib.oakland_weather.get_current_oakland_weather(), logger=logger )
            ret = { 'code': 0,
                    'data': { 'temperature': current_temperature } }
    except Exception, err:
        django_unusual.models.Crash.record(request=request,label="ERROR ON api_get_temperature",details=unicode(err))
        ret = { 'code': 1, 'data': 'error unknown city' }

    return HttpResponse( json.dumps(ret,separators=(',',':')), mimetype='application/json' )
