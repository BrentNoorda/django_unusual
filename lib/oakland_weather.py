# scrape yahoo weather page for current oakland weather. This is sure to break
# anytime yahoo changes its weather page

import re
import time
import random
import requests

OAKLAND_WEATHER_URL = 'http://weather.yahoo.com/united-states/california/oakland-12797399/'
URL_THAT_WILL_SURELY_FAIL = "http://weather.yahoo.commie/blah"
TEMPERATURE_REGEXP = r'<div class="day-temp-current temp-f ">(\d+)&'

def get_current_oakland_weather(extra_delay=0,fail_sometimes_on_purpose=False,default=None):

    try:

        if extra_delay != 0:
            time.sleep(extra_delay)

        url = OAKLAND_WEATHER_URL

        if fail_sometimes_on_purpose:
            if 0 == random.randint(0,3):    # fail 33% of the time on purpose
                url = URL_THAT_WILL_SURELY_FAIL

        html = requests.get(url,timeout=5.0)
        html.raise_for_status()
        match = re.search(TEMPERATURE_REGEXP,html.content)
        return int(match.group(1))

    except:
        if default is None:
            raise
        else:
            return default



if __name__ == '__main__':

    print get_current_oakland_weather(extra_delay=0,fail_sometimes_on_purpose=False)
