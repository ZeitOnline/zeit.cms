# Copyright (c) 2007-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.view
import zeit.cms.checkout.interfaces
import zeit.cms.content.interfaces
import zeit.cms.interfaces
import zope.cachedescriptors.property
import zope.location.interfaces
import zope.traversing.api


MARKER = object()


class Breadcrumbs(zeit.cms.browser.view.Base):

    @zope.cachedescriptors.property.Lazy
    def get_breadcrumbs(self):
        """Returns a list of dicts with title and URL."""
        try:
            metadata = zeit.cms.content.interfaces.ICommonMetadata(
                self.context)
        except TypeError:
            pass
        else:
            return self.get_breadcrumbs_from_commonmetadata(metadata)
        return self.get_breadcrumbs_from_path(self.context)

    def get_breadcrumbs_from_commonmetadata(self, context):
        result = []

        if context.ressort:
            ressort_id = 'http://xml.zeit.de/%s' % (context.ressort.lower())
            url = self.cms_url(ressort_id)
            if url:
                result.append(dict(
                        title=context.ressort,
                        url=url,
                        uniqueId=None,
                        ))

        if context.sub_ressort:
            sub_ressort_id = '%s/%s' % (
                ressort_id, context.sub_ressort.lower())
            url = self.cms_url(sub_ressort_id)
            if url:
                result.append(dict(
                        title=context.sub_ressort,
                        url=url,
                        uniqueId=None,
                        ))

        name = context.__name__
        url = self.url(context)
        unique_id = getattr(context, 'uniqueId', None)
        result.append(dict(
            title=name,
            url=url,
            uniqueId=unique_id,
            ))

        return result

    def get_breadcrumbs_from_path(self, context):
        has_parents = True
        if zeit.cms.checkout.interfaces.ILocalContent.providedBy(context):
            try:
                context = zeit.cms.interfaces.ICMSContent(context.uniqueId)
            except TypeError:
                has_parents = False
        traverse_items = [context]
        if has_parents:
            traverse_items += zope.traversing.api.getParents(context)

        result = []
        for item in traverse_items:
            if zope.location.interfaces.ISite.providedBy(item):
                break
            title = item.__name__
            uniqueId = getattr(item, 'uniqueId', None)
            result.append(
                dict(title=title,
                     url=self.url(item),
                     uniqueId=uniqueId))

        result.reverse()
        return result

    def cms_url(self, unique_id):
            try:
                return self.url(zeit.cms.interfaces.ICMSContent(unique_id))
            except TypeError:
                return None
