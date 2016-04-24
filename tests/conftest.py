# -*- coding: utf-8 -*-
# pragma: nocover
import invoke
import pytest


class DkContext(object):
    def init(self, default=None, **kw):

        def cfg_dict(d):
            res = invoke.Config()
            for k, v in d.items():
                res[k] = cfg_obj(v)
            return res

        def cfg_obj(obj):
            return {
                dict: cfg_dict
            }.get(type(obj), lambda x: x)(obj)

        cfg = invoke.Config().config
        if default is not None:
            cfg.update(default)
        cfg.update(kw)
        return invoke.Context(cfg_dict(cfg))


@pytest.fixture
def ctx():
    return DkContext()
