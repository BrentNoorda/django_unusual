import os
from django.http import HttpResponse
import django_unusual.settings

import logging
logger = logging.getLogger(__name__)

import mako

MakoTemplateLookup = mako.lookup.TemplateLookup(
    directories=[os.path.normpath(django_unusual.settings.PROJECT_PATH+'/mako')],
    module_directory=os.path.normpath(django_unusual.settings.PROJECT_PATH + '/tmp/mako_modules'),
    filesystem_checks=django_unusual.settings.DEBUG,
    output_encoding='utf-8', encoding_errors='replace',
    strict_undefined=django_unusual.settings.DEBUG )


def show_mako_page(request,filename):
    response = HttpResponse()
    logger.info('show_mako_page:'+filename)
    try:

        template = MakoTemplateLookup.get_template( filename )
        html = template.render(request=request,response=response,logger=logger)
        if response.status_code == 200:  # if not 200 then something internally has changed the response code
            response.content = html

    except: # Exception, err:
        if django_unusual.settings.DEBUG:
            logger.exception(str(mako.exceptions.html_error_template().render()))
            response.content = mako.exceptions.html_error_template().render()
        else:
            response = HttpResponse("Server Error - Sorry")

    return response
