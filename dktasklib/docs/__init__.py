# -*- coding: utf-8 -*-

from dkfileutils.path import Path
from invoke import Collection
from .docstasks import build, tree, browse_docs, clean_docs, mkdocs


# Vanilla/default/parameterized collection for normal use
ns = Collection('docs', clean_docs, browse_docs, build, tree, mkdocs)
ns.configure({
    'docs': {
        'source': 'docs',
        'builddir': Path('build') / 'docs',
        'target_file': 'index.html',
    }
})
