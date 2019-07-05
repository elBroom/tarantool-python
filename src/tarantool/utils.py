# -*- coding: utf-8 -*-
# pylint: disable=C0301,W0105,W0401,W0614
import sys

py3 = sys.version_info.major >= 3
if py3:
    long = int
    basestring = str


def check_key(*args, **kwargs):
    if 'first' not in kwargs:
        kwargs['first'] = True
    if 'select' not in kwargs:
        kwargs['select'] = False
    if len(args) == 0 and kwargs['select']:
        return []
    if len(args) == 1:
        if isinstance(args[0], (list, tuple)) and kwargs['first']:
            kwargs['first'] = False
            return check_key(*args[0], **kwargs)
        elif args[0] is None and kwargs['select']:
            return []
    for key in args:
        assert isinstance(key, (int, long, basestring))
    return list(args)
