# coding: utf-8
# Created on: 04.01.2018
# Author: Roman Miroshnychenko aka Roman V.M. (roman1972@gmail.com)

import sys
import inspect

__all__ = ['PY2', 'py2_encode', 'py2_decode', 'patch_module', 'encode_decode']

PY2 = sys.version_info[0] == 2  #: ``True`` for Python 2


def py2_encode(s, encoding='utf-8'):
    """
    Encode Python 2 ``unicode`` to ``str``

    In Python 3 the string is not changed.
    """
    if PY2 and isinstance(s, unicode):
        s = s.encode(encoding)
    return s


def py2_decode(s, encoding='utf-8'):
    """
    Decode Python 2 ``str`` to ``unicode``

    In Python 3 the string is not changed.
    """
    if PY2 and isinstance(s, str):
        s = s.decode(encoding)
    return s


def encode_decode(func):
    """
    A decorator that encodes all unicode function arguments to UTF-8-encoded
    byte strings and decodes function str return value to unicode.

    This decorator is no-op in Python 3.

    :param func: wrapped function or a method
    :type func: types.FunctionType or types.MethodType
    :return: function wrapper
    :rtype: types.FunctionType
    """
    if PY2:
        def wrapper(*args, **kwargs):
            mod_args = tuple((py2_encode(item) for item in args))
            mod_kwargs = {key: py2_encode(value) for key, value
                          in kwargs.iteritems()}
            return py2_decode(func(*mod_args, **mod_kwargs))
        return wrapper
    return func


def _wrap_class(cls):
    class ClassWrapper(cls):
        pass
    ClassWrapper.__name__ = 'wrapped_{0}'.format(cls.__name__)
    return ClassWrapper


def patch_module(mod):
    """
    Applies :func:`encode_decode` decorator to all
    functions and classes in a module

    :param mod: module for patching
    :type mod: types.ModuleType
    """
    for name, obj in inspect.getmembers(mod):
        if inspect.isbuiltin(obj):
            setattr(mod, name, encode_decode(obj))
        elif inspect.isclass(obj):
            # We cannot patch methods of Kodi classes directly.
            cls = _wrap_class(obj)
            for memb_name, member in inspect.getmembers(cls):
                # Do not patch special methods!
                if (not memb_name.startswith('__') and
                        inspect.ismethoddescriptor(member)):
                    setattr(cls, memb_name, encode_decode(member))
            setattr(mod, name, cls)
