# do_over - method to help calling things that are expected to fail

import sys
import time
import random

############################################## DO_OVER ###########################################

"""
do_over - utility function for calling a function that might possibly fail a few times, such
          as when making a call to a server that might hiccup

method do_over( func, retryWaits = _DEFAULT_RETRY_WAITS,
                cookie_obj = None, retry_alert = None )
    func = func to call that performs whatever is the action - function must accept argument (cookie_obj)
           if this function throws an error then that starts retry stuff happening
    retryWaits = an array of how long to wait between each retry attempt. some randomness will be thrown in to prevent
                 deadlockingishness between servers
                 Example:  retryWaits = [ 500, 1500, 3000 ]
    cookie_obj = variable that will be passed to func and to retry_alert
    retry_alert = function called when try has failed, before sleep and retry, given parameters (cookie_obj,attempts,retry_wait_total,errType,errValue,errTraceback)
                  attempts is how many times it has tried already
                  this function should return True to keep trying, and False to give up with the original error (or throw its own error)
"""

# with these default it will call at times (approximately) 0, 500, 2000, 5000, 11000, 21000, 31000, 41000, 51000, 61000 then will give up for good
_DEFAULT_RETRY_WAITS = [ 500, 1500, 3000, 6000, 10000, 10000, 10000, 10000 ]

def do_over( func, retryWaits = _DEFAULT_RETRY_WAITS, cookie_obj = None, retry_alert = None, logger = None ):

    retry_attempt = 0
    retry_wait_total = 0
    while True:
        try:
            # flake out on the first attempt just to help make sure we hit all the bad spots
            return func(cookie_obj)
        except:

            retry_attempt += 1

            if len(retryWaits) < retry_attempt:
                if logger is not None:
                    logger.info('do_over failed %d many times, waited a total %d milliseconds, and finally gave up' % (retry_attempt,retry_wait_total))
                raise

            retry_wait = retryWaits[retry_attempt-1]
            retry_wait = int(retry_wait + random.randint(-(retry_wait/10),(retry_wait/10)))
            if retry_alert is not None:
                errType, errValue, errTraceback = sys.exc_info()
                if not retry_alert(cookie_obj,retry_attempt,retry_wait_total,errType,errValue,errTraceback):
                    if logger is not None:
                        logger.info('do_over failed %d many times, waited a total %d milliseconds, and finally gave up because retry_alert said to' % (retry_attempt,retry_wait_total))
                    raise
            if logger is not None:
                logger.warning('do_over error on retry_attempt %d, have waited total %d milliseconds, will retry again in %d milliseconds'%(retry_attempt,retry_wait_total,retry_wait))
            retry_wait_total += retry_wait
            time.sleep( float(retry_wait) / 1000.0 )
