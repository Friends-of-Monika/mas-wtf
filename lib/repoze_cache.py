# License
#
#   A copyright notice accompanies this license document that identifies
#   the copyright holders.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
#
#   1.  Redistributions in source code must retain the accompanying
#       copyright notice, this list of conditions, and the following
#       disclaimer.
#
#   2.  Redistributions in binary form must reproduce the accompanying
#       copyright notice, this list of conditions, and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#   3.  Names of the copyright holders must not be used to endorse or
#       promote products derived from this software without prior
#       written permission from the copyright holders.
#
#   4.  If any files are modified, you must cause the modified files to
#       carry prominent notices stating that you changed the files and
#       the date of any change.
#
#   Disclaimer
#
#     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND
#     ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#     TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#     PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#     HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#     EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#     TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#     DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#     ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
#     TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
#     THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#     SUCH DAMAGE.


""" LRU caching class and decorator """
from abc import abstractmethod
from abc import ABCMeta

import threading
import time
import uuid


_MARKER = object()
# By default, expire items after 2**60 seconds. This fits into 64 bit
# integers and is close enough to "never" for practical purposes.
_DEFAULT_TIMEOUT = 2 ** 60


class Cache(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def clear(self):
        """Remove all entries from the cache"""

    @abstractmethod
    def get(self, key, default=None):
        """Return value for key. If not in cache, return default"""

    @abstractmethod
    def put(self, key, val):
        """Add key to the cache with value val"""

    @abstractmethod
    def invalidate(self, key):
        """Remove key from the cache"""


class UnboundedCache(Cache):
    """
    a simple unbounded cache backed by a dictionary
    """

    def __init__(self):
        self._data = dict()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def clear(self):
        self._data.clear()

    def invalidate(self, key):
        try:
            del self._data[key]
        except KeyError:
            pass

    def put(self, key, val):
        self._data[key] = val


class LRUCache(Cache):
    """ Implements a pseudo-LRU algorithm (CLOCK)

    The Clock algorithm is not kept strictly to improve performance, e.g. to
    allow get() and invalidate() to work without acquiring the lock.
    """
    def __init__(self, size):
        size = int(size)
        if size < 1:
            raise ValueError('size must be >0')
        self.size = size
        self.lock = threading.Lock()
        self.hand = 0
        self.maxpos = size - 1
        self.clock_keys = None
        self.clock_refs = None
        self.data = None
        self.evictions = 0
        self.hits = 0
        self.misses = 0
        self.lookups = 0
        self.clear()

    def clear(self):
        """Remove all entries from the cache"""
        with self.lock:
            # If really clear()ing a full cache, clean up self.data first to
            # give garbage collection a chance to reduce memorey usage.
            # Instantiating "[_MARKER] * size" will temporarily have 2 lists
            # in memory -> high peak memory usage for tiny amount of time.
            # With self.data already clear, that peak should not exceed what
            # we normally use.
            self.data = {}
            size = self.size
            self.clock_keys = [_MARKER] * size
            self.clock_refs = [False] * size
            self.hand = 0
            self.evictions = 0
            self.hits = 0
            self.misses = 0
            self.lookups = 0

    def get(self, key, default=None):
        """Return value for key. If not in cache, return default"""
        self.lookups += 1
        try:
            pos, val = self.data[key]
            self.hits += 1
        except KeyError:
            self.misses += 1
            return default
        self.clock_refs[pos] = True
        return val

    def put(self, key, val):
        """Add key to the cache with value val"""
        # These do not change or they are just references, no need for locking.
        maxpos = self.maxpos
        clock_refs = self.clock_refs
        clock_keys = self.clock_keys
        data = self.data

        with self.lock:
            entry = data.get(key)
            if entry is not None:
                # We already have key. Only make sure data is up to date and
                # to remember that it was used.
                pos, old_val = entry
                if old_val is not val:
                    data[key] = (pos, val)
                self.clock_refs[pos] = True
                return
            # else: key is not yet in cache. Search place to insert it.

            hand = self.hand
            count = 0
            max_count = 107
            while 1:
                ref = clock_refs[hand]
                if ref == True:
                    clock_refs[hand] = False
                    hand += 1
                    if hand > maxpos:
                        hand = 0

                    count += 1
                    if count >= max_count:
                        # We have been searching long enough. Force eviction of
                        # next entry, no matter what its status is.
                        clock_refs[hand] = False
                else:
                    oldkey = clock_keys[hand]
                    # Maybe oldkey was not in self.data to begin with. If it
                    # was, self.invalidate() in another thread might have
                    # already removed it. del() would raise KeyError, so pop().
                    oldentry = data.pop(oldkey, _MARKER)
                    if oldentry is not _MARKER:
                        self.evictions += 1
                    clock_keys[hand] = key
                    clock_refs[hand] = True
                    data[key] = (hand, val)
                    hand += 1
                    if hand > maxpos:
                        hand = 0
                    self.hand = hand
                    break

    def invalidate(self, key):
        """Remove key from the cache"""
        # pop with default arg will not raise KeyError
        entry = self.data.pop(key, _MARKER)
        if entry is not _MARKER:
            # We have no lock, but worst thing that can happen is that we
            # set another key's entry to False.
            self.clock_refs[entry[0]] = False
        # else: key was not in cache. Nothing to do.


class ExpiringLRUCache(Cache):
    """ Implements a pseudo-LRU algorithm (CLOCK) with expiration times

    The Clock algorithm is not kept strictly to improve performance, e.g. to
    allow get() and invalidate() to work without acquiring the lock.
    """
    def __init__(self, size, default_timeout=_DEFAULT_TIMEOUT):
        self.default_timeout = default_timeout
        size = int(size)
        if size < 1:
            raise ValueError('size must be >0')
        self.size = size
        self.lock = threading.Lock()
        self.hand = 0
        self.maxpos = size - 1
        self.clock_keys = None
        self.clock_refs = None
        self.data = None
        self.evictions = 0
        self.hits = 0
        self.misses = 0
        self.lookups = 0
        self.clear()

    def clear(self):
        """Remove all entries from the cache"""
        with self.lock:
            # If really clear()ing a full cache, clean up self.data first to
            # give garbage collection a chance to reduce memorey usage.
            # Instantiating "[_MARKER] * size" will temporarily have 2 lists
            # in memory -> high peak memory usage for tiny amount of time.
            # With self.data already clear, that peak should not exceed what
            # we normally use.
            # self.data contains (pos, val, expires) triplets
            self.data = {}
            size = self.size
            self.clock_keys = [_MARKER] * size
            self.clock_refs = [False] * size
            self.hand = 0
            self.evictions = 0
            self.hits = 0
            self.misses = 0
            self.lookups = 0

    def get(self, key, default=None):
        """Return value for key. If not in cache or expired, return default"""
        self.lookups += 1
        try:
            pos, val, expires = self.data[key]
        except KeyError:
            self.misses += 1
            return default
        if expires > time.time():
            # cache entry still valid
            self.hits += 1
            self.clock_refs[pos] = True
            return val
        else:
            # cache entry has expired. Make sure the space in the cache can
            # be recycled soon.
            self.misses += 1
            self.clock_refs[pos] = False
            return default

    def put(self, key, val, timeout=None):
        """Add key to the cache with value val

        key will expire in $timeout seconds. If key is already in cache, val
        and timeout will be updated.
        """
        # These do not change or they are just references, no need for locking.
        maxpos = self.maxpos
        clock_refs = self.clock_refs
        clock_keys = self.clock_keys
        data = self.data
        lock = self.lock
        if timeout is None:
            timeout = self.default_timeout

        with self.lock:
            entry = data.get(key)
            if entry is not None:
                # We already have key. Only make sure data is up to date and
                # to remember that it was used.
                pos = entry[0]
                data[key] = (pos, val, time.time() + timeout)
                clock_refs[pos] = True
                return
            # else: key is not yet in cache. Search place to insert it.

            hand = self.hand
            count = 0
            max_count = 107
            while 1:
                ref = clock_refs[hand]
                if ref == True:
                    clock_refs[hand] = False
                    hand += 1
                    if hand > maxpos:
                        hand = 0

                    count += 1
                    if count >= max_count:
                        # We have been searching long enough. Force eviction of
                        # next entry, no matter what its status is.
                        clock_refs[hand] = False
                else:
                    oldkey = clock_keys[hand]
                    # Maybe oldkey was not in self.data to begin with. If it
                    # was, self.invalidate() in another thread might have
                    # already removed it. del() would raise KeyError, so pop().
                    oldentry = data.pop(oldkey, _MARKER)
                    if oldentry is not _MARKER:
                        self.evictions += 1
                    clock_keys[hand] = key
                    clock_refs[hand] = True
                    data[key] = (hand, val, time.time() + timeout)
                    hand += 1
                    if hand > maxpos:
                        hand = 0
                    self.hand = hand
                    break

    def invalidate(self, key):
        """Remove key from the cache"""
        # pop with default arg will not raise KeyError
        entry = self.data.pop(key, _MARKER)
        if entry is not _MARKER:
            # We have no lock, but worst thing that can happen is that we
            # set another key's entry to False.
            self.clock_refs[entry[0]] = False
        # else: key was not in cache. Nothing to do.


class lru_cache(object):
    """ Decorator for LRU-cached function

    timeout parameter specifies after how many seconds a cached entry should
    be considered invalid.
    """
    def __init__(self,
                 maxsize,
                 cache=None, # cache is an arg to serve tests
                 timeout=None,
                 ignore_unhashable_args=False):
        if cache is None:
            if maxsize is None:
                cache = UnboundedCache()
            elif timeout is None:
                cache = LRUCache(maxsize)
            else:
                cache = ExpiringLRUCache(maxsize, default_timeout=timeout)
        self.cache = cache
        self._ignore_unhashable_args = ignore_unhashable_args

    def __call__(self, func):
        cache = self.cache
        marker = _MARKER

        def cached_wrapper(*args, **kwargs):
            try:
                key = (args, frozenset(kwargs.items())) if kwargs else args
            except TypeError as e:
                if self._ignore_unhashable_args:
                    return func(*args, **kwargs)
                else:
                    raise e
            else:
                val = cache.get(key, marker)
                if val is marker:
                    val = func(*args, **kwargs)
                    cache.put(key, val)
                return val

        def _maybe_copy(source, target, attr):
            value = getattr(source, attr, source)
            if value is not source:
                setattr(target, attr, value)

        _maybe_copy(func, cached_wrapper, '__module__')
        _maybe_copy(func, cached_wrapper, '__name__')
        _maybe_copy(func, cached_wrapper, '__doc__')
        cached_wrapper._cache = cache
        return cached_wrapper


class CacheMaker(object):
    """Generates decorators that can be cleared later
    """
    def __init__(self, maxsize=None, timeout=_DEFAULT_TIMEOUT):
        """Create cache decorator factory.

        - maxsize : the default size for created caches.

        - timeout : the defaut expiraiton time for created caches.
        """
        self._maxsize = maxsize
        self._timeout = timeout
        self._cache = {}

    def _resolve_setting(self, name=None, maxsize=None, timeout=None):
        if name is None:
            while True:
                name = str(uuid.uuid4())
                ## the probability of collision is so low ....
                if name not in self._cache:  # pragma: NO COVER
                    break

        if name in self._cache:
            raise KeyError("cache %s already in use" % name)

        if maxsize is None:
            maxsize = self._maxsize

        if maxsize is None:
            raise ValueError("Cache must have a maxsize set")

        if timeout is None:
            timeout = self._timeout

        return name, maxsize, timeout

    def memoized(self, name=None):
        name, maxsize, _ = self._resolve_setting(name, 0)
        cache = self._cache[name] = UnboundedCache()
        return lru_cache(None, cache)

    def lrucache(self, name=None, maxsize=None):
        """Named arguments:

        - name (optional) is a string, and should be unique amongst all caches

        - maxsize (optional) is an int, overriding any default value set by
          the constructor
        """
        name, maxsize, _ = self._resolve_setting(name, maxsize)
        cache = self._cache[name] = LRUCache(maxsize)
        return lru_cache(maxsize, cache)

    def expiring_lrucache(self, name=None, maxsize=None, timeout=None):
        """Named arguments:

        - name (optional) is a string, and should be unique amongst all caches

        - maxsize (optional) is an int, overriding any default value set by
          the constructor

        - timeout (optional) is an int, overriding any default value set by
          the constructor or the default value (%d seconds)
        """ % _DEFAULT_TIMEOUT
        name, maxsize, timeout = self._resolve_setting(name, maxsize, timeout)
        cache = self._cache[name] = ExpiringLRUCache(maxsize, timeout)
        return lru_cache(maxsize, cache, timeout)

    def clear(self, *names):
        """Clear the given cache(s).

        If no 'names' are passed, clear all caches.
        """
        if len(names) == 0:
            names = self._cache.keys()

        for name in names:
            self._cache[name].clear()
