from functools import lru_cache

import numpy as np


class XMixin:
    def __init__(self, x, clip_x):
        self._x = x
        self.clip_x = clip_x

    @property
    @lru_cache(maxsize=1)
    def x(self):
        return np.minimum(np.maximum(self._x, 0), self.clip_x)

    @x.setter
    def x(self, value):
        self._x = value
        XMixin.x.fget.cache_clear()


class YMixin:
    def __init__(self, y, clip_y):
        self._y = y
        self.clip_y = clip_y

    @property
    @lru_cache(maxsize=1)
    def y(self):
        return np.minimum(np.maximum(self._y, 0), self.clip_y)

    @y.setter
    def y(self, value):
        self._y = value
        YMixin.y.fget.cache_clear()


class ZMixin:
    def __init__(self, z, clip_z):
        self._z = z
        self.clip_z = clip_z

    @property
    @lru_cache(maxsize=1)
    def z(self):
        return np.minimum(np.maximum(self._z, 0), self.clip_z)

    @z.setter
    def z(self, value):
        self._z = value
        ZMixin.z.fget.cache_clear()


class TMixin:
    def __init__(self, t, clip_t):
        self._t = t
        self.clip_t = clip_t

    @property
    @lru_cache(maxsize=1)
    def t(self):
        return np.minimum(np.maximum(self._t, 0), self.clip_t)

    @t.setter
    def t(self, value):
        self._t = value
        TMixin.t.fget.cache_clear()


class XYCoord(XMixin, YMixin):
    def __init__(self, shape, x=0, y=0):
        XMixin.__init__(self, x, shape[0] - 1)
        YMixin.__init__(self, y, shape[1] - 1)


class XYTCoord(XMixin, YMixin, TMixin):
    def __init__(self, shape, x=0, y=0, t=0):
        XMixin.__init__(self, x, shape[0] - 1)
        YMixin.__init__(self, y, shape[1] - 1)
        TMixin.__init__(self, t, shape[2] - 1)


class XYZCoord(XMixin, YMixin, ZMixin):
    def __init__(self, shape, x=0, y=0, z=0):
        XMixin.__init__(self, x, shape[0] - 1)
        YMixin.__init__(self, y, shape[1] - 1)
        ZMixin.__init__(self, z, shape[2] - 1)


class XYZTCoord(XMixin, YMixin, ZMixin, TMixin):
    def __init__(self, shape, x=0, y=0, z=0, t=0):
        XMixin.__init__(self, x, shape[0] - 1)
        YMixin.__init__(self, y, shape[1] - 1)
        ZMixin.__init__(self, z, shape[2] - 1)
        TMixin.__init__(self, t, shape[3] - 1)
