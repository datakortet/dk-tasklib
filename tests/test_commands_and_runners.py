import subprocess
from unittest.mock import Mock

import invoke
import pytest

from dktasklib import commands, runners


def test_command_builds_arguments_and_options(monkeypatch):
    require = Mock()
    monkeypatch.setattr(commands.exe, 'require', require)
    monkeypatch.setattr(commands.exe, 'find', lambda name: 'my tool')
    command = commands.Command(
        'tool --fixed',
        '{source} {opts} {pos}',
        requirements=('runtime',),
        policy={'negative_bool': 'prefix', 'list_join': ':'},
    )
    ctx = invoke.Context()
    ctx.run = Mock()

    result = command(
        ctx,
        'tail',
        source='input.txt',
        verbose=True,
        cache=False,
        include=['a', 'b'],
        label='hello world',
        count=3,
        empty=[],
    )

    require.assert_called_once_with('runtime')
    assert result.startswith('"my tool" --fixed')
    assert '--verbose' in result
    assert '--no-cache' in result
    assert '--include=a:b' in result
    assert '--label="hello world"' in result
    assert '--count=3' in result
    assert '--empty=[]' in result
    assert result.endswith('tail')
    ctx.run.assert_called_once_with(result, warn=True)

    command._initialize()
    assert require.call_count == 1


def test_command_accepts_first_positional_argument_as_data(monkeypatch):
    monkeypatch.setattr(commands.exe, 'require', Mock())
    monkeypatch.setattr(commands.exe, 'find', lambda name: name)
    run = Mock()
    monkeypatch.setattr(invoke.Context, 'run', run)

    command = commands.Command('tool', '{pos}{opts}')
    assert command('one', 'two', short='x') == 'tool one two --short="x"'
    run.assert_called_once()


def test_command_uses_existing_executable_path(monkeypatch, tmp_path):
    executable = tmp_path / 'tool.exe'
    executable.write_text('placeholder')
    find = Mock()
    monkeypatch.setattr(commands.exe, 'find', find)

    command = commands.Command(str(executable))
    command._initialize()

    assert command.cmd == str(executable)
    find.assert_not_called()


def test_run_returns_decoded_result(monkeypatch):
    monkeypatch.setattr(
        runners.subprocess,
        'check_output',
        lambda command, shell: b'finished\n',
    )

    result = runners.run('build')

    assert result == 'finished\n'
    assert result.cmd == 'build'
    assert result.returncode is None


def test_run_reports_or_raises_failure(monkeypatch):
    error = subprocess.CalledProcessError(7, 'build', output=b'failed\n')

    def fail(command, shell):
        raise error

    monkeypatch.setattr(runners.subprocess, 'check_output', fail)

    result = runners.run('build')
    assert result == 'failed\n'
    assert result.returncode == 7
    assert result.cmd == 'build'

    with pytest.raises(subprocess.CalledProcessError):
        runners.run('build', throw=True)


def test_command_factory_runs_and_supports_dry_run(monkeypatch, capsys):
    run = Mock(return_value='ok')
    monkeypatch.setattr(runners, 'run', run)

    command = runners.command('ignored')
    assert command('deploy', target='two words', verbose=True) == 'ok'
    run.assert_called_once_with('deploy --target="two words" --verbose')

    dry_run = runners.command('ignored', dryrun=True)
    assert dry_run('deploy', target='test') is None
    assert capsys.readouterr().out.strip() == 'deploy --target=test'
