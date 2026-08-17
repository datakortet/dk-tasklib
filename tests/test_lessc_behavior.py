from types import SimpleNamespace
from unittest.mock import Mock

import invoke
from dkfileutils.path import Path

from dktasklib import lessc


def make_context(tmp_path):
    root = Path(str(tmp_path))
    package = SimpleNamespace(
        root=root,
        name='sample',
        source=root / 'sample',
    )
    context = invoke.Context(config=invoke.Config(overrides={'pkg': package}))
    return context


def test_less_rule_skips_missing_and_unchanged_sources(
        monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    context = make_context(tmp_path)
    command = Mock()
    monkeypatch.setattr(lessc, 'lessc', command)

    rule = lessc.LessRule.body()
    rule.ctx = context
    assert rule() is None
    assert 'Missing source' in capsys.readouterr().out

    source = context.pkg.source / 'less' / 'sample.less'
    source.dirname().makedirs()
    source.write('.sample {}')
    monkeypatch.setattr(
        lessc,
        'Directory',
        lambda path: SimpleNamespace(changed=lambda glob: False),
    )
    assert rule() is None
    assert 'No changes' in capsys.readouterr().out
    command.assert_not_called()


def test_less_rule_inlines_builds_and_copies(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    context = make_context(tmp_path)
    source = context.pkg.source / 'less' / 'sample.less'
    source.dirname().makedirs()
    source.write('.sample {}')
    inline_source = source.dirname() / 'icons.inline'
    inline_source.write('@icon: "icon.png";')
    command = Mock()
    inline = Mock()
    copy = Mock()
    monkeypatch.setattr(lessc, 'lessc', command)
    monkeypatch.setattr(lessc.urlinliner, 'inline', inline)
    monkeypatch.setattr(lessc, 'copy', copy)
    monkeypatch.setattr(lessc, 'get_version', lambda ctx, source, kind: '1.2.3')
    monkeypatch.setattr(
        lessc,
        'Directory',
        lambda path: SimpleNamespace(changed=lambda glob: True),
    )

    rule = lessc.LessRule.body(import_fname='templates/sample-css.html')
    rule.ctx = context
    destination = str(
        context.pkg.source / 'static' / 'sample' / 'css' /
        'sample-{version}.min.css'
    )
    result = rule(
        src=str(source),
        dst=destination,
        version='hash',
        bootstrap=True,
        force=True,
        path=['vendor'],
    )

    assert result.endswith('sample-1.2.3.min.css')
    inline.assert_called_once()
    assert command.call_args.kwargs['include_path'][0] == 'vendor'
    assert lessc.LessRule.body.bootstrap_src in command.call_args.kwargs['include_path']
    copy.assert_called_once()


def test_less_rule_can_disable_bootstrap(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    context = make_context(tmp_path)
    source = context.pkg.source / 'less' / 'sample.less'
    source.dirname().makedirs()
    source.write('.sample {}')
    command = Mock()
    monkeypatch.setattr(lessc, 'lessc', command)
    monkeypatch.setattr(lessc, 'copy', Mock())
    monkeypatch.setattr(lessc, 'get_version', lambda ctx, source, kind: '1.0')
    monkeypatch.setattr(
        lessc,
        'Directory',
        lambda path: SimpleNamespace(changed=lambda glob: True),
    )

    rule = lessc.LessRule.body()
    rule.ctx = context
    rule(src=str(source), dst='style-{version}.css', bootstrap=False, force=True)
    assert command.call_args.kwargs['include_path'] == []
