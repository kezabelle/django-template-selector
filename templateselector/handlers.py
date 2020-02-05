# -*- coding: utf-8 -*-
from django.template.loaders import app_directories, filesystem, cached
from os import scandir

__all__ = ['get_results_from_registry']


def scandir_recursive(path):
    for item in scandir(path):
        yield item
        if item.is_dir(follow_symlinks=False):
            for subitem in scandir_recursive(item.path):
                yield subitem

usable_loaders = {}

def from_filesystem(instance):
    dirs = instance.get_dirs()
    for directory in dirs:
        strip_first = len(directory)
        for item in scandir_recursive(directory):
            if item.is_file():
                yield item.path[strip_first+1:]

def from_cached(instance):
    """
    Just go and look at the registry again using the child loaders...
    """
    loaders = instance.loaders
    for result in get_results_from_registry(loaders):
        yield result

usable_loaders[app_directories.Loader] = from_filesystem
usable_loaders[filesystem.Loader] = from_filesystem
usable_loaders[cached.Loader] = from_cached


def get_results_from_registry(loaders):
    for loader in loaders:
        cls = loader.__class__
        if cls in usable_loaders:
            finder = usable_loaders[cls]
            for result in finder(instance=loader):
                yield result
