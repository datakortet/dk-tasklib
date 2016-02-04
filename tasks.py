# -*- coding: utf-8 -*-
from invoke import Collection
from dktasklib import docs, version, publish

ns = Collection(docs, version, publish)
