# Licensed under a 3-clause BSD style license - see LICENSE.rst

# THIRD-PARTY
from astropy.io import registry as io_registry

__all__ = ["PawprintRead", "PawprintWrite", "PawprintFromFormat", "PawprintToFormat"]
__doctest_skip__ = __all__


# ==============================================================================
# Read / Write

readwrite_registry = io_registry.UnifiedIORegistry()


class PawprintRead(io_registry.UnifiedReadWrite):
    def __init__(self, instance, pawprint_cls):
        super().__init__(instance, pawprint_cls, "read", registry=readwrite_registry)

    def __call__(self, *args, **kwargs):
        return self.registry.read(self._cls, *args, **kwargs)


class PawprintWrite(io_registry.UnifiedReadWrite):
    def __init__(self, instance, cls):
        super().__init__(instance, cls, "write", registry=readwrite_registry)

    def __call__(self, *args, **kwargs):
        self.registry.write(self._instance, *args, **kwargs)


# ==============================================================================
# Format Interchange

convert_registry = io_registry.UnifiedIORegistry()


class PawprintFromFormat(io_registry.UnifiedReadWrite):
    def __init__(self, instance, pawprint_cls):
        super().__init__(instance, pawprint_cls, "read", registry=convert_registry)

    def __call__(self, obj, *args, format=None, **kwargs):
        return self.registry.read(self._cls, obj, *args, format=format, **kwargs)


class PawprintToFormat(io_registry.UnifiedReadWrite):
    def __init__(self, instance, cls):
        super().__init__(instance, cls, "write", registry=convert_registry)

    def __call__(self, format, *args, **kwargs):
        return self.registry.write(self._instance, None, *args, format=format, **kwargs)
