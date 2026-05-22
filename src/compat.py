import collections
import collections.abc

# Parche de compatibilidad para experta en Python 3.10+
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping
if not hasattr(collections, 'Callable'):
    collections.Callable = collections.abc.Callable
