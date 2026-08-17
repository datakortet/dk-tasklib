from unittest.mock import Mock

from dktasklib import help as help_tasks


def test_help_tasks_delegate_to_invoke():
    context = Mock()
    help_tasks.help.body(context)
    help_tasks.list.body(context)
    assert [call.args[0] for call in context.run.call_args_list] == [
        'invoke --help',
        'invoke --list',
    ]
