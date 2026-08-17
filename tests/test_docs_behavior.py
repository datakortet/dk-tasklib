import datetime
import os
from types import SimpleNamespace
from unittest.mock import Mock

import invoke
import pytest
from dkfileutils.path import Path

from dktasklib import docs


def make_context(tmp_path):
    root = Path(str(tmp_path))
    package = SimpleNamespace(
        root=root,
        docs=root / 'docs',
        source=root / 'sample',
        version='1.2.3',
        name='sample',
        get=Mock(return_value=''),
    )
    context = invoke.Context(config=invoke.Config(overrides={'pkg': package}))
    context.run = Mock()
    return context


def test_clean_only_removes_nonempty_build(monkeypatch, tmp_path):
    context = make_context(tmp_path)
    build = tmp_path / 'build' / 'docs'
    build.mkdir(parents=True)

    docs._clean.body(context)
    context.run.assert_not_called()

    (build / 'index.html').write_text('content')
    docs._clean.body(context)
    assert context.run.call_args.args[0].lower() == f'rm -rf {build}/*'.lower()


def test_browse_opens_generated_index(monkeypatch, tmp_path):
    context = make_context(tmp_path)
    open_new = Mock()
    monkeypatch.setattr(docs.webbrowser, 'open_new', open_new)
    docs._browse.body(context)
    assert open_new.call_args.args[0].endswith(
        os.path.join('build', 'docs', 'index.html')
    )


def test_initdocs_prints_current_command(monkeypatch, tmp_path, capsys):
    context = make_context(tmp_path)
    monkeypatch.setattr(docs, 'Package', lambda: context.pkg)
    docs.initdocs.body(context, author='Ada Lovelace', language='en')
    output = capsys.readouterr().out
    assert 'sphinx-quickstart' in output
    assert '-a "Ada Lovelace"' in output
    assert '-v 1.2.3' in output


def test_create_docs_directory_and_index(monkeypatch, tmp_path):
    context = make_context(tmp_path)
    monkeypatch.setattr(docs, 'run', lambda command: 'Ada Lovelace\n')

    docs.create_docs_directory.body(context)
    docs.create_index.body(context)

    configuration = (tmp_path / 'docs' / 'conf.py').read_text()
    assert "project = u'sample'" in configuration
    assert "version = u'1.2.3'" in configuration
    assert str(datetime.date.today().year) in configuration
    index = (tmp_path / 'docs' / 'index.rst').read_text()
    assert 'sample' in index

    with pytest.raises(SystemExit):
        docs.create_docs_directory.body(context)
    with pytest.raises(SystemExit):
        docs.create_index.body(context)

    docs.create_docs_directory.body(context, force=True)
    docs.create_index.body(context, force=True)


def test_make_api_docs_prefixes_files(monkeypatch, tmp_path, capsys):
    context = make_context(tmp_path)
    context.pkg.docs.makedirs('api')
    (tmp_path / 'docs' / 'api' / 'sample.rst').write_text(
        'sample\n======\n\n.. automodule:: sample\n'
    )
    (tmp_path / 'docs' / 'index.rst').write_text('sample docs')
    copy = Mock()
    monkeypatch.setattr(docs.concat, 'copy', copy)

    docs.make_api_docs.body(context, prefix='legacy.')

    renamed = tmp_path / 'docs' / 'api' / 'legacy.sample.rst'
    assert renamed.exists()
    assert '.. automodule:: legacy.sample' in renamed.read_text()
    assert context.run.call_count == 3
    copy.assert_called_once()
    assert 'WARNING: you need to include' in capsys.readouterr().out


def test_build_handles_unchanged_and_full_options(monkeypatch, tmp_path, capsys):
    context = make_context(tmp_path)
    context.pkg.docs.makedirs()
    monkeypatch.setattr(docs, 'changed', Mock(return_value=False))

    assert docs.build.body(context) is None
    assert 'No changes detected' in capsys.readouterr().out

    monkeypatch.setattr(docs, 'changed', Mock(return_value=True))
    clean = Mock()
    api = Mock()
    browse = Mock()
    monkeypatch.setattr(docs, '_clean', clean)
    monkeypatch.setattr(docs, 'make_api_docs', api)
    monkeypatch.setattr(docs, '_browse', browse)
    context.pkg.get.return_value = 'sample.settings'

    docs.build.body(
        context,
        clean=True,
        browse=True,
        warn=True,
        builder='linkcheck',
        force=True,
        opts='-q',
        prefix='legacy.',
    )

    clean.assert_called_once_with(context)
    api.assert_called_once_with(context, force=True, prefix='legacy.')
    command = context.run.call_args.args[0]
    assert '-q -b linkcheck -n -W -a -E' in command
    assert 'DJANGO_SETTINGS_MODULE' in docs.os.environ
    browse.assert_called_once_with(context)


def test_docs_tree_delegates(tmp_path):
    context = make_context(tmp_path)
    docs.tree.body(context)
    assert 'tree -Ca -I' in context.run.call_args.args[0]
