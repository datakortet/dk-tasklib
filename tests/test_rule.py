# -*- coding: utf-8 -*-
import os

import invoke
from yamldirs import create_files

from dktasklib import lessc
from dktasklib import Package
from dktasklib import rule


def get_context(dct, default=None):
    def cfg_dict(d):
        res = invoke.Config()
        for k, v in d.items():
            res[k] = cfg_obj(v)
        return res

    def cfg_obj(obj):
        return {
            dict: cfg_dict
        }.get(type(obj), lambda x:x)(obj)

    cfg = invoke.Config().config
    if default is not None:
        cfg.update(default)
    cfg.update(dct)
    return invoke.Context(cfg_obj(cfg))
