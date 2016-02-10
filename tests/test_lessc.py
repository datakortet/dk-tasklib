# -*- coding: utf-8 -*-
import os

import invoke
from yamldirs import create_files

from dktasklib import lessc
from dktasklib.utils import cd


def test_lessc(ctx):
    files = """
        foo.less: |
            .foo {
                display: flex;
            }
    """
    with create_files(files) as directory:
        os.chdir(directory)
        assert lessc.lessc(ctx, 'foo.less') == 'foo.css'
        assert 'foo.css' in os.listdir('.')
        print open('foo.css').read()
        assert len(open('foo.css').read()) > len(open('foo.less').read())


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

#
# def test_build_css():
#     files = """
#         foo.less: |
#             .foo {
#                 display: flex;
#                 color: lighten(red, 20%);
#             }
#     """
#     with create_files(files) as directory:
#         os.chdir(directory)
#         ctx = get_context({}, lessc.ns.configuration())
#
#         fname = lessc.build_css(ctx, 'foo.less', 'foo.css', version='hash')
#         ctx.run('tree')
#         #
#         #    |-- build
#         #    |   `-- css
#         #    |       |-- foo-214ec5a558de22bb640095fe67ba9edc.min.css
#         #    |       `-- foo.min.css
#         #    `-- foo.less
#         #
#         print 'FNAME:test_build_css:', fname
#         assert set(os.listdir('.')) == {'foo.less', 'build'}
#         assert os.listdir('build') == ['css']
#         assert set(os.listdir('build/css')) == {'foo.min.css', os.path.split(fname)[1]}
#         print open(fname).read()
#         assert 1


# def test_build_css_pkg_version():
#     files = """
#         - package.json: |
#             {"version": "1.2.3"}
#         - foo.less: |
#             .foo {
#                 display: flex;
#                 color: lighten(red, 20%);
#             }
#     """
#     with create_files(files) as directory:
#         os.chdir(directory)
#         ctx = get_context({'pkg': {"version": "1.2.3"}}, lessc.ns.configuration())
#
#         # ctx.lessc= invoke.Config()
#         # ctx.lessc.source = 'less/index.less'
#         # ctx.lessc.target = ''
#         # ctx.lessc.bootstrap_less_src = os.path.join(os.environ.get('BOOTSTRAPSRC', ''), 'less')
#
#         fname = lessc.build_css(ctx, 'foo.less', 'foo.css', version='pkg')
#         ctx.run('tree')
#         #
#         #    |-- build
#         #    |   `-- css
#         #    |       |-- foo-1.2.3.min.css
#         #    |       `-- foo.min.css
#         #    `-- foo.less
#         #
#         print 'FNAME:test_build_css:', fname
#         assert set(os.listdir('.')) == {'package.json', 'foo.less', 'build'}
#         assert os.listdir('build') == ['css']
#         assert set(os.listdir('build/css')) == {'foo.min.css', 'foo-1.2.3.min.css'}
#         print open(fname).read()
#         assert 1


def test_build_less():
    files = """
    andy:
        package.json: |
            {
                "name": "bar",
                "version": "1.2.3"
            }
        invoke.json: |
            {
                "pkg": {
                    "name": "andy",
                    "version": "4.5.6"
                }
            }
        less:
            bar.less: |
                .foo {
                    display: flex;
                    color: orange;
                }
            andy.less: |
                .foo {
                    display: inline;
                    color: chartreuse;
                }

    """
    with create_files(files) as directory:
        # os.chdir(directory)

        ctx = get_context(
            invoke.Config(runtime_path='invoke.json'),
            lessc.ns.configuration()
        )
        # ctx.config.merge()
        print "CONFIGGGG:"
        import pprint;pprint.pprint(dict(**ctx.config))
        # ctx.lessc = invoke.Config()
        # ctx.lessc.source = 'less/index.less'
        # ctx.lessc.target = ''
        # ctx.lessc.bootstrap_less_src = os.path.join(os.environ.get('BOOTSTRAPSRC', ''), 'less')
        lessc.build_less(ctx)
        ctx.run('tree')
        #
        #    |-- build
        #    |   `-- css
        #    |       `-- static
        #    |           `-- bar
        #    |               |-- bar-1.2.3.min.css
        #    |               `-- bar.min.css
        #    |-- less
        #    |   `-- bar.less
        #    `-- package.json
        #
        assert 1
