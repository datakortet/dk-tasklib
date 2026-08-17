from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from dktasklib import jstools


def make_context(tmp_path):
    return SimpleNamespace(
        pkg=SimpleNamespace(root=str(tmp_path)),
        run=Mock(),
    )


def test_node_project_configuration_helpers(monkeypatch, tmp_path):
    ctx = make_context(tmp_path)

    assert jstools.ensure_package_json(ctx) is None
    ctx.run.assert_called_once_with('npm init -f')
    (tmp_path / 'package.json').write_text('{}')
    assert jstools.ensure_package_json(ctx) is True

    assert jstools.ensure_babelrc(ctx) is None
    babelrc = (tmp_path / '.babelrc').read_text()
    assert '"presets"' in babelrc
    assert jstools.ensure_babelrc(ctx) is True

    assert jstools.ensure_node_modules(ctx) is None
    assert ctx.run.call_args.args[0] == 'npm install --no-color'
    (tmp_path / 'node_modules').mkdir()
    assert jstools.ensure_node_modules(ctx) is True


@pytest.mark.parametrize(
    ('function_name', 'needle', 'install_command'),
    [
        ('ensure_es2015', 'babel-preset-es2015', 'npm install babel-preset-es2015 --save-dev'),
        ('ensure_preset_es2016', 'babel-preset-es2015', 'npm install babel-preset-es2016 --save-dev'),
        ('ensure_preset_es2017', 'babel-preset-es2017', 'npm install babel-preset-es2017 --save-dev'),
        ('ensure_preset_latest', 'babel-preset-env', 'npm install babel-preset-env --save-dev'),
        ('ensure_preset_babili', 'babel-preset-babili', 'npm install babel-preset-babili --save-dev'),
        ('ensure_babelify', 'babelify', 'npm install --save-dev babelify --no-color'),
    ],
)
def test_ensure_node_dependency(
        monkeypatch, tmp_path, function_name, needle, install_command):
    ctx = make_context(tmp_path)
    monkeypatch.setattr(jstools.runners, 'run', lambda command: '')
    function = getattr(jstools, function_name)

    assert function(ctx) is None
    assert ctx.run.call_args.args[0] == install_command

    ctx.run.reset_mock()
    monkeypatch.setattr(jstools.runners, 'run', lambda command: needle)
    assert function(ctx) is True
    ctx.run.assert_not_called()


def test_ensure_babel_minify(monkeypatch, tmp_path):
    ctx = make_context(tmp_path)
    monkeypatch.setattr(jstools.runners, 'run', lambda command: '')
    assert jstools.ensure_babel_minify(ctx) is None
    ctx.run.assert_called_once()

    monkeypatch.setattr(jstools.runners, 'run', lambda command: 'minify')
    assert jstools.ensure_babel_minify(ctx) is True


def test_browserify_builds_command_and_normalizes_newlines(monkeypatch, tmp_path):
    destination = tmp_path / 'bundle.js'
    ctx = make_context(tmp_path)

    monkeypatch.setattr(jstools, 'ensure_package_json', Mock(return_value=True))
    monkeypatch.setattr(jstools, 'ensure_node_modules', Mock(return_value=True))
    monkeypatch.setattr(jstools, 'ensure_babelify', Mock(return_value=True))
    monkeypatch.setattr(jstools, 'ensure_preset_latest', Mock(return_value=True))

    def run(command):
        destination.write_bytes(b'one\r\ntwo\r\n')

    ctx.run.side_effect = run
    result = jstools.browserify.body(
        ctx,
        'entry.js',
        str(destination),
        babelify=True,
        require=('alpha',),
        external=('beta',),
        entry='main.js',
    )

    assert result == str(destination)
    command = ctx.run.call_args.args[0]
    assert '-t babelify --presets env' in command
    assert '-r "alpha"' in command
    assert '-x "beta"' in command
    assert '-e "main.js"' in command
    assert destination.read_bytes() == b'one\ntwo\n'


def test_minifier_tasks_delegate_to_commands(monkeypatch):
    ctx = SimpleNamespace()
    babili = Mock()
    babel_minify = Mock()
    uglify = Mock()
    monkeypatch.setattr(jstools, 'babilicmd', babili)
    monkeypatch.setattr(jstools, 'babel_minifycmd', babel_minify)
    monkeypatch.setattr(jstools, 'uglifycmd', uglify)

    assert jstools.babili.body(ctx, 'a.js', 'a.min.js') == 'a.min.js'
    babili.assert_called_once_with(ctx, src='a.js', dst='a.min.js')

    assert jstools.babel_minify.body(ctx, 'a.js', 'a.min.js') == 'a.min.js'
    assert babel_minify.call_args.kwargs['keepFnName'] is True
    assert babel_minify.call_args.kwargs['mangle'] is False

    assert jstools.uglifyjs.body(
        ctx, 'a.js', 'a.min.js', compress=False, mangle=False
    ) == 'a.min.js'
    uglify.assert_called_once_with(
        ctx,
        src='a.js',
        dst='a.min.js',
        compress=False,
        mangle=False,
    )


def test_buildjs_routes_optional_processing(monkeypatch):
    ctx = SimpleNamespace()
    browserify = Mock(return_value='bundle.js')
    uglify = Mock(return_value='bundle.min.js')
    copy = Mock(return_value='bundle-1.0.js')
    monkeypatch.setattr(jstools, 'browserify', browserify)
    monkeypatch.setattr(jstools, 'uglifyjs', uglify)
    monkeypatch.setattr(jstools, 'copy_to_version', copy)

    result = jstools.buildjs.body(
        ctx,
        'entry.jsx',
        'bundle.js',
        browserify=True,
        uglify=True,
        force=True,
        require=('dependency',),
    )

    assert result == 'bundle-1.0.js'
    assert browserify.call_args.kwargs['babelify'] is True
    uglify.assert_called_once_with(ctx, 'bundle.js', 'bundle.min.js')
    copy.assert_called_once_with(ctx, 'bundle.min.js', force=True)

    assert jstools.buildjs.body(ctx, 'entry.js', 'bundle.js') == 'bundle.js'


def test_version_js_delegates(monkeypatch):
    copy = Mock(return_value='app-1.2.3.js')
    monkeypatch.setattr(jstools, 'copy_to_version', copy)
    ctx = SimpleNamespace()
    assert jstools.version_js(ctx, 'app.js', kind='hash', force=True) == (
        'app-1.2.3.js'
    )
    copy.assert_called_once_with(ctx, 'app.js', kind='hash', force=True)
