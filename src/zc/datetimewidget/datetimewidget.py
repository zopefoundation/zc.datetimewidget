##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Datetime widget

$Id: datetimewidget.py 4368 2005-12-08 22:19:15Z gary $
"""
import datetime
import pytz

from zope.interface.common.idatetime import ITZInfo
from zope.datetime import DateTimeError
from zope.datetime import parseDatetimetz
from zope.app.form.browser import textwidgets
from zope.app.form.browser.widget import renderElement
import zope.datetime
import zc.i18n.date
import zc.resourcelibrary

def normalizeDateTime(dt, request):
    if dt is not None:
        if (dt.tzinfo is not None and
            isinstance(dt.tzinfo, zope.datetime._tzinfo)):
            tzinfo = ITZInfo(request)
            dt = dt.replace(tzinfo=None) # TODO: this is a hack
            # to accomodate pre-Zope-3.2 datetime widgets that assume UTC
            # timezone.  Zope 3.2+ datetime widgets should use the
            # request's timezone, or pytz.utc for UTC rather than the
            # datetimeutils version.
        dt = zc.i18n.date.normalize(request, dt)
    return dt

def localizeDateTime(dt, request):
    if isinstance(dt, datetime.datetime) and dt.tzinfo is pytz.utc:
        tzinfo = ITZInfo(request, None)
        if tzinfo is not None:
            dt = dt.astimezone(tzinfo)
    return dt

template = """
%(widget_html)s
<input type="button" value="..." id="%(name)s_trigger">
<script type="text/javascript">
  Calendar.setup(
    {
      inputField: "%(name)s", // ID of the input field
      ifFormat: "%(datetime_format)s", // the date format
      button: "%(name)s_trigger", // ID of the button
      showsTime: %(showsTime)s
    }
  );
</script>
"""


class DatetimeBase(object):

    def __call__(self):
        zc.resourcelibrary.need('zc.datetimewidget')
        widget_html = super(DatetimeBase, self).__call__()
        return template % {"widget_html": widget_html,
                           "name": self.name,
                           "showsTime": self._showsTime,
                           "datetime_format": self._format}

class DatetimeWidget(DatetimeBase, textwidgets.DatetimeWidget):
    """Datetime entry widget."""

    _format = '%Y-%m-%d %H:%M:%S'
    _showsTime = "true"

    def _toFormValue(self, value):
        dt = localizeDateTime(
            super(DatetimeWidget, self)._toFormValue(value),
            self.request)
        return dt.strftime(self._format)
        
    

    def _toFieldValue(self, input):
        res = super(DatetimeWidget, self)._toFieldValue(input)
        #import pdb;pdb.set_trace()
        if res is not self.context.missing_value:
            res = normalizeDateTime(res, self.request)
        return res

class DateWidget(DatetimeBase, textwidgets.DateWidget):
    """Date entry widget."""

    displayWidth = 10

    def _toFormValue(self, value):
        return localizeDateTime(
            super(DateWidget, self)._toFormValue(value), self.request)

    _format = '%Y-%m-%d'
    _showsTime = "false"

class DatetimeDisplayBase(object):

    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default
        if content == self.context.missing_value:
            return ""
        content = localizeDateTime(content, self.request)
        formatter = self.request.locale.dates.getFormatter(
            self._category, (self.displayStyle or None))
        content = formatter.format(content)
        return renderElement("span", contents=textwidgets.escape(content),
                             cssClass=self.cssClass)

class DatetimeDisplayWidget(
    DatetimeDisplayBase, textwidgets.DatetimeDisplayWidget):

    pass

class DateDisplayWidget(DatetimeDisplayBase, textwidgets.DateDisplayWidget):

    pass
