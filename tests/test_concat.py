# -*- coding: utf-8 -*-
import os

from yamldirs import create_files

from dktasklib.concat import line_endings, chomp, fix_line_endings, concat, copy


def test_line_endings():
    files = """
        foo.txt
    """
    with create_files(files) as directory:
        with open('foo.txt', 'wb') as fp:
            fp.write("a\nb\r\nc\nd\n")

        print repr(open('foo.txt', 'rb').read())

        assert len(line_endings('foo.txt')) == 2

        fix_line_endings('foo.txt')
        assert len(line_endings('foo.txt')) == 1


def test_chomp():
    assert chomp('ab\r\n') == 'ab'
    assert chomp('ab\n') == 'ab'
    assert chomp('') == ''
    assert chomp('ab') == 'ab'


def test_copy(ctx):
    files = """
        foo.txt: hello world
    """
    with create_files(files) as directory:
        ctx = ctx.init()
        copy(ctx, 'foo.txt', 'foo.txt')
        copy(ctx, 'foo.txt', 'bar.txt')
        assert open('bar.txt').read() == 'hello world'


def test_concat(ctx):
    files = """
        foo.txt
        bar.txt
    """
    with create_files(files) as directory:
        with open('foo.txt', 'wb') as fp:
            fp.write('a\r\n')
        with open('bar.txt', 'wb') as fp:
            fp.write('b\n')
        print "LISTDIR", os.listdir('.')
        concat(ctx.init(), 'baz.txt', 'foo.txt', 'bar.txt', force=True)
        assert open('baz.txt').read().split() == ['a', 'b']
