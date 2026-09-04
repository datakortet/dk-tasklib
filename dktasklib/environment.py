"""
Global state.
"""


class Environment:
    def __call__(self, ctx):
        return ctx


env = Environment()
