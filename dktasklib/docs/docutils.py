# -*- coding: utf-8 -*-


def synopsis(txt):
    try:
        return txt.split('\n\n')[0]
    except:
        return ''


def _import(name):
    if '.' in name:
        package, item = name.rsplit('.', 1)
        tmp = __import__(package, {}, {}, [item], -1)
        return getattr(tmp, item)
    else:
        return __import__(name, {}, {}, [], -1)
