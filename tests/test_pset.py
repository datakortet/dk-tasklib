# -*- coding: utf-8 -*-
import pytest

from dktasklib.pset import pset


def test_internal():
    """Test the add method.
    """
    p1 = pset(foo='bar', knights=9)
    # noinspection PyProtectedMember
    p1._add('round', 'table')  # pylint:disable=W0212
    assert p1.round == 'table'
    p1._foo = 42  # don't add to values
    assert p1 == pset(foo='bar', knights=9, round='table')
    # noinspection PyProtectedMember
    assert p1._foo == 42

    with pytest.raises(AttributeError):
        # noinspection PyStatementEffect
        p1.xxx


def test_init2():
    p1 = pset({'a': 1, 'b': 2})
    assert p1 == {'a': 1, 'b': 2}


def test_remove():
    """Test the remove method.
    """
    p1 = pset(foo='bar', knights=9)
    p1.remove('foo')
    assert str(p1) == "{'knights': 9}"


def test_eq_():
    """Test the __eq__ method.
    """
    p1 = pset(foo='bar', knights=9)
    ps1 = pset(foo='bar', knights=9)
    ps2 = pset(foo='bar', knights=8)
    ps3 = pset(foo='bar')
    ps4 = pset(knights=9, foo='bar')
    assert p1 == ps1
    assert p1 != ps2
    assert p1 != ps3
    assert p1 == ps4
    # noinspection PyComparisonWithNone
    assert not (p1 == None)
    assert p1 != None


def test_eq_order():
    p1 = pset()
    p2 = pset()
    assert p1 == p2
    p1.a = 1
    p2.a = 1
    assert p1 == p2
    p1.b = 2
    p2.b = 2


def test_delattr():
    p1 = pset(a=1, b=2)
    del p1.a
    assert p1 == pset(b=2)


def test_delitem():
    p1 = pset(a=1, b=2)
    del p1['a']
    assert p1 == pset(b=2)


def test_items_keys_values():
    p1 = pset()
    p1.a = 1
    p1.b = 2
    assert p1.keys() == ['a', 'b']
    assert p1.values() == [1, 2]
    assert list(p1.items()) == [('a', 1), ('b', 2)]


def test_iadd():
    p1 = pset()
    p2 = pset(a=1, b=2)
    p1 += p2
    assert p1 == p2


def test_radd():
    p1 = pset(a=1)
    p2 = {'b': 2}
    p3 = pset(a=1, b=2)
    assert p2 + p1 == p3


def test_add():
    p1 = pset(a=1)
    p2 = pset(b=2)
    p3 = pset()
    p3.a = 1
    p3.b = 2
    assert p1 + p2 == p3
    print 'p1 + p2:', p1 + p2
    print 'p2 + p1:', p2 + p1
    assert p1 + p2 == p2 + p1  # key order not considered for equality
