from zeit.cms.content.interfaces import WRITEABLE_LIVE, WRITEABLE_ALWAYS
from zeit.cms.i18n import MessageFactory as _
from zeit.cms.workflow.interfaces import PRIORITY_TIMEBASED
import celery.result
import datetime
import pytz
import rwproperty
import zeit.cms.content.dav
import zeit.cms.content.xmlsupport
import zeit.workflow.interfaces
import zeit.workflow.publish
import zeit.workflow.publishinfo
import zope.component
import zope.interface


WORKFLOW_NS = zeit.workflow.interfaces.WORKFLOW_NS


class TimeBasedWorkflow(zeit.workflow.publishinfo.PublishInfo):
    """Timebased workflow."""

    zope.interface.implements(zeit.workflow.interfaces.ITimeBasedPublishing)

    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing[
            'release_period'].fields[0],
        WORKFLOW_NS, 'released_from', writeable=WRITEABLE_ALWAYS)
    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.ITimeBasedPublishing[
            'release_period'].fields[1],
        WORKFLOW_NS, 'released_to', writeable=WRITEABLE_ALWAYS)

    publish_job_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.Text(), WORKFLOW_NS, 'publish_job_id',
        writeable=WRITEABLE_LIVE)
    retract_job_id = zeit.cms.content.dav.DAVProperty(
        zope.schema.Text(), WORKFLOW_NS, 'retract_job_id',
        writeable=WRITEABLE_LIVE)

    def __init__(self, context):
        self.context = self.__parent__ = context

    @rwproperty.getproperty
    def release_period(self):
        return self.released_from, self.released_to

    @rwproperty.setproperty
    def release_period(self, value):
        """When setting the release period jobs to publish retract are created.
        """
        if value is None:
            value = None, None
        released_from, released_to = value
        if self.released_from != released_from:
            cancelled = self.cancel_job(self.publish_job_id)
            if cancelled:
                self.log(
                    _('scheduled-publishing-cancelled',
                      default=(u"Scheduled publication cancelled "
                               "(job #${job})."),
                      mapping=dict(job=self.publish_job_id)))
            if released_from is not None:
                self.publish_job_id = self.add_job(
                    zeit.workflow.publish.PUBLISH_TASK,
                    released_from)
                self.log(_('scheduled-for-publishing-on',
                           default=u"To be published on ${date} (job #${job})",
                           mapping=dict(
                               date=self.format_datetime(released_from),
                               job=self.publish_job_id)))

        if self.released_to != released_to:
            cancelled = self.cancel_job(self.retract_job_id)
            if cancelled:
                self.log(
                    _('scheduled-retracting-cancelled',
                      default=(u"Scheduled retracting cancelled "
                               "(job #${job})."),
                      mapping=dict(job=self.retract_job_id)))
            if released_to is not None:
                self.retract_job_id = self.add_job(
                    zeit.workflow.publish.RETRACT_TASK,
                    released_to)
                self.log(_('scheduled-for-retracting-on',
                           default=u"To be retracted on ${date} (job #${job})",
                           mapping=dict(
                               date=self.format_datetime(released_to),
                               job=self.retract_job_id)))

        self.released_from, self.released_to = value

    def add_job(self, task, when):
        delay = when - datetime.datetime.now(pytz.UTC)
        delay = 60 * 60 * 24 * delay.days + delay.seconds  # Ignore microsecond
        if delay > 0:
            job_id = task.apply_async(
                (self.context.uniqueId,), countdown=delay,
                urgency=PRIORITY_TIMEBASED).id
        else:
            job_id = task.delay(self.context.uniqueId).id
        return job_id

    def cancel_job(self, job_id):
        if not job_id:
            return False
        promise = celery.result.AsyncResult(job_id)
        if promise.status != u'PENDING':
            return False
        promise.revoke()
        return True

    def log(self, message):
        log = zope.component.getUtility(zeit.objectlog.interfaces.IObjectLog)
        log.log(self.context, message)

    @staticmethod
    def format_datetime(dt):
        interaction = zope.security.management.getInteraction()
        request = interaction.participations[0]
        tzinfo = zope.interface.common.idatetime.ITZInfo(request, None)
        if tzinfo is not None:
            dt = dt.astimezone(tzinfo)
        formatter = request.locale.dates.getFormatter('dateTime', 'medium')
        return formatter.format(dt)


class XMLReferenceUpdater(zeit.cms.content.xmlsupport.XMLReferenceUpdater):
    """Add the expire/publication time to feed entry."""

    target_iface = zeit.workflow.interfaces.ITimeBasedPublishing

    def update_with_context(self, entry, workflow):
        date = ''
        if workflow.released_from:
            date = workflow.released_from.isoformat()
        entry.set('publication-date', date)

        date = ''
        if workflow.released_to:
            date = workflow.released_to.isoformat()
        entry.set('expires', date)
