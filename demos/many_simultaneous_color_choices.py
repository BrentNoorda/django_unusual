# simulate many many users hitting the url: http://192.168.0.199:8000/examples/favorite_color_with_temperature.mako?favorite=purple

TEST_URL = "http://192.168.0.199:8000/examples/favorite_color_with_temperature.mako?favorite=purple"

gConnectionCount = 0

import gevent.monkey; gevent.monkey.patch_all()
import sys
import time
import requests

def the_test(idx):
    global gConnectionCount

    try:
        r = requests.get(TEST_URL,timeout=90)
        r.raise_for_status()

        assert -1 != r.content.find("Salmonella Enterprises")

    except Exception, err:
        print "ERROR MAKING CONNECTION",idx,err

    gConnectionCount -= 1

def simultest(simulcount):
    global gConnectionCount

    print "test URL for %d users" % simulcount

    for i in xrange(simulcount):
        gConnectionCount += 1
        gevent.Greenlet( the_test, i ).start()

    start_time = time.time()
    while 0 < gConnectionCount:
        print "%d connections waiting for response" % gConnectionCount
        sys.stdout.flush()
        time.sleep(1)
    end_time = time.time()

    print "test of",simulcount,"requests ran for",(end_time-start_time),"seconds"

def main():

    try:
        simulcount = long(sys.argv[1])
        assert str(simulcount) == sys.argv[1]
    except:
        print "python many_simultaneous_color_choices.py [simultatenous_user_count]"
        print "EXAMPLE: python many_simultaneous_color_choices.py 500"
    else:
        simultest(simulcount)

if __name__ == "__main__":
    main()

