# pragma: nocover
import invoke
import pytest


class DkContext:
    def init(self, default=None, **kw):
        overrides = {}
        if default is not None:
            overrides.update(default)
        overrides.update(kw)
        return invoke.Context(config=invoke.Config(overrides=overrides))


@pytest.fixture
def ctx():
    return DkContext()
