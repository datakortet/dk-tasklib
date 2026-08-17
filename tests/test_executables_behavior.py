from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest
from dkfileutils.path import Path

from dktasklib import executables


def test_context_is_lazy_and_require_checks_each_dependency(monkeypatch):
    registry = executables.Executables()
    assert registry._ctx is None
    assert registry.ctx is registry.ctx

    find = Mock()
    monkeypatch.setattr(registry, 'find', find)
    registry.require('one', 'two')
    assert find.call_args_list == [call('one'), call('two')]


def test_find_caches_custom_and_generic_lookups(monkeypatch):
    registry = executables.Executables()
    registry.find_custom = Mock(return_value='custom.exe')
    generic = Mock(return_value='generic.exe')
    monkeypatch.setattr(registry, '_find_exe', generic)

    assert registry.find('custom') == 'custom.exe'
    assert registry.find('custom') == 'custom.exe'
    assert registry.find_custom.call_count == 1

    assert registry.find('generic', requires=('base',), install_txt='install') == (
        'generic.exe'
    )
    assert generic.call_args_list[-1] == call('generic', ('base',), 'install')


def test_find_executable_and_local_node_binary(monkeypatch, tmp_path):
    registry = executables.Executables()
    monkeypatch.setattr(executables, 'get_executable', lambda name: 'tool.exe')
    assert registry._find_exe('tool') == 'tool.exe'

    binary_dir = tmp_path / 'node_modules' / '.bin'
    binary_dir.mkdir(parents=True)
    (binary_dir / 'local.cmd').write_text('')
    monkeypatch.setattr(executables, 'get_executable', lambda name: None)
    monkeypatch.setattr(
        executables,
        'Package',
        lambda: SimpleNamespace(root=Path(str(tmp_path))),
        raising=False,
    )
    assert registry._find_exe('local').endswith('local.cmd')

    with pytest.raises(executables.MissingCommand, match='requires'):
        registry._find_exe('missing', requires=('node',))
    with pytest.raises(executables.MissingCommand, match='install this'):
        registry._find_exe('missing', install_txt='install this')


@pytest.mark.parametrize(
    ('method', 'executable', 'install_command'),
    [
        ('find_twine', 'twine', 'pip.exe install twine'),
        ('find_uglify', 'uglifyjs', 'npm install -g uglify-js --no-color'),
        ('find_browserify', 'browserify', 'npm install -g browserify --no-color'),
        ('find_babili', 'babili', 'npm install -g babili --no-color'),
        ('find_babel', 'babel', 'npm install -g babel-cli --no-color'),
    ],
)
def test_installable_executables_on_windows(
        monkeypatch, method, executable, install_command):
    registry = executables.Executables()
    calls = []

    def locate(name):
        calls.append(name)
        if name == 'pip':
            return 'pip.exe'
        return None if calls.count(executable) == 1 else executable + '.exe'

    monkeypatch.setattr(executables, 'get_executable', locate)
    monkeypatch.setattr(executables, 'win32', True)
    registry._ctx = SimpleNamespace(run=Mock())
    run = Mock()
    monkeypatch.setattr(executables.runners, 'run', run)

    result = getattr(registry, method)()
    assert result == executable + '.exe'
    if method in ('find_twine',):
        run.assert_called_once_with(install_command)
    else:
        registry.ctx.run.assert_called_once()
        assert install_command in registry.ctx.run.call_args.args[0]


def test_find_wheel_installs_and_generates_key(monkeypatch):
    registry = executables.Executables()
    found = iter([None, 'pip.exe', 'wheel.exe'])
    monkeypatch.setattr(executables, 'get_executable', lambda name: next(found))
    monkeypatch.setattr(executables, 'win32', True)
    run = Mock()
    monkeypatch.setattr(executables.runners, 'run', run)

    assert registry.find_wheel() == 'wheel.exe'
    assert run.call_args_list == [
        call('pip.exe install wheel[signatures]'),
        call('wheel.exe keygen'),
    ]


@pytest.mark.parametrize(
    ('method', 'message'),
    [
        ('find_wheel', 'Missing wheel'),
        ('find_twine', 'Missing twine'),
        ('find_uglify', 'Missing uglifyjs'),
        ('find_browserify', 'Missing browserify'),
        ('find_babili', 'Missing babili'),
        ('find_babel', 'Missing babel'),
    ],
)
def test_missing_installable_executables_on_non_windows(
        monkeypatch, method, message):
    registry = executables.Executables()
    monkeypatch.setattr(
        executables,
        'get_executable',
        lambda name: 'pip.exe' if name == 'pip' else None,
    )
    monkeypatch.setattr(executables, 'win32', False)

    with pytest.raises(executables.MissingCommand, match=message):
        getattr(registry, method)()


def test_node_and_npm_detection(monkeypatch):
    registry = executables.Executables()
    monkeypatch.setattr(executables.sys, 'platform', 'linux')
    monkeypatch.setattr(
        executables,
        'get_executable',
        lambda name: '/bin/node' if name == 'node' else None,
    )
    assert registry.find_nodejs() == '/bin/node'

    monkeypatch.setattr(
        executables,
        'get_executable',
        lambda name: '/bin/npm' if name == 'npm' else None,
    )
    assert registry.find_npm() == '/bin/npm'

    monkeypatch.setattr(executables, 'get_executable', lambda name: None)
    with pytest.raises(executables.MissingCommand, match='Install Node.js'):
        registry.find_nodejs()
    with pytest.raises(executables.MissingCommand, match='Install Node.js'):
        registry.find_npm()


def test_requires_warns_but_preserves_function(monkeypatch):
    monkeypatch.setattr(
        executables.exe,
        'require',
        Mock(side_effect=executables.MissingCommand('missing')),
    )

    def operation():
        return 'ok'

    with pytest.warns(UserWarning, match='missing'):
        decorated = executables.requires('tool')(operation)
    assert decorated is operation
