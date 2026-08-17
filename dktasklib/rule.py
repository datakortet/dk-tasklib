# -*- coding: utf-8 -*-

import invoke


class BuildRule(object):
    requires = []
    after = []
    _temp_mark = _perm_mark = False

    def __init__(self, *args, **kwargs):
        # print "name:", self.__class__.__name__
        # print "ARGS:", args
        # print "KW:", kwargs
        self.ctx = None
        self.kwargs = kwargs
        self.args = ()
        if len(args) == 0:
            return

        ctx = None
        first, rest = args[0], args[1:]
        if isinstance(first, invoke.Context):
            ctx = first
            self.args = rest
        else:
            self.args = args

        if ctx is not None:
            self.run(ctx)

    def run(self, ctx):
        self.ctx = ctx
        for task_obj in self.topsort(self.requires):
            task_obj.run(ctx)

        if self.needs_to_run():
            self(*self.args, **self.kwargs)
            for task_obj in self.topsort(self.after):
                task_obj.run(ctx)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def needs_to_run(self):
        return True

    def topsort(self, tasklist):
        """Topological sort
        """
        permanent = set()
        temporary = set()
        res = []

        def visit(task):
            name = id(task)
            if name in temporary:
                raise ValueError("Circularity", name, res)
            if name in permanent:
                return
            temporary.add(name)
            for dependency in task.requires:
                visit(dependency)
            permanent.add(name)
            temporary.remove(name)
            res.append(task)

        for task in tasklist:
            visit(task)
        return res


# @task
# class CreateFoo(BuildRule):
#     """Create foo.txt
#     """
#     requires = [FileExists('foo.txt')]
#
#     def needs_to_run(self):
#         # return False
#         return not os.path.exists('foo.txt') or int(open('foo.txt').read()) < time.time()
#
#     def __call__(self, name):
#         print "name:", name
#         with open('foo.txt', 'w') as fp:
#             print >>fp, int(time.time())
#         self.ctx.run('echo foo')
#         print 'foo:', open('foo.txt').read()
