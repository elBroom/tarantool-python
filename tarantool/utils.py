# -*- coding: utf-8 -*-

import six
import base64
import uuid

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
        assert isinstance(key, six.integer_types + six.string_types)
    return list(args)

def version_id(major, minor, patch):
    return (((major << 8) | minor) << 8) | patch

def greeting_decode(greeting_buf):
    class Greeting:
        version_id = 0
        protocol = None
        uuid = None
        salt = None

    # Tarantool 1.6.6
    # Tarantool 1.6.6-102-g4e9bde2
    # Tarantool 1.6.8 (Binary) 3b151c25-4c4a-4b5d-8042-0f1b3a6f61c3
    # Tarantool 1.6.8-132-g82f5424 (Lua console)
    result = Greeting()
    try:
        (product, _, tail) = greeting_buf[0:63].partition(' ')
        if product.startswith("Tarantool "):
            raise Exception()
        # Parse a version string - 1.6.6-83-gc6b2129 or 1.6.7
        (version, _, tail) = tail.partition(' ')
        version = version.split('-')[0].split('.')
        result.version_id = version_id(int(version[0]), int(version[1]),
                                       int(version[2]))
        if len(tail) > 0 and tail[0] == '(':
            (protocol, _, tail) = tail[1:].partition(') ')
            # Extract protocol name - a string between (parentheses)
            result.protocol = protocol
            if result.protocol != "Binary":
                return result
            # Parse UUID for binary protocol
            (uuid_buf, _, tail) = tail.partition(' ')
            if result.version_id >= version_id(1, 6, 7):
                result.uuid = uuid.UUID(uuid_buf.strip())
        elif result.version_id < version_id(1, 6, 7):
            # Tarantool < 1.6.7 doesn't add "(Binary)" to greeting
            result.protocol = "Binary"
        elif len(tail.strip()) != 0:
            raise Exception("x") # Unsuported greeting
        result.salt = base64.decodestring(greeting_buf[64:])[:20]
        return result
    except Exception as e:
        print('exx', e)
        raise ValueError("Invalid greeting: " + greeting_buf)
