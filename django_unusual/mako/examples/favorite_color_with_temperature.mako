<!DOCTYPE html>
<%!
    ## module-level block - This code is executed only once (per django instance) the first time
    ##                      this page is loaded. Put imports and common functions here, and sometimes
    ##                      globals (but seldom writable globals)

    import datetime
    import lib.oakland_weather

    gColors = { # list colors and their RGB value
        'red' :       { 'rgb':0xFF0000, 'temperatures': [] }, # global temperature will be seen as a bad idea
        'green':      { 'rgb':0x00FF00, 'temperatures': [] },
        'blue':       { 'rgb':0x0000FF, 'temperatures': [] },
        'black':      { 'rgb':0x000000, 'temperatures': [] },
        'white':      { 'rgb':0xFFFFFF, 'temperatures': [] },
        'yellow':     { 'rgb':0xFFFF00, 'temperatures': [] },
        'purple':     { 'rgb':0xFF00FF, 'temperatures': [] },
        'black&blue': { 'rgb':0x000099, 'temperatures': [] },
    }

    def rgbattr(rgb):   # return HTML friendly version of color
        ret = '%X' % (rgb & 0xFFFFFF)
        while len(ret) < 6:
            ret = '0' + ret
        return '#' + ret

    visitor_count = 0   # this is a global where we count how many times anyone has visited this
                        # page - this is BAD CODE because of restarts, multiple
                        # processes or forks, and in-process concurrency

    def get_visitor_count():    # BAD CODE, because of the global stuff mentioned above
        global visitor_count
        visitor_count += 1
        return visitor_count

    def get_previous_favorite(request):    # get prevous favorite of this user, or None
        try:
            return request.session['favorite_color']
        except:
            return None

    def set_previous_favorite(request,favorite_color):
        request.session['favorite_color'] = favorite_color
%>
<%
    # python code blocks can appear anywhwere, this one will initialize stuff
    popular_color = None

    previous_favorite = get_previous_favorite(request)

    if 'favorite' in request.GET:
        favorite_color = request.GET['favorite']
        current_temperature = lib.oakland_weather.get_current_oakland_weather(extra_delay=5,default=72)
        gColors[favorite_color]['temperatures'].append(current_temperature)
        set_previous_favorite(request,favorite_color)
    else:
        favorite_color = None
%>
<html lang="en">
    <head/>
    <body>

        % if favorite_color is not None:
            <p>You selected ${ favorite_color | h } and the temperature was ${current_temperature}.</p>
            ## any line starting with a '##' is a comment, other than pointing that out I
            ## had no real reason to put this comment here
        % endif

        <p>Your previous favorite was ${ previous_favorite }.</p>

        <p>What is your favorite color now (at ${datetime.datetime.now()})?</p>

        <table border="1">
            <tr><td>color</td><td>popularity</td><td>avg. temp</td></tr>
            % for name,v in gColors.items():
                <tr>
                    <td style="background-color:${ rgbattr(v['rgb'] )}">
                        <a href="./favorite_color_with_temperature.mako?favorite=${ name | u}" style="color:${rgbattr(v['rgb'] ^ 0xFFFFFF)}">
                            ${ name | h}
                        </a>
                    </td>
                    <td>
                        ${ len(v['temperatures']) }
                    </td>
                    <td>
                        % if len(v['temperatures']) == 0:
                            <span style="color:#bbb">n/a</span>
                        % else:
                            <%
                                total_temp = 0
                                for temp in v['temperatures']:
                                    total_temp += temp
                            %>
                            ${ total_temp / len(v['temperatures'])}
                        % endif
                    </td>

                    <%
                        # python code blocks can appear anywhwere, this one checks if color is more popular
                        if (popular_color is None) or (len(gColors[popular_color]['temperatures']) < len(v['temperatures'])):
                            popular_color = name
                    %>
                </tr>
            % endfor
        </table>

        <p>This page has been visited ${get_visitor_count()} times.</p>

        % if popular_color is not None:
            <p>The most popular color is ${ popular_color | h }</p>
        % endif

        <%include file="example_footer.include" args="allRights=False"/>

    </body>
</html>
