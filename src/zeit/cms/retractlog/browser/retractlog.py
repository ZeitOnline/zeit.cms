from datetime import datetime
from zeit.cms.i18n import MessageFactory as _

import pytz
import re
import zc.table
import zeit.cms.retractlog.interfaces
import zope.formlib.form
import zope.interface

import zeit.cms.browser
import zeit.cms.workflow.interfaces


class Listing(zeit.cms.browser.listing.Listing):

    title = _("Retract log")
    filter_interface = zope.interface.Interface
    css_class = 'contentListing'

    columns = (
        zc.table.column.SelectionColumn(
            idgetter=lambda item: item.__name__),
        zeit.cms.browser.column.LinkColumn(
            title=_('Title'),
            cell_formatter=lambda v, i, f: i.title),
    )

    @property
    def content(self):
        return self.context.values()


class View(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.published = []
        self.retracted = []
        self.unknown = []
        for url in self.context.urls:
            content = zeit.cms.interfaces.ICMSContent(url, None)
            if content:
                pub_info = zeit.cms.workflow.interfaces.IPublishInfo(content)
                if pub_info.published:
                    self.published.append(url)
                else:
                    self.retracted.append(url)
            else:
                self.unknown.append(url)

    def config(self):
        return "\n".join(["%s=410" % url.replace('http://xml.zeit.de', "")
                          for url in self.retracted])

    def produce_config(self):
        return not self.published and self.retracted


class Add(zeit.cms.browser.form.AddForm):

    title = _("Add retract job")
    factory = zeit.cms.retractlog.retractlog.Job
    next_view = 'index.html'
    form_fields = zope.formlib.form.FormFields(
        zeit.cms.retractlog.interfaces.IJob).select('urls_text')

    def suggestName(self, job):
        job.title = datetime.now(
            pytz.timezone('Europe/Berlin')).strftime(
                '%Y-%m-%dT%H:%M:%S')
        return job.title

    def applyChanges(self, job, data):
        urls = data['urls_text'].split('\n')
        data['urls_text'] = ''
        url_match = re.compile('.*.zeit.de')
        for url in urls:
            url = url.strip()
            if not url:
                continue
            unique_id = re.sub(url_match, 'http://xml.zeit.de', url)
            custom_filter = re.compile(
                zeit.cms.retractlog.interfaces.RETRACT_LOG_SOURCE.filter)
            if custom_filter.match(unique_id):
                if zeit.cms.interfaces.ICMSContent(unique_id, None):
                    job.urls.append(unique_id)
                else:
                    job.unknown.append(unique_id)
            else:
                job.invalid.append(unique_id)
        if job.invalid:
            self.send_message(
                _('Job created but invalid urls where found'),
                type='error')
        else:
            self.send_message(_('Retract job created.'))
        changed = super(Add, self).applyChanges(job, data)
        job.start()
        return changed


class MenuItem(zeit.cms.browser.menu.GlobalMenuItem):

    title = _("Retract log")
    viewURL = 'retractlog'
    pathitem = 'retractlog'
