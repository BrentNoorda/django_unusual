import inspect
import datetime
import traceback
from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.db import models, transaction, IntegrityError, DatabaseError

import logging
logger = logging.getLogger(__name__)

############################### ColorTemp ###############################
## Record user color choices, along with the temperature in oakland when that happened.
## The id in her cycles back to zero after it gets too big.
## You should run demos/ColorTemp_GC.py once in a while to clear out old crap (because
## we only care about this stuff over about the past hour).

class ColorTemp(models.Model):
    # id <IMPLICIT>     - will be set to automatically rollover
    created = models.DateTimeField(null=False,blank=False,db_index=True)
    color = models.CharField(max_length=100,null=False,blank=False)
    temperature = models.SmallIntegerField(null=False,blank=False)

    HOW_MANY_HOURS_TO_CARE = 1       # how many hours we care about this data

    def __unicode__(self):
        return u"#%d: %s - %d %s" % (self.id,unicode(self.created),self.temperature,self.color)

admin.site.register(ColorTemp)


################################# Crash #################################
## record of bad things that have happened - keep a couple of globals here
## to catch the case where crashes are getting out of control -- there may be lots of
## servers so this global only catches this instance on this server, but still it can
## keep us from getting way out of control

class Crash(models.Model):
    hash = models.BigIntegerField(primary_key=True)   # so similar crashes all belong together - made from label+details+trace+customer_id+filename+lineno
    first = models.DateTimeField(null=False,blank=False)                # index this mostly to prevent cascade situations when our database use is just out of control
    last = models.DateTimeField(null=False,blank=False)                 # most-recent time this happened
    count = models.IntegerField(null=False,blank=False)                 # how many times has this crash occured

    label = models.CharField(max_length=1000,null=False,blank=True)     # usually a short explanation
    details = models.CharField(max_length=10000,null=False,blank=True)  # probably a big crash report
    trace = models.CharField(max_length=10000,null=False,blank=True)    # try to get from traceback
    url = models.CharField(max_length=10000,null=False,blank=True)      # url that was being called, if we know it
    body = models.CharField(max_length=20000,null=False,blank=True)     # a lot of the body from this crash

    filename = models.CharField(max_length=1000,null=False,blank=True)  # what python file called Crash.record
    lineno = models.IntegerField(null=False,blank=False)                # line where Crash.record was called

    userid = models.IntegerField(null=False,blank=False)                  # user id if known (else 0)

    _last_crash_time = None
    _last_crash_time_count = 0

    @classmethod
    def record(cls,request=None,label='',details='',trace=None,         # if trace none we'll figure it out here
               may_contain_sensitive_information=False):                # if it's possible there is e.g. passwords or credit cards don't log that
        try:
            now = datetime.datetime.utcnow().replace(microsecond=0)

            # see if maybe there are too many crashes going on
            if cls._last_crash_time == now:
                cls._last_crash_time_count += 1
            else:
                cls._last_crash_time = now
                cls._last_crash_time_count = 1

            if cls._last_crash_time_count > 10:
                logger.info("GETTING TOO MANY ERRORS THIS SECOND, SO GIVE UP ON CRASH RECORDING UNTIL NEXT SECOND")
                return

            label=label[:333]
            details=details[:3333]
            if trace is None:
                try:
                    trace = unicode(traceback.format_exc())[:3333]
                except Exception:
                    trace = ''
            else:
                trace = unicode(trace)[:3333]

            if request is None:
                url = ''
                rawbody = ''
                userid = 0
            else:
                try:
                    url = request.get_full_path()[:3333]
                    if may_contain_sensitive_information:
                        quoteIdx = url.find('?')
                        if quoteIdx != -1:
                            url = url[:quoteIdx+1] + '~~~ may contain sensitive information, so not recorded ~~~'
                except Exception:
                    url = ''
                try:
                    rawbody = unicode(request.body)
                    if may_contain_sensitive_information and (len(rawbody) != 0):
                        rawbody = '~~~ may contain sensitive information, so not recorded ~~~'
                except Exception:
                    rawbody = ''
                try:
                    userid = request.user.id
                    if userid is None:
                        userid = 0
                except Exception:
                    userid = 0

            body = u'------------------------------ %s ------------------------------\r\n' % unicode(now)
            if request is not None:
                try:
                    for head,val in request.META.items():
                        body += u'%s: %s\r\n' % (head,val)
                except:
                    body += u'ERROR GETTING HEADERS\r\n'

            body += rawbody
            body = body[:6666]

            # determine filename and lineno stuff from fancy python libraries
            try:
                _, filename, lineno, _, _, _ = inspect.stack()[1]
                if filename is None:
                    filename = ''
                if lineno is None:
                    lineno = 0
            except Exception:
                filename = ''
                lineno = 0

            calchash = hash(label + details + trace + unicode(userid) + filename + unicode(lineno) )

            crash = cls(hash=calchash,first=now,last=now,count=1,label=label,details=details,trace=trace,url=url,body=body,
                        filename=filename,lineno=lineno,userid=userid)

            # try real hard to reset any error that may currently exist in the database
            try:
                sid = transaction.savepoint()
            except DatabaseError:
                try:
                    transaction.rollback()  # may lose even good transaction that already happened, but, sheesh, we want to record this!
                except:
                    pass
                sid = transaction.savepoint()
            try:
                crash.save(force_insert=True)
                transaction.savepoint_commit(sid)
            except IntegrityError:
                # apparently this hash already exists - so add one more count to it
                transaction.savepoint_rollback(sid)
                crash = cls.objects.get(hash=calchash)
                crash.last = now
                if crash.count < 2000000000:
                    crash.count += 1
                crash.body = ( body + u'\r\n' + crash.body )[:6666]

                crash.save(force_update=True)

        except Exception:
            logger.exception("ERROR ON Crash.record")


    @staticmethod
    def trytryagain_alert(cookie_obj,attempts,retry_wait_total,errType,errValue,errTraceback):
        # while we are not yet sure how often we'll used this (e.g. for S3 failures) we will record each instance in crash log
        request = None
        label = ''
        if cookie_obj is not None:
            request = cookie_obj.get('request',None)
            label = cookie_obj.get('label','')
        Crash.record(request=request,label='trytryagain failing after %d attempts and waiting a total %d milliseconds. %s' % (attempts,retry_wait_total,label),
                     details=unicode(errValue),trace=errTraceback)
        return True

    @classmethod
    def warning_message(cls):
        # return a message about what's wrong, and level - level 0 means no problem (and no message)
        # else level 1 is a warning and level 2 is an error and level 3 is severe
        now = datetime.datetime.utcnow()
        def too_old_count(minutes,msg):
            recent_time = now - datetime.timedelta(minutes=minutes)
            count = cls.objects.filter(last__gte=recent_time).count()
            if count == 0:
                return None
            else:
                return 'At least %d calls to Crash.record in the past %s.' % (count,msg)
        bad = too_old_count(15,'15 minutes')
        if bad is not None:
            return 3,bad
        bad = too_old_count(60,'hour')
        if bad is not None:
            return 2,bad
        bad = too_old_count(60*24,'day')
        if bad is not None:
            return 1,bad
        return 0,None

    def __unicode__(self):
        return u'%d %s %s - %s - %s - %s:%d' % (self.count,unicode(self.last),self.how_long_ago(),self.label[:40],self.details[:80],self.filename,self.lineno)

    class Meta:
        ordering = ['-last']    # see newest crashes first

class CrashAdmin(admin.ModelAdmin):
    list_display = ('hash','count','last','ago','label','details','filename_lineno')
    fields = ('hash','count','first','last_happened','label','url','filename_lineno','userid','details_html','trace_html','body_html')
    readonly_fields = ('hash','count','first','last_happened','label','url','filename_lineno','userid','details_html','trace_html','body_html')

    def trace_html(self,obj):
        return mark_safe(u'<br/><pre>%s</pre>' % escape(unicode(obj.trace)))
    trace_html.short_description = "Trace"

    def ago(self,obj):
        return obj.how_long_ago()[1:-5]
    ago.short_description = "age"

    def body_html(self,obj):
        return mark_safe(u'<br/><pre>%s</pre>' % escape(unicode(obj.body)))
    body_html.short_description = "Body"

    def details_html(self,obj):
        return mark_safe(u'%s' % escape(unicode(obj.details)))
    details_html.short_description = "Details"

    def last_happened(self,obj):
        return unicode(obj.last) + u' ' + obj.how_long_ago()
    last_happened.short_description = "Last"

    def filename_lineno(self,obj):
        return obj.filename + ' : ' + str(obj.lineno)
    filename_lineno.short_description = "CalledFrom"

admin.site.register(Crash,CrashAdmin)
