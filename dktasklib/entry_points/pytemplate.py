# -*- coding: utf-8 -*-
from string import Template
import re


class PyTemplate(Template):
    """
    Template strings that can replace ##{PATTERN} instances.
    """
    def __init__(self, t):
        super(PyTemplate, self).__init__(t.replace('$', '$$').replace('##{', '${'))

    def substitute(self, *args, **kw):
        return super(PyTemplate, self).substitute(
            **{k.upper(): v for k, v in kw.iteritems()}
        )
