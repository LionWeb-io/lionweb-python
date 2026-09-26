# Kept for backward compatibility: the constants live in lionweb.autoresolve so
# that lionweb.model can use them without importing the lionweb.utils package.
from lionweb.autoresolve import (
    LIONCORE_AUTORESOLVE_PREFIX,
    LIONCOREBUILTINS_AUTORESOLVE_PREFIX,
)

__all__ = ["LIONCORE_AUTORESOLVE_PREFIX", "LIONCOREBUILTINS_AUTORESOLVE_PREFIX"]
