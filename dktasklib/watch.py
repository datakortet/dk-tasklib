# -*- coding: utf-8 -*-
"""
Usage::

    @task
    def watch(ctx):
        watcher = Watcher(ctx)
        watcher.watch_file(
            name='{pkg.sourcedir}/less/{pkg.name}.less',
            action=lambda e: build(ctx, less=True)
        )
        watcher.watch_directory(
            path='{pkg.sourcedir}/js', ext='.jsx',
            action=lambda e: build(ctx, js=True)
        )
        watcher.watch_directory(
            path='{pkg.docsdir}', ext='.rst',
            action=lambda e: build(ctx, docs=True)
        )
        watcher.start()

    ns = Collection(..., watch, ...)
    ns.configure({
        'pkg': Package()
    })

"""
import time
from dkfileutils.path import Path
from invoke import ctask as task
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from dktasklib import Package


class FileModified(FileSystemEventHandler):
    def __init__(self, ctx, fname, action):
        super(FileModified, self).__init__()
        self.ctx = ctx
        self.fname = Path(fname.format(pkg=ctx.pkg)).abspath()
        self.action = action

    def on_modified(self, event):
        if event.src_path != self.fname:
            return
        self.action(event)


class DirectoryModified(FileSystemEventHandler):
    def __init__(self, ctx, path, ext, action):
        super(DirectoryModified, self).__init__()
        self.ctx = ctx
        self.path = Path(path.format(pkg=ctx.pkg)).abspath()
        self.ext = ext
        self.action = action

    def on_modified(self, event):
        if not event.src_path.startswith(self.path):
            return
        if self.ext and not event.src_path.endswith(self.ext):
            return
        self.action(event)


class Watcher(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.observer = Observer()

    def watch_file(self, name, action):
        self.observer.schedule(
            FileModified(self.ctx, name, action),
            self.ctx.pkg.root,
            recursive=True
        )

    def watch_directory(self, path, ext, action):
        self.observer.schedule(
            DirectoryModified(self.ctx, path, ext, action),
            self.ctx.pkg.root,
            recursive=True
        )

    def start(self):
        self.observer.start()
        try:
            while 1:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
