# simulate many many users hitting the url: http://192.168.0.199:8000/examples/favorite_color_with_temperature.mako?favorite=purple

TEST_URL = "http://127.0.0.1:8000/examples/favorite_color_with_temperature.mako?favorite=purple"

gConnectionCount = 0

import gevent.monkey; gevent.monkey.patch_all()
import re
import sys
import time
import requests

MEMORY_REGEXP = r'pid:(\d+) - mem:([\d\.]+)MB'
pid_memory_map = { }   # will build dictionary of how much memory each pid is using

def the_test(idx,unique_str):
    global gConnectionCount
    global pid_memory_map

    try:
        #print "1",TEST_URL+'&v='+unique_str
        r = requests.get(TEST_URL+'&v='+unique_str,timeout=90)
        #print "2",TEST_URL+'&v='+unique_str
        r.raise_for_status()

        assert -1 != r.content.find("Salmonella Enterprises")

        match = re.search(MEMORY_REGEXP,r.content)
        pid = int(match.group(1))
        mem_use = float(match.group(2))

        if pid in pid_memory_map:
            pid_memory_map[pid] = max(mem_use,pid_memory_map[pid])
        else:
            pid_memory_map[pid] = mem_use

    except Exception, err:
        print "ERROR MAKING CONNECTION",idx,err

    gConnectionCount -= 1

def simultest(simulcount):
    global gConnectionCount

    print "test URL for %d users" % simulcount

    unique_str = str(time.time())
    for i in xrange(simulcount):
        gConnectionCount += 1
        gevent.Greenlet( the_test, i, unique_str + '.' + str(i) ).start()

    start_time = time.time()
    while 0 < gConnectionCount:
        print "%d connections waiting for response" % gConnectionCount
        sys.stdout.flush()
        time.sleep(1)
    end_time = time.time()

    print "test of",simulcount,"requests ran for",(end_time-start_time),"seconds"
    #print "server process is using about",max_memory,"MB"
    total_mem_use = 0
    for pid,mem_use in pid_memory_map.items():
        total_mem_use += mem_use
    print ( "server ran %d process%s using a total %0.02fMB memory"
          % (len(pid_memory_map),'' if (len(pid_memory_map)==0) else 'es',total_mem_use) )
    #print
    #print pid_memory_map

def main():

    try:
        simulcount = long(sys.argv[1])
        assert str(simulcount) == sys.argv[1]
    except:
        print "python many_simultaneous_color_choices.py [simultatenous_user_count]"
        print "EXAMPLE: python many_simultaneous_color_choices.py 50"
    else:
        simultest(simulcount)

if __name__ == "__main__":
    main()

