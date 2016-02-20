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


def test_less_rule_default():
    # standard package structure..
    files = """
    mypackage:
        - package.json: |
            {"version": "1.2.3"}
        - setup.py
        - mypackage:
            - less:
                mypackage.less: |
                    .foo {
                        display: flex;
                        color: lighten(red, 20%);
                    }
    """
    with create_files(files) as directory:
        os.chdir('mypackage')  # into the package directory

        ctx = get_context({
            'pkg': Package()
        }, lessc.ns.configuration())

        fname = rule.LessRule(ctx)
        ctx.run('tree')
        # .
        # |-- mypackage
        # |   |-- less
        # |   |   `-- mypackage.less
        # |   |-- static
        # |   |   `-- mypackage
        # |   |       `-- css
        # |   |           |-- mypackage-1.2.3.min.css
        # |   |           `-- mypackage.css
        # |   `-- templates
        # |       `-- mypackage
        # |           `-- mypackage-css.html
        # |-- package.json
        # `-- setup.py


        print 'FNAME:test_build_css:', fname
        assert set(os.listdir('.')) == {'package.json', 'foo.less', 'build'}
        assert os.listdir('build') == ['css']
        assert set(os.listdir('build/css')) == {'foo.min.css', 'foo-1.2.3.min.css'}
        print open(fname).read()
        assert 1
