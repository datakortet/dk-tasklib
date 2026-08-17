# -*- coding: utf-8 -*-
from string import Template


class PyTemplate(Template):
    """
    Template strings that can replace ##{PATTERN} instances.
    """
    def __init__(self, t):
        if isinstance(t, bytes):
            t = t.decode('u8')
        super(PyTemplate, self).__init__(t.replace('$', '$$').replace('##{', '${'))

    def substitute(self, *args, **kw):
        return super(PyTemplate, self).substitute(
            **{k.upper(): v for k, v in kw.items()}
        )
