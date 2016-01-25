# -*- coding: utf-8 -*-
import os

import invoke
from yamldirs import create_files

from dktasklib import lessc


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


def test_build_css(ctx):
    files = """
        foo.less: |
            .foo {
                display: flex;
                color: lighten(red, 20%);
            }
    """
    with create_files(files) as directory:
        os.chdir(directory)
        ctx.lessc= invoke.Config()
        ctx.lessc.source = 'less/index.less'
        ctx.lessc.target = ''
        ctx.lessc.bootstrap_less_src = os.path.join(os.environ.get('BOOTSTRAPSRC', ''), 'less')

        fname = lessc.build_css(ctx, 'foo.less', 'foo.css', version='hash')
        ctx.run('tree')
        #
        #    |-- build
        #    |   `-- css
        #    |       |-- foo-214ec5a558de22bb640095fe67ba9edc.min.css
        #    |       `-- foo.min.css
        #    `-- foo.less
        #
        print 'FNAME:test_build_css:', fname
        assert set(os.listdir('.')) == {'foo.less', 'build'}
        assert os.listdir('build') == ['css']
        assert set(os.listdir('build/css')) == {'foo.min.css', os.path.split(fname)[1]}
        print open(fname).read()
        assert 1


def test_build_css_pkg_version(ctx):
    files = """
        - package.json: |
            {"version": "1.2.3"}
        - foo.less: |
            .foo {
                display: flex;
                color: lighten(red, 20%);
            }
    """
    with create_files(files) as directory:
        os.chdir(directory)
        ctx.lessc= invoke.Config()
        ctx.lessc.source = 'less/index.less'
        ctx.lessc.target = ''
        ctx.lessc.bootstrap_less_src = os.path.join(os.environ.get('BOOTSTRAPSRC', ''), 'less')

        fname = lessc.build_css(ctx, 'foo.less', 'foo.css', version='pkg')
        ctx.run('tree')
        #
        #    |-- build
        #    |   `-- css
        #    |       |-- foo-1.2.3.min.css
        #    |       `-- foo.min.css
        #    `-- foo.less
        #
        print 'FNAME:test_build_css:', fname
        assert set(os.listdir('.')) == {'package.json', 'foo.less', 'build'}
        assert os.listdir('build') == ['css']
        assert set(os.listdir('build/css')) == {'foo.min.css', 'foo-1.2.3.min.css'}
        print open(fname).read()
        assert 1


def test_build_less(ctx):
    files = """
        - package.json: |
            {
                "name": "bar",
                "version": "1.2.3"
            }
        - less:
            - bar.less: |
                .foo {
                    display: flex;
                    color: lighten(red, 20%);
                }
    """
    with create_files(files) as directory:
        os.chdir(directory)
        ctx.lessc= invoke.Config()
        ctx.lessc.source = 'less/index.less'
        ctx.lessc.target = ''
        ctx.lessc.bootstrap_less_src = os.path.join(os.environ.get('BOOTSTRAPSRC', ''), 'less')
        lessc.build(ctx)
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
