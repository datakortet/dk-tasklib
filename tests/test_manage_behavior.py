from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from dkfileutils.path import Path

from dktasklib import manage


def test_manage_resolves_path_and_environment(monkeypatch, tmp_path):
    monkeypatch.delenv('DJANGO_SETTINGS_MODULE', raising=False)
    settings_dir = tmp_path / 'project'
    settings_dir.mkdir()
    (settings_dir / 'manage.py').write_text('')
    monkeypatch.setattr(manage, 'find_pymodule', lambda settings: settings_dir)
    monkeypatch.setattr(manage, 'pfind', lambda path, name: settings_dir / name)
    run = Mock()
    monkeypatch.setattr(manage, 'run', run)

    manage.manage.body(SimpleNamespace(), 'check', settings='sample.settings')

    run.assert_called_once_with('python manage.py check')
    assert 'DJANGO_SETTINGS_MODULE' not in manage.os.environ

    manage.manage.body(
        SimpleNamespace(),
        'migrate',
        settings=None,
        manage_path=settings_dir,
        venv='dev',
    )
    run.assert_called_with('vex dev python manage.py migrate --traceback')


def make_package(tmp_path):
    django_static = Path(str(tmp_path / 'package-static'))
    django_static.makedirs()
    return SimpleNamespace(
        django_static=django_static,
        django_settings_module='sample.settings',
    )


def test_collectstatic_skips_unchanged_directory(monkeypatch, tmp_path, capsys):
    package = make_package(tmp_path)
    context = SimpleNamespace(pkg=package)
    monkeypatch.setattr(
        manage,
        'Directory',
        lambda path: SimpleNamespace(changed=lambda: False),
    )
    operation = Mock()
    monkeypatch.setattr(manage, 'manage', operation)

    manage.collectstatic.body(context)

    operation.assert_not_called()
    assert 'Skipping collectstic' in capsys.readouterr().out


def test_collectstatic_runs_and_records_changes(monkeypatch, tmp_path):
    package = make_package(tmp_path)
    context = SimpleNamespace(pkg=package)
    monkeypatch.setattr(
        manage,
        'Directory',
        lambda path: SimpleNamespace(changed=lambda: True),
    )
    operation = Mock()
    recorded = Mock()
    monkeypatch.setattr(manage, 'manage', operation)
    monkeypatch.setattr(manage, 'changed', recorded)

    manage.collectstatic.body(context, clobber=True, venv='dev')

    operation.assert_called_once_with(
        context,
        'collectstatic --noinput',
        settings='sample.settings',
        venv='dev',
    )
    recorded.assert_called_once_with(package.django_static)


def test_collectstatic_detects_changed_versioned_resources(
        monkeypatch, tmp_path, capsys):
    srv = tmp_path / 'srv'
    monkeypatch.setenv('SRV', str(srv))
    package = make_package(tmp_path)
    generated = package.django_static / 'js' / 'app-1.min.js'
    generated.dirname().makedirs()
    generated.write('new')
    published = Path(str(srv)) / 'data' / 'static' / 'js' / 'app-1.min.js'
    published.dirname().makedirs()
    published.write('old')
    context = SimpleNamespace(pkg=package)
    monkeypatch.setattr(
        manage,
        'Directory',
        lambda path: SimpleNamespace(changed=lambda: True),
    )

    with pytest.raises(SystemExit):
        manage.collectstatic.body(context)
    assert 'versioned file has changes' in capsys.readouterr().out


def test_collectstatic_creates_package_and_uses_default_settings(
        monkeypatch, tmp_path):
    package = make_package(tmp_path)
    del package.django_settings_module

    class Context:
        pass

    context = Context()
    monkeypatch.setattr(manage, 'Package', lambda: package)
    monkeypatch.setattr(
        manage,
        'Directory',
        lambda path: SimpleNamespace(changed=lambda: True),
    )
    operation = Mock()
    monkeypatch.setattr(manage, 'manage', operation)
    monkeypatch.setattr(manage, 'changed', Mock())

    manage.collectstatic.body(context, clobber=True)

    assert context.pkg is package
    assert operation.call_args.kwargs['settings'] == manage.DEFAULT_SETTINGS_MODULE
