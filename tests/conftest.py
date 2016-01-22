# -*- coding: utf-8 -*-
import invoke
import pytest


@pytest.fixture
def ctx():
    return invoke.Context()
