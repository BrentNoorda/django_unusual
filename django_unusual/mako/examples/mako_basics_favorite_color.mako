<!DOCTYPE html>
<%!
    ## module-level block - This code is executed only once (per django instance) the first time
    ##                      this page is loaded. Put imports and common functions here, and sometimes
    ##                      globals (but seldom writable globals)

    import datetime

    gColors = { # list colors and their RGB value
        'red' :       { 'rgb':0xFF0000, 'votes': 0 }, # votes will be seen as a bad idea
        'green':      { 'rgb':0x00FF00, 'votes': 0 },
        'blue':       { 'rgb':0x0000FF, 'votes': 0 },
        'black':      { 'rgb':0x000000, 'votes': 0 },
        'white':      { 'rgb':0xFFFFFF, 'votes': 0 },
        'yellow':     { 'rgb':0xFFFF00, 'votes': 0 },
        'purple':     { 'rgb':0xFF00FF, 'votes': 0 },
        'black&blue': { 'rgb':0x000099, 'votes': 0 },
    }

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
<%
    # python code blocks can appear anywhwere, this one will initialize stuff
    popular_color = None

    try:
        favorite_color = request.GET['favorite']
        gColors[favorite_color]['votes'] += 1    # this is bad code because of global stuff
    except:
        pass
%>
<html lang="en">
    <head/>
    <body>

        <p>What is your favorite color now (at ${datetime.datetime.now()})?</p>

        % for k,v in gColors.items():
            <a href="./mako_basics_favorite_color.mako?favorite=${ k | u}"
            style="background-color:${rgbattr(v['rgb'])};color:${rgbattr(v['rgb'] ^ 0xFFFFFF)}">
                ${ k | h}
            </a>
            popularity: ${ v['votes'] }
            <br/>

            <%
                # python code blocks can appear anywhwere, this one checks if color is more popular
                if (popular_color is None) or (gColors[popular_color]['votes'] < v['votes']):
                    popular_color = k
            %>

        % endfor

        <p>This page has been visited ${get_visitor_count()} times.</p>

        % if popular_color is not None:
            <p>The most popular color is ${ popular_color | h }</p>
        % endif

    </body>
</html>
