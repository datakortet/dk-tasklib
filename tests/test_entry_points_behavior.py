from argparse import Namespace
from unittest.mock import Mock

import pytest
from dkfileutils.path import Path

from dktasklib.entry_points import dktasklibcmd
from dktasklib.entry_points.pytemplate import PyTemplate


def test_python_template_accepts_text_and_bytes():
    assert PyTemplate(b'##{NAME} $literal').substitute(name='value') == (
        'value $literal'
    )
    assert PyTemplate('##{NAME}').substitute(name='value') == 'value'


def test_install_command_writes_template_and_optional_django(
        monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    django = Mock()
    monkeypatch.setattr(dktasklibcmd, 'add_django_to_docs_conf', django)

    dktasklibcmd.install_cmd(Namespace(force=False, django=True))

    content = (tmp_path / 'tasks.py').read_text()
    assert 'dk-tasklib is a library' in content
    assert dktasklibcmd.__version__ in content
    django.assert_called_once_with()

    with pytest.raises(SystemExit):
        dktasklibcmd.install_cmd(Namespace(force=False, django=False))
    dktasklibcmd.install_cmd(Namespace(force=True, django=False))


def test_create_docs_command_writes_configuration(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    values = {
        'python setup.py --version': '2.3.4',
        'python setup.py --name': 'sample',
        'python setup.py --author': 'Ada Lovelace',
    }
    monkeypatch.setattr(dktasklibcmd, 'run', lambda command: values[command])

    dktasklibcmd.create_docs_cmd(Namespace(force=False))

    configuration = (tmp_path / 'docs' / 'conf.py').read_text()
    assert "project = u'sample'" in configuration
    assert "version = u'2.3.4'" in configuration
    assert "author = u'Ada Lovelace'" in configuration

    with pytest.raises(SystemExit):
        dktasklibcmd.create_docs_cmd(Namespace(force=False))
    dktasklibcmd.create_docs_cmd(Namespace(force=True))


def test_add_django_setup_is_idempotent(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    docs = tmp_path / 'docs'
    docs.mkdir()
    configuration = docs / 'conf.py'
    configuration.write_text('# header\n\nproject = "sample"\n')

    dktasklibcmd.add_django_to_docs_conf()
    assert configuration.read_text().count('django.setup()') == 1
    dktasklibcmd.add_django_to_docs_conf()
    assert 'already contains django.setup()' in capsys.readouterr().out


def test_main_dispatches_and_rejects_unknown(monkeypatch, capsys):
    install = Mock()
    monkeypatch.setattr(dktasklibcmd, 'install_cmd', install)
    dktasklibcmd.main(['install', '--verbose', '--force'])
    assert install.call_args.args[0].force is True
    assert 'ARGS:' in capsys.readouterr().out

    with pytest.raises(SystemExit):
        dktasklibcmd.main(['unknown'])
    assert 'Unknown command: unknown' in capsys.readouterr().out
