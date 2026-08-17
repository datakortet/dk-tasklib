import os

import pytest

from dktasklib import utils


def test_format_table_supports_alignment_multiline_and_row_spacing():
    table = utils.format_table(
        [
            {'name': 'alpha', 'value': 'one\ntwo'},
            {'name': 'b', 'value': 'three'},
        ],
        utils.Column(field='name', align='right'),
        utils.Column(field='value', title='result', align='center'),
        rowspace=True,
    )

    assert 'name  result' in table
    assert 'alpha  one ' in table
    assert '       two ' in table
    assert '    b three' in table


def test_format_table_accepts_object_field_getter():
    class Item:
        name = 'sample'

    table = utils.format_table(
        [Item()],
        utils.Column(field='name', format=str.upper),
        get_field=lambda field: lambda item: getattr(item, field),
    )
    assert 'SAMPLE' in table


def test_destination_timestamp_checks(tmp_path):
    source = tmp_path / 'source.txt'
    destination = tmp_path / 'destination.txt'
    source.write_text('source')

    assert not utils.dest_is_newer_than_source(source, destination)
    destination.write_text('destination')
    os.utime(source, (1, 1))
    os.utime(destination, (2, 2))
    assert utils.dest_is_newer_than_source(source, destination)

    source.unlink()
    with pytest.raises(ValueError, match='Source does not exist'):
        utils.dest_is_newer_than_source(source, destination)


def test_formatting_and_filename_helpers():
    package = type('Package', (), {'name': 'demo'})()
    assert utils.fmt('{pkg.name}/{missing.value}', {'pkg': package}) == (
        'demo/{missing.value}'
    )
    assert utils.switch_extension('path/demo.less', '.css') == 'path/demo.css'
    assert utils.switch_extension('path/demo.less', '.css', '.less') == 'path/demo.css'
    with pytest.raises(AssertionError):
        utils.switch_extension('path/demo.less', '.css', '.scss')
    assert utils.filename('path/demo.less') == 'demo.less'


def test_message_reports_success_and_failure(capsys):
    with utils.message('work'):
        pass
    assert 'ok: work' in capsys.readouterr().out

    with pytest.raises(RuntimeError):
        with utils.message('work'):
            raise RuntimeError('boom')
    assert 'error =====> work' in capsys.readouterr().out


def test_environment_is_restored_after_success_and_failure(monkeypatch):
    monkeypatch.setenv('DKTASKLIB_EXISTING', 'before')
    monkeypatch.delenv('DKTASKLIB_NEW', raising=False)

    with utils.env(DKTASKLIB_EXISTING='during', DKTASKLIB_NEW=42):
        assert os.environ['DKTASKLIB_EXISTING'] == 'during'
        assert os.environ['DKTASKLIB_NEW'] == '42'

    assert os.environ['DKTASKLIB_EXISTING'] == 'before'
    assert 'DKTASKLIB_NEW' not in os.environ

    with pytest.raises(RuntimeError):
        with utils.env(DKTASKLIB_NEW='during'):
            raise RuntimeError('boom')
    assert 'DKTASKLIB_NEW' not in os.environ


def test_cd_is_restored_after_success_and_failure(tmp_path):
    original = os.getcwd()
    with utils.cd(tmp_path):
        assert os.getcwd() == str(tmp_path)
    assert os.getcwd() == original

    with pytest.raises(RuntimeError):
        with utils.cd(tmp_path):
            raise RuntimeError('boom')
    assert os.getcwd() == original


def test_find_python_package_and_module(monkeypatch, tmp_path):
    package_dir = tmp_path / 'samplepkg'
    package_dir.mkdir()
    (package_dir / '__init__.py').write_text('')
    module_dir = tmp_path / 'modules'
    module_dir.mkdir()
    (module_dir / 'single.py').write_text('')
    monkeypatch.setattr(utils.sys, 'path', ['', str(tmp_path), str(module_dir)])

    assert os.path.normcase(utils.find_pymodule('samplepkg.settings')) == (
        os.path.normcase(str(package_dir))
    )
    assert os.path.normcase(utils.find_pymodule('single')) == (
        os.path.normcase(str(module_dir))
    )
    with pytest.raises(ValueError, match='Path not found'):
        utils.find_pymodule('missing')
