# -*- coding: utf-8 -*-

from invoke import collection
from dktasklib.docs import docs


ns = collection.Collection(
    docs
)
