import base64
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

from dktasklib import npm, urlinliner


def test_inline_data_and_file(tmp_path, capsys):
    assert urlinliner.inline_data(b'abc') == (
        'data:image/png;base64,' + base64.b64encode(b'abc').decode('ascii')
    )
    assert urlinliner.inline_data(b'x' * (10 * 1024 + 1), name='large.png') == (
        'large.png'
    )
    assert 'is too big' in capsys.readouterr().out

    image = tmp_path / 'icon.gif'
    image.write_bytes(b'gif')
    assert urlinliner.inline_file(str(image)).startswith('data:image/gif;base64,')


def test_inline_url_closes_response(monkeypatch):
    response = Mock()
    response.read.return_value = b'image'
    response.headers = {'Content-Type': 'image/svg+xml'}
    manager = Mock()
    manager.__enter__ = Mock(return_value=response)
    manager.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(urlinliner, 'urlopen', Mock(return_value=manager))

    result = urlinliner.inline_url('https://example.test/icon.svg')

    assert result.startswith('data:image/svg+xml;base64,')
    manager.__exit__.assert_called_once()


def test_inline_compiles_local_and_remote_references(monkeypatch, tmp_path):
    image = tmp_path / 'icon.png'
    image.write_bytes(b'png')
    source = tmp_path / 'theme.less.inline'
    source.write_text(
        f'@local: "{image}";\n'
        '@remote: "https://example.test/remote.png";\n'
        '.rule { color: red; }\n'
    )
    monkeypatch.setattr(
        urlinliner,
        'inline_url',
        Mock(return_value='data:image/png;base64,remote'),
    )

    urlinliner.inline.body(SimpleNamespace(), str(source))

    output = (tmp_path / 'theme.less').read_text()
    assert '@local: "data:image/png;base64,' in output
    assert '@remote: "data:image/png;base64,remote";' in output
    assert '.rule { color: red; }' in output


def test_list_urls(monkeypatch, tmp_path, capsys):
    stylesheet = tmp_path / 'style.css'
    stylesheet.write_text('a { background: url(one.png) } b { src: url("two.woff") }')
    urlinliner.list_urls.body(SimpleNamespace(), str(stylesheet))
    assert capsys.readouterr().out.splitlines() == ['one.png', '"two.woff"']


def test_npm_and_global_package(monkeypatch):
    monkeypatch.setattr(npm.exe, 'find', Mock(return_value='npm.exe'))
    check_output = Mock(return_value=b'package list')
    monkeypatch.setattr(npm.subprocess, 'check_output', check_output)
    assert npm.npm('ls') == 'package list'
    check_output.assert_called_once_with('npm ls', shell=True)

    monkeypatch.setattr(npm, 'npm', Mock(return_value='installed'))
    assert npm.global_package('example') is True
    monkeypatch.setattr(
        npm,
        'npm',
        Mock(side_effect=subprocess.CalledProcessError(1, 'npm')),
    )
    assert npm.global_package('missing') is False
