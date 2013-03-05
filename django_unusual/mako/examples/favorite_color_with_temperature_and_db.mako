<!DOCTYPE html>
<%!
    ## module-level block - This code is executed only once (per django instance) the first time
    ##                      this page is loaded. Put imports and common functions here, and sometimes
    ##                      globals (but seldom writable globals)

    import datetime
    import lib.oakland_weather
    from django_unusual.models import ColorTemp

    gColorRGBs = { # list known colors and their RGB
        'red' :       0xFF0000,
        'green':      0x00FF00,
        'blue':       0x0000FF,
        'black':      0x000000,
        'white':      0xFFFFFF,
        'yellow':     0xFFFF00,
        'purple':     0xFF00FF,
        'black&blue': 0x000099,
    }

    def rgbattr(rgb):   # return HTML friendly version of color
        ret = '%X' % (rgb & 0xFFFFFF)
        while len(ret) < 6:
            ret = '0' + ret
        return '#' + ret

    def get_total_votes():    # total vote count for the past hour
        too_old_to_care = datetime.datetime.utcnow() - datetime.timedelta(hours = ColorTemp.HOW_MANY_HOURS_TO_CARE)
        return ColorTemp.objects.filter(created__gt = too_old_to_care).count()

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
        current_temperature = lib.oakland_weather.get_current_oakland_weather(fail_sometimes_on_purpose=True)
        set_previous_favorite(request,favorite_color)

        # store this color in the db at this time
        ColorTemp(created=datetime.datetime.utcnow(),color=favorite_color,temperature=current_temperature).save()
    else:
        favorite_color = None

    # load up all the colors into colorCounts dict by name, where each entry
    # has these fields based on data received in the past hour
    #  'total' : how many of these were selected in the past hour
    #  'totalTemp' : add up the temperature at each selected time in the past hour
    colorCounts = { }
    too_old_to_care = datetime.datetime.utcnow() - datetime.timedelta(hours = ColorTemp.HOW_MANY_HOURS_TO_CARE)
    for ct in ColorTemp.objects.filter(created__gt = too_old_to_care):
        try:
            colorCounts[ct.color]['total'] += 1
            colorCounts[ct.color]['totalTemp'] += ct.temperature
        except:
            colorCounts[ct.color] = { 'total':1, 'totalTemp':ct.temperature }
%>
<html lang="en">
    <head/>
    <body>

        % if favorite_color is not None:
            <p>You selected <span style="color:${rgbattr(gColorRGBs[favorite_color])}">${ favorite_color | h }</span> and the temperature was ${current_temperature}.</p>
            ## any line starting with a '##' is a comment, other than pointing that out I
            ## had no real reason to put this comment here
        % endif

        <p>Your previous favorite was ${ previous_favorite }.</p>

        <p>What is your favorite color now (at ${datetime.datetime.now()})?</p>

        <table border="1">
            <tr><td>color</td><td>hourly popularity</td><td>avg. temp</td></tr>
            % for name,rgb in gColorRGBs.items():
                <tr>
                    <td style="background-color:${ rgbattr(rgb) }">
                        <a href="./favorite_color_with_temperature_and_db.mako?favorite=${ name | u}" style="color:${rgbattr(rgb ^ 0xFFFFFF)}">
                            ${ name | h}
                        </a>
                    </td>
                    <td>
                        ${ colorCounts[name]['total'] if (name in colorCounts) else 0 }
                    </td>
                    <td>
                        % if name not in colorCounts:
                            <span style="color:#bbb">n/a</span>
                        % else:
                            ${ colorCounts[name]['totalTemp'] / colorCounts[name]['total'] }
                            <%
                                # python code blocks can appear anywhwere, this one checks if color is more popular
                                if (popular_color is None) or (colorCounts[popular_color]['total'] < colorCounts[name]['total']):
                                    popular_color = name
                            %>
                        % endif
                    </td>

                </tr>
            % endfor
        </table>

        <p>There have been ${get_total_votes()} votes in the past hour.</p>

        % if popular_color is not None:
            <p>The most popular color is ${ popular_color | h }</p>
        % endif

        <%include file="example_footer.include" args="allRights=False"/>

    </body>
</html>
