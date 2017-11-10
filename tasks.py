# -*- coding: utf-8 -*-
from invoke import Collection
from dktasklib import docs, version, upversion, publish

ns = Collection(docs, version, upversion, publish)
ns.configure({
    'run': {
        'echo': True
    }
})
