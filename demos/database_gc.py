# Database-GC.py - garbage collection routines to be run against the django DB now and then
#                  this might be called from CRON once in a while, or by hand once a day

#### vvvvvvvvvv THIS SECTION SETS US UP WITHIN THE DJANGO ENVIRONMENT vvvvvvvvvv ####
import os
import sys
django_unusual_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__))+os.sep+'..'+os.sep)
sys.path.append(django_unusual_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = "django_unusual.settings"
#### ^^^^^^^^^^ THIS SECTION SETS US UP WITHIN THE DJANGO ENVIRONMENT ^^^^^^^^^^ ####

import datetime
from django_unusual.models import ColorTemp, Crash

def clean_outdated_crashes():

    print
    print "clean_outdated_crashes() - If a crash hasn't happened in over a week, get rid of it"

    print "before cleaning there are",Crash.objects.count(),"crash records"
    too_old = datetime.datetime.utcnow() - datetime.timedelta(days = 7)
    Crash.objects.filter(last__lte=too_old).delete()
    print "after cleaning there are",Crash.objects.count(),"crash records"

def clean_old_color_temps():

    print
    print "clean_old_color_temps() - Remove ColorTemp records that are more than an hour beyond their freshness date"

    print "before cleaning there are",ColorTemp.objects.count(),"ColorTemp records"
    too_old = datetime.datetime.utcnow() - datetime.timedelta(hours = (ColorTemp.HOW_MANY_HOURS_TO_CARE + 1))
    ColorTemp.objects.filter(created__lte=too_old).delete()
    print "after cleaning there are",ColorTemp.objects.count(),"ColorTemp records"

    ## we want to make sure these things aren't growing out of control
    assert ColorTemp.objects.count() < 1000000000


def main():

    clean_outdated_crashes()

    clean_old_color_temps()

if __name__ == "__main__":
    main()
