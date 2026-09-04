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


def test_build_all_routes_less_docs_and_static(monkeypatch, tmp_path):
    context = make_context(tmp_path)
    source = context.pkg.source_less / 'sample.less'
    source.dirname().makedirs()
    source.write('.sample {}')
    less_rule = Mock()
    docs = Mock()
    collectstatic = Mock()
    monkeypatch.setattr(taskbase.lessc, 'LessRule', less_rule)
    monkeypatch.setattr(taskbase.doctools, 'build', docs)
    monkeypatch.setattr(taskbase, 'collectstatic', collectstatic)
    monkeypatch.setattr(taskbase, 'WARN_ABOUT_SETTINGS', False)
    monkeypatch.setattr(taskbase, 'HAVE_SETTINGS', True)
    monkeypatch.setattr(taskbase, 'DJANGO_SETTINGS_MODULE', 'sample.settings')
    monkeypatch.setattr(taskbase, 'changed', lambda path: True)

    taskbase.build.body(context, force=True)

    less_rule.assert_called_once()
    docs.assert_called_once_with(context, force=True)
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

    assert watcher.watch_directory.call_count == 2
    paths = [call.kwargs['path'] for call in watcher.watch_directory.call_args_list]
    assert paths == ['{pkg.source_less}', '{pkg.docs}']
    watcher.start.assert_called_once_with()
