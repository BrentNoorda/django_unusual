<!DOCTYPE html>
<%!
    ## module-level block - This code is executed only once (per django instance) the first time
    ##                      this page is loaded. Put imports and common functions here, and sometimes
    ##                      globals (but seldom writable globals)

    import datetime

    gColors = [ # list colors and their RGB value
        { 'name':'red',         'rgb':0xFF0000,     'votes': 0 }, # votes will be seen as a bad idea
        { 'name':'green',       'rgb':0x00FF00,     'votes': 0 },
        { 'name':'blue',        'rgb':0x0000FF,     'votes': 0 },
        { 'name':'black',       'rgb':0x000000,     'votes': 0 },
        { 'name':'white',       'rgb':0xFFFFFF,     'votes': 0 },
        { 'name':'yellow',      'rgb':0xFFFF00,     'votes': 0 },
        { 'name':'purple',      'rgb':0xFF00FF,     'votes': 0 },
        { 'name':'black&blue',  'rgb':0x000099,     'votes': 0 },
    ]

    def rgbattr(rgb):   # return HTML friendly version of color
        ret = '%X' % (rgb & 0xFFFFFF)
        while len(ret) < 6:
            ret = '0' + ret
        return '#' + ret

    visitor_count = 0   # this is a global where we count how many times anyone has visited this
                        # page - this is a really bad idea because of restartes, multiple
                        # processes or forks, and in-processconcurrency

    def get_visitor_count():    # bad code, because of the global stuff mentioned above
        global visitor_count
        visitor_count += 1
        return visitor_count

%>
<html lang="en">
  <head/>
  <body>

    <p>What is your favorite color now (at ${datetime.datetime.now()})?</p>

    % for color in gColors:
      <a href="./mako_basics_favorite_color.mako?favorite=${ color['name'] | u}"
       style="background-color:${rgbattr(color['rgb'])};color:${rgbattr(color['rgb'] ^ 0xFFFFFF)}">
        ${ color['name'] | h}
      </a>
      <br/>
    % endfor

    <p>This page has been visited ${get_visitor_count()} times.</p>

  </body>
</html>
