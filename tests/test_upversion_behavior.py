from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from dkfileutils.path import Path

from dktasklib import upversion


def test_files_with_version_numbers_uses_package_layout(tmp_path):
    root = Path(str(tmp_path))
    package = SimpleNamespace(root=root, source=root / 'sample')
    files = upversion.files_with_version_numbers(package)
    assert root / 'setup.py' in files
    assert root / 'docs' / 'conf.py' in files
    assert package.source / '_version.py' in files


def test_replace_version_handles_missing_absent_and_present(tmp_path):
    missing = Path(str(tmp_path / 'missing.txt'))
    assert upversion._replace_version(missing, '1.0.0', '1.0.1') is False

    filename = Path(str(tmp_path / 'version.txt'))
    filename.write('no version here')
    assert upversion._replace_version(filename, '1.0.0', '1.0.1') is False

    filename.write('version = 1.0.0\n')
    assert upversion._replace_version(filename, '1.0.0', '1.0.1') == 1
    assert filename.read() == 'version = 1.0.1\n'


@pytest.mark.parametrize(
    ('options', 'expected'),
    [
        ({'patch': True}, '1.2.4'),
        ({'minor': True}, '1.3.0'),
        ({'major': True}, '2.0.0'),
    ],
)
def test_upversion_updates_files(monkeypatch, tmp_path, options, expected):
    root = Path(str(tmp_path))
    version_file = root / 'version.txt'
    version_file.write('1.2.3')
    package = SimpleNamespace(root=root, version='1.2.3', vcs=lambda: '')
    monkeypatch.setattr(upversion, 'Package', lambda: package)
    monkeypatch.setattr(
        upversion,
        'files_with_version_numbers',
        lambda pkg=None: {version_file},
    )
    context = SimpleNamespace()

    assert upversion.upversion.body(context, **options) == expected
    assert version_file.read() == expected


def test_upversion_supports_additional_files_and_git_tag(monkeypatch, tmp_path):
    root = Path(str(tmp_path))
    standard = root / 'version.txt'
    additional = root / 'extra.txt'
    standard.write('1.0.0')
    additional.write('1.0.0')
    package = SimpleNamespace(root=root, version='1.0.0', vcs=lambda: 'git')
    monkeypatch.setattr(upversion, 'Package', lambda: package)
    monkeypatch.setattr(
        upversion,
        'files_with_version_numbers',
        lambda pkg=None: {standard},
    )
    context = SimpleNamespace(versionfiles=['extra.txt'], run=Mock())

    assert upversion.upversion.body(context, patch=True, tag=True) == '1.0.1'
    assert standard.read() == '1.0.1'
    assert additional.read() == '1.0.1'
    assert context.run.call_count == 2
    assert context.run.call_args_list[0].args[0] == (
        'git tag -a v1.0.1 -m "Version 1.0.1"'
    )


def test_update_template_version_creates_and_updates_template(tmp_path):
    root = Path(str(tmp_path))
    class Context(dict):
        __getattr__ = dict.__getitem__

    context = Context(
        pkg=SimpleNamespace(root=root, name='sample', version='2.3.4'),
    )
    rule = upversion.UpdateTemplateVersion()
    rule.ctx = context
    filename = root / 'templates' / 'sample-css.html'

    rule(str(filename))
    content = filename.read()
    assert '{% with "2.3.4" as version %}' in content
    assert 'sample/sample-' in content

    rule.ctx.pkg.version = '2.4.0'
    rule(str(filename))
    assert '{% with "2.4.0" as version %}' in filename.read()
