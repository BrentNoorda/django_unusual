import os
import codecs
import socket
import markdown
from django.http import HttpResponse
import django_unusual.settings

import logging
logger = logging.getLogger(__name__)

import mako
import mako.lookup

# Mako Template Lookup to find files in /mako directory and stores the compiled code
# into /tmp/mako_modules, and do other settings for DEBUG versus DEPLOY
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


def show_markdown_page(request,filename):

    try:
        # turn into real file, and make sure no cheating is going on
        normparent = os.path.normpath(django_unusual.settings.PROJECT_PATH + os.sep + '..') + os.sep
        filespec = os.path.normpath(normparent + filename)
        if not filespec.startswith(normparent):
            # no cheating allowed by trying to read another path
            raise Exception("cannot look there at " + filespec )


        input_file = codecs.open(filespec, mode="r", encoding="utf-8")
        text = input_file.read()
        input_file.close()
        html = markdown.markdown(text,extensions=['nl2br'],output_format="html5")

        html = ( '<!DOCTYPE html>\r\n'
                 '<html>\r\n'
                 '<head>\r\n'
                 '<style type="text/css">\r\n'      # /path-slash-ok/
                 'body pre {\r\n'
                 '  background-color: #f8f8f8;\r\n'
                 '  border: 1px solid #ccc;\r\n'
                 '  font-size: 12px;\r\n'
                 '  line-height: 19px;\r\n'
                 '  overflow: auto;\r\n'
                 '  padding: 6px 10px;\r\n'
                 '  border-radius: 3px;\r\n'
                 '}\r\n'
                 '#markdown-body {\r\n'
                 '  background-color: #fff;\r\n'
                 '  border: 1px solid #CACACA;\r\n'
                 '  padding: 30px;\r\n'
                 '  margin: 10px\r\n'
                 '}\r\n'
                 '</style>\r\n'
                 '</head>\r\n'
                 '<body><div id="markdown-body">\r\n' ) + (
                 html ) + (
                 '</div></body>\r\n'
                 '</html>' )

        html = html.replace('MY_IP_ADDRESS',socket.gethostbyname(socket.gethostname()))

        response = HttpResponse(html,content_type="text/html")
        response['Cache-Control'] = 'no-cache'

    except Exception, err:
        print "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
        response = HttpResponse()
        if django_unusual.settings.DEBUG:
            logger.exception(err)
            response = HttpResponse(err)
        else:
            response = HttpResponse("Server Error - Sorry")

    return response
