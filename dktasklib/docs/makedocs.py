# -*- coding: utf-8 -*-
import os
from jinja2 import Template  # sphinxdoc  makes jinja available...
DIRNAME = os.path.dirname(__file__)


def document_module(module):
    tmpltxt = open(os.path.join(DIRNAME, 'module-docs.jinja')).read().decode('u8')
    t = Template(tmpltxt)
    txt = t.render(module=module)
    module.fp.write(txt.encode('u8'))
