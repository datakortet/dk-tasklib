from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from dkfileutils.path import Path

from dktasklib.entry_points import taskbase


def make_context(tmp_path):
    root = Path(str(tmp_path))
    package = SimpleNamespace(
        root=root,
        name='sample',
        source_less=root / 'sample' / 'less',
        source_js=root / 'sample' / 'js',
        django_static=root / 'sample' / 'static',
        docs=root / 'docs',
    )
    return SimpleNamespace(pkg=package)


def test_build_js_builds_each_configured_source(monkeypatch, tmp_path):
    context = make_context(tmp_path)
    babel = Mock()
    monkeypatch.setattr(taskbase.jstools, 'babel', babel, raising=False)
    monkeypatch.setattr(taskbase, 'JSX_FILENAMES', ['one.jsx', 'two.jsx'])

    taskbase.build_js.body(context, force=True)

    assert babel.call_count == 2
    assert babel.call_args_list[0].args[1:] == (
        '{pkg.source_js}/one.jsx',
        '{pkg.django_static}/{pkg.name}/js/one.jsx.js',
    )
    assert babel.call_args_list[0].kwargs['force'] is True


def test_build_all_routes_less_docs_js_and_static(monkeypatch, tmp_path):
    context = make_context(tmp_path)
    source = context.pkg.source_less / 'sample.less'
    source.dirname().makedirs()
    source.write('.sample {}')
    less_rule = Mock()
    docs = Mock()
    javascript = Mock()
    collectstatic = Mock()
    monkeypatch.setattr(taskbase.lessc, 'LessRule', less_rule)
    monkeypatch.setattr(taskbase.doctools, 'build', docs)
    monkeypatch.setattr(taskbase, 'build_js', javascript)
    monkeypatch.setattr(taskbase, 'collectstatic', collectstatic)
    monkeypatch.setattr(taskbase, 'WARN_ABOUT_SETTINGS', False)
    monkeypatch.setattr(taskbase, 'HAVE_SETTINGS', True)
    monkeypatch.setattr(taskbase, 'DJANGO_SETTINGS_MODULE', 'sample.settings')
    monkeypatch.setattr(taskbase, 'changed', lambda path: True)

    taskbase.build.body(context, force=True)

    less_rule.assert_called_once()
    docs.assert_called_once_with(context, force=True)
    javascript.assert_called_once_with(context, True)
    collectstatic.assert_called_once_with(
        context,
        'sample.settings',
        force=True,
    )


def test_build_selected_missing_less_and_docs_warning(
        monkeypatch, tmp_path):
    context = make_context(tmp_path)
    monkeypatch.setattr(taskbase, 'WARN_ABOUT_SETTINGS', True)
    monkeypatch.setattr(taskbase, 'HAVE_SETTINGS', False)
    docs = Mock()
    monkeypatch.setattr(taskbase.doctools, 'build', docs)

    with pytest.warns(UserWarning, match='no file'):
        taskbase.build.body(context, less=True)
    with pytest.warns(UserWarning, match='dummy settings'):
        taskbase.build.body(context, docs=True)
    docs.assert_called_once_with(context, force=False)


def test_watch_registers_each_source(monkeypatch, tmp_path):
    context = make_context(tmp_path)
    watcher = Mock()
    monkeypatch.setattr(taskbase, 'Watcher', Mock(return_value=watcher))

    taskbase.watch.body(context)

    assert watcher.watch_directory.call_count == 3
    paths = [call.kwargs['path'] for call in watcher.watch_directory.call_args_list]
    assert paths == ['{pkg.source_less}', '{pkg.source_js}', '{pkg.docs}']
    watcher.start.assert_called_once_with()
