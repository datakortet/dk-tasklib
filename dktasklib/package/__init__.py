from dktasklib.wintask import task
from .package_interface import Package
from ..utils import format_table, Column


@task
def package(ctx):
    """Print detected package directories.
    """
    pkg = ctx.pkg if hasattr(ctx, 'pkg') else Package()

    def row(attribute, value, description=''):
        return dict(attribute=attribute, value=value, description=description)

    print("The dk-tasklib Package object thinks your code has the following layout:")

    print(format_table(
        [
            row('package_name', pkg.package_name, '(repo/pip-installable name)'),
            row('name', pkg.name, '(importable name)'),
            row('root', pkg.root, '(wc)'),
            row('source', pkg.source, '(source directory)'),
            row('source_js', pkg.source_js, '(js source directory)'),
            row('source_less', pkg.source_less, '(less source directory)'),
            row('docs', pkg.docs, '(docs directory)'),
            row('django?', 'yes' if pkg.is_django() else 'no', '(django?)'),
        ],
        Column(field='attribute'),
        Column(field='value'),
        Column(field='description'),
    ))
