from types import SimpleNamespace
from unittest.mock import Mock

import invoke
import pytest

from dktasklib.rule import BuildRule
from dktasklib import watch


class RecordingRule(BuildRule):
    def __init__(self, name, events, should_run=True, *args, **kwargs):
        self.name = name
        self.events = events
        self.should_run = should_run
        super().__init__(*args, **kwargs)

    def needs_to_run(self):
        return self.should_run

    def __call__(self, *args, **kwargs):
        self.events.append((self.name, args, kwargs))


def test_build_rule_runs_dependencies_action_and_after_tasks():
    events = []
    dependency = RecordingRule('dependency', events)
    action = RecordingRule('action', events)
    after = RecordingRule('after', events)
    action.requires = [dependency]
    action.after = [after]

    action.args = ('argument',)
    action.kwargs = {'option': True}
    action.run(invoke.Context())

    assert [event[0] for event in events] == ['dependency', 'action', 'after']
    assert events[1][1:] == (('argument',), {'option': True})

    events.clear()
    action.should_run = False
    action.run(invoke.Context())
    assert [event[0] for event in events] == ['dependency']


def test_build_rule_constructor_and_not_implemented():
    events = []
    context = invoke.Context()
    RecordingRule('action', events, True, context, 'value', flag=True)
    assert events == [('action', ('value',), {'flag': True})]

    with pytest.raises(NotImplementedError):
        BuildRule()(None)


def test_topological_sort_detects_nested_cycles_and_is_repeatable():
    events = []
    first = RecordingRule('first', events)
    second = RecordingRule('second', events)
    third = RecordingRule('third', events)
    third.requires = [second]
    second.requires = [first]

    assert third.topsort([third]) == [first, second, third]
    assert third.topsort([third]) == [first, second, third]

    first.requires = [third]
    with pytest.raises(ValueError, match='Circularity'):
        third.topsort([third])


def test_file_modified_filters_events(tmp_path):
    target = tmp_path / 'source.txt'
    package = SimpleNamespace(root=str(tmp_path))
    context = SimpleNamespace(pkg=package)
    action = Mock()
    handler = watch.FileModified(context, str(target), action)

    handler.on_modified(SimpleNamespace(src_path=str(tmp_path / 'other.txt')))
    action.assert_not_called()
    event = SimpleNamespace(src_path=str(target))
    handler.on_modified(event)
    action.assert_called_once_with(event)


def test_directory_modified_filters_path_and_extension(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    context = SimpleNamespace(pkg=SimpleNamespace(root=str(tmp_path)))
    action = Mock()
    handler = watch.DirectoryModified(context, str(source), '.js', action)

    handler.on_modified(SimpleNamespace(src_path=str(tmp_path / 'other.js')))
    handler.on_modified(SimpleNamespace(src_path=str(source / 'style.css')))
    action.assert_not_called()
    event = SimpleNamespace(src_path=str(source / 'app.js'))
    handler.on_modified(event)
    action.assert_called_once_with(event)

    any_extension = watch.DirectoryModified(context, str(source), '', action)
    any_extension.on_modified(SimpleNamespace(src_path=str(source / 'style.css')))
    assert action.call_count == 2


def test_watcher_schedules_handlers_and_stops_on_interrupt(monkeypatch, tmp_path):
    context = SimpleNamespace(pkg=SimpleNamespace(root=str(tmp_path)))
    observer = Mock()
    watcher = watch.Watcher(context)
    watcher.observer = observer
    action = Mock()

    watcher.watch_file(str(tmp_path / 'file.txt'), action)
    watcher.watch_directory(str(tmp_path), '.rst', action)

    assert observer.schedule.call_count == 2
    assert observer.schedule.call_args_list[0].kwargs['recursive'] is True

    monkeypatch.setattr(
        watch.time,
        'sleep',
        Mock(side_effect=KeyboardInterrupt),
    )
    watcher.start()
    observer.start.assert_called_once_with()
    observer.stop.assert_called_once_with()
    observer.join.assert_called_once_with()
