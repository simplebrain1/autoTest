from functools import wraps


def Const(cls):
    @wraps(cls)
    def new_setattr(self, name, value):
        raise Exception('const : {} can not be changed'.format(name))

    cls.__setattr__ = new_setattr
    return cls


@Const
class _StageSepx(object):
    compress_rate = 0.4
    threshold = 0.97
    block = 6
    offset = None


@Const
class _Platform(object):
    mac = 'mac'
    windows = 'windows'
    linux = 'linux'


@Const
class _Const(object):
    stagesepx = _StageSepx()
    platform = _Platform()


CONST = _Const()
