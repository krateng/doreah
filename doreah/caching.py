import math
import datetime
from threading import Thread
import os
import sys
import pickle

from ._internal import DEFAULT, defaultarguments, doreahconfig
from .persistence import save, load, delete, size
from .regular import repeathourly

_config = {}

_caches = {}

def config(maxsize=math.inf,maxmemory=math.inf,maxstorage=16*1024*1024*1024,maxage=60*60*24*1,maxage_negative=60*60*24*1,lazy_refresh=True,folder="cache"):
	"""Configures default values for this module.

	These defaults define behaviour of function calls when respective arguments are omitted. Any call of this function will overload the configuration in the .doreah file of the project. This function must be called with all configurations, as any omitted argument will reset to default, even if it has been changed with a previous function call."""
	global _config
	_config["maxsize"] = maxsize
	_config["maxmemory"] = maxmemory
	_config["maxstorage"] = maxstorage
	_config["maxage"] = maxage
	_config["maxage_negative"] = maxage_negative
	_config["folder"] = folder
	if _config["maxsize"] is None: _config["maxsize"] = math.inf
	if _config["maxage"] is None: _config["maxage"] = math.inf
	if _config["maxage_negative"] is None: _config["maxage_negative"] = math.inf
	_config["lazy_refresh"] = lazy_refresh


config()


class Cache:
	"""Dictionary-like object to store key-value pairs up to a certain amount and discard them after they expire.

	:param integer maxsize: Amount of entries the cache should hold before discarding old entries
	:param integer maxmemory: Soft memory limit for the cache (in bytes), not meant for precision
	:param integer maxage: Time in seconds entries are valid for after their last update. Entries older than this value are lazily removed, which means they might still be accessible with the ``allow_expired`` argument of the :meth:`get` method.
	:param integer maxage_negative: Time in seconds entries with the ``None`` value are valid. This is useful for negative caching.
	:param boolean persistent: Whether this cache should be persistent through program restarts
	:param string name: If persistent, this is the filename used"""

	@defaultarguments(_config,maxsize="maxsize",maxmemory="maxmemory",maxage="maxage",maxage_negative="maxage_negative")
	def __init__(self,maxsize=DEFAULT,maxmemory=DEFAULT,maxage=DEFAULT,maxage_negative=DEFAULT,persistent=False,name=None):

		self.maxsize = maxsize
		self.maxmemory = maxmemory
		self.maxage = maxage
		self.maxage_negative = maxage_negative
		self.persistent = persistent
		if self.persistent:
			self.name = name
			try:
				obj = load(name,folder=_config["folder"])
				if obj is not None:
					self.cache,self.times = obj
					self.changed = False
					self._maintenance()
					return
			except:
				pass
		# if either no object loaded, or not persistent in the first place
		self.cache = {}
		self.times = {}
		self.changed = False
		self._maintenance()

	def __del__(self):
		self._maintenance()

#	def create(name="defaultcache",**kwargs):
#		"""Create a new Cache object, preinitializing it from disk if applicable
#
#		:param string name: Name of the object, consistent between sessions
#		:param kwargs: Standard arguments of :class:`Cache` object creation
#		:return: Newly created object"""
#
#		obj = load(name,folder=_config["folder"])
#		if obj is not None: return obj
#
#		obj = Cache(**kwargs,persistent=True,name=name)
#		return obj

	def __contains__(self,key):
		#if key not in self.cache: return False

		#now_stamp = int(datetime.datetime.utcnow().timestamp())
		#cache_stamp = self.times.get(key)

		#if self.cache[key] is None and (now_stamp - cache_stamp) < self.maxage_negative: return True
		#if self.cache[key] is not None and (now_stamp - cache_stamp) < self.maxage: return True

		#return False
		try:
			self.get(key)
			return True
		except KeyError:
			return False


	def get(self,key,allow_expired=False):
		"""Get the value of a key in the cache.

		:param key: Key to be retrieved
		:param boolean allow_expired: If set to True, entries that have already expired will still be returned.
		:return: Value of the requested key in the cache
		:raises KeyError: No valid entry for the key found."""

		if key not in self.cache: raise KeyError()

		value = self.cache[key]

		if allow_expired: return value

		now_stamp = int(datetime.datetime.utcnow().timestamp())
		cache_stamp = self.times.get(key)



		if value is None and (now_stamp - cache_stamp) < self.maxage_negative: return value
		if value is not None and (now_stamp - cache_stamp) < self.maxage: return value

		raise KeyError()

	def add(self,key,value):
		"""Add an entry to the cache.

		:param key: Key to be added
		:param value: Value of this entry"""

#		if len(self.cache) < self.maxsize: #still have space
#			pass
#		else:
#			self.flush() #try to make space
#			if len(self.cache) < self.maxsize: pass # success
#			else:
#				self.
#				raise MemoryError() # still no space


		self.cache[key] = value
		self.times[key] = int(datetime.datetime.utcnow().timestamp())

		self._onupdate()

	def flush(self):
		"""Flush all expired entries from the cache. This is normally done lazily when needed, so this function does not need to be called manually."""

		now_stamp = int(datetime.datetime.utcnow().timestamp())

		for key in list(self.cache.keys()):
			value = self.cache[key]
			cache_stamp = self.times.get(key)

			if value is None and (now_stamp - cache_stamp) > self.maxage_negative:
				del self.cache[key]
				del self.times[key]
			if value is not None and (now_stamp - cache_stamp) > self.maxage:
				del self.cache[key]
				del self.times[key]


	def _onupdate(self):
		self.changed = True

	@repeathourly
	def _maintenance(self):
		if self.changed:
			if len(self.cache) > self.maxsize or self._size() > self.maxmemory:
				#flush anyway expired entries
				self.flush()

			while len(self.cache) > self.maxsize or self._size() > self.maxmemory:
				#expire oldest entry
				keys = list(self.times.keys())
				keys.sort(key=lambda k:self.times[k])
				delkey = keys[0]
				del self.cache[delkey]
				del self.times[delkey]

			if self.persistent:
				save((self.cache,self.times),self.name,folder=_config["folder"])

			self.changed = False



	def _size(self):
		return sys.getsizeof(pickle.dumps(self.cache))



class _DiskReference:
	def __init__(self,filename):
		self.filename = filename

class DeepCache(Cache):
	"""Dictionary-like object to store key-value pairs with the help of hard disk storage up to a certain amount and discard them after they expire.

	:param integer maxmemory: Soft memory limit for the cache (in bytes), not meant for precision
	:param integer maxstorage: Soft disk space limit for the cache (in bytes), not meant for precision
	:param integer maxage: Time in seconds entries are valid for after their last update. Entries older than this value are lazily removed, which means they might still be accessible with the ``allow_expired`` argument of the :meth:`get` method.
	:param integer maxage_negative: Time in seconds entries with the ``None`` value are valid. This is useful for negative caching.
	:param string name: Directory name used for storage"""

	@defaultarguments(_config,maxmemory="maxmemory",maxstorage="maxstorage",maxage="maxage",maxage_negative="maxage_negative")
	def __init__(self,maxmemory=DEFAULT,maxage=DEFAULT,maxstorage=DEFAULT,maxage_negative=DEFAULT,name="deepcache"):

		self.maxmemory = maxmemory
		self.maxstorage = maxstorage
		self.maxage = maxage
		self.maxage_negative = maxage_negative

		self.name = name

		try:
			obj = load(self._file(),folder=_config["folder"])
			self.cache,self.times,self.counter = obj
			self.changed = False
		except:
			self.cache = {}
			self.times = {}
			self.counter = 0

		self.changed = False

		self._maintenance()

	def get(self,key,allow_expired=False):
		"""Get the value of a key in the cache.

		:param key: Key to be retrieved
		:param boolean allow_expired: If set to True, entries that have already expired will still be returned.
		:return: Value of the requested key in the cache
		:raises KeyError: No valid entry for the key found."""

		if key not in self.cache: raise KeyError()

		value = self.cache[key]
		if isinstance(value,_DiskReference):
			value = load(self._file(value.filename),folder=_config["folder"])
		if allow_expired: return value

		now_stamp = int(datetime.datetime.utcnow().timestamp())
		cache_stamp = self.times.get(key)



		if value is None and (now_stamp - cache_stamp) < self.maxage_negative: return value
		if value is not None and (now_stamp - cache_stamp) < self.maxage: return value

		raise KeyError()

	def add(self,key,value):
		"""Add an entry to the cache.

		:param key: Key to be added
		:param value: Value of this entry"""

		# remove old file
		if key in self.cache and isinstance(self.cache[key],_DiskReference):
			delete(self._file(self.cache[key].filename),folder=_config["folder"])

		self.cache[key] = value
		self.times[key] = int(datetime.datetime.utcnow().timestamp())

		self._onupdate()

	def flush(self):
		"""Flush all expired entries from the cache. This is normally done lazily when needed, so this function does not need to be called manually."""

		now_stamp = int(datetime.datetime.utcnow().timestamp())

		for key in list(self.cache.keys()):
			value = self.cache[key]
			cache_stamp = self.times.get(key)

			if value is None and (now_stamp - cache_stamp) > self.maxage_negative:
				if isinstance(self.cache[key],_DiskReference): delete(self._file(self.cache[key].filename),folder=_config["folder"])
				del self.cache[key]
				del self.times[key]
			if value is not None and (now_stamp - cache_stamp) > self.maxage:
				if isinstance(self.cache[key],_DiskReference): delete(self._file(self.cache[key].filename),folder=_config["folder"])
				del self.cache[key]
				del self.times[key]


	def _onupdate(self):
		self.changed = True

	@repeathourly
	def _maintenance(self):
		if self.changed:
			if self._size() > self.maxmemory:
				#flush anyway expired entries
				self.flush()

			while self._size() > self.maxmemory:
				#serialize biggest entry
				keys = list(self.times.keys())
				keys.sort(key=lambda k:sys.getsizeof(pickle.dumps(self.cache[k])),reverse=True)
				keys = [k for k in keys if not isinstance(self.cache[k],_DiskReference)]
				if sys.getsizeof(pickle.dumps(self.cache[keys[0]])) < (512 * 1024):
					break
					# don't serialize tiny stuff
				try:
					movekey = keys[0]
					self._memorytodisk(movekey)
				except:
					break

			while self._disksize() > self.maxstorage:
				print("Disk size " + str(self._disksize()))
				keys = list(self.times.keys())
				keys.sort(key=lambda k:self.times[k])
				keys = [k for k in keys if isinstance(self.cache[k],_DiskReference)]
				try:
					delkey = keys[0]
					print("Deleting " + delkey)
					delete(self._file(self.cache[delkey].filename),folder=_config["folder"])
					del self.cache[delkey]
					del self.times[delkey]
				except:
					break


			save((self.cache,self.times,self.counter),self._file(),folder=_config["folder"])

			self.changed = False

	def _memorytodisk(self,key):
		print("Moving " + key + " from memory to disk")
		self.counter += 1
		value = self.cache[key]
		filename = str(self.counter)
		save(value,self._file(filename),folder=_config["folder"])
		self.cache[key] = _DiskReference(filename)

	def _disktomemory(self,key):
		print("Moving " + key + " from disk to memory")
		filename = self.cache[key].filename
		value = load("./" + self.name + "/" + filename,folder=_config["folder"])
		self.cache[key] = value
		delete(self._file(filename),folder=_config["folder"])


	def _size(self):
		return sys.getsizeof(pickle.dumps([self.cache[key] for key in self.cache if not isinstance(self.cache[key],_DiskReference)]))

	def _disksize(self):
		#return sum(os.path.getsize("./" + _config["folder"] + "/" + self.name + "/" + f) for f in os.listdir("./" + _config["folder"] + "/" + self.name))
		sumsize = 0
		for key in self.cache:
			if isinstance(self.cache[key],_DiskReference):
				sumsize += size(self._file(self.cache[key].filename),folder=_config["folder"])
		return sumsize

	# gets a relative filename for keys of this deepcache object
	def _file(self,name=None):
		if name is None: name = "root"
		return os.path.join(self.name,name)


# decorator
@defaultarguments(_config,maxsize="maxsize",maxage="maxage",maxage_negative="maxage_negative",lazy_refresh="lazy_refresh")
def cached(maxsize=DEFAULT,maxage=DEFAULT,maxage_negative=DEFAULT,lazy_refresh=DEFAULT):
	"""Method decorator to add a proxy cache to a function without keyword arguments.

	:param integer maxsize: Amount of entries the cache should hold before discarding old entries.
	:param integer maxage: Time in seconds entries are valid for after their last update. Entries older than this value are lazily removed, which means they might still be accessible with the ``allow_expired`` argument of the :meth:`get` method.
	:param integer maxage_negative: Time in seconds entries with the ``None`` value are valid. This is useful for negative caching.
	:param boolean lazy_refresh: If True, expired cache entries will still be returned, but trigger a background refresh. Useful if speed is more important than currentness of data."""


	# decorator for lazy refresh
	if lazy_refresh:
		def cacheddecorator(func):

			def newfunc(*args,cache=Cache(maxsize=maxsize,maxage=maxage,maxage_negative=maxage_negative)):
				try:
					result = cache.get(args,allow_expired=True)
				except:
					result = func(*args)
					cache.add(args,result)
					return result

				if args not in cache: # if we just got an expired result, we want to execute the function and add to cache

					def fillcache(cache,args,func):
						cache.add(args,func(*args))

					t = Thread(target=fillcache,args=(cache,args,func,))
					t.start()

				return result

			return newfunc

	# decorator for non-lazy
	else:
		def cacheddecorator(func):

			def newfunc(*args,cache=Cache(maxsize=maxsize,maxage=maxage,maxage_negative=maxage_negative)):
				try:
					return cache.get(args)
				except:
					result = func(*args)
					cache.add(args,result)
					return result

			return newfunc

	return cacheddecorator



# now check local configuration file
_config.update(doreahconfig("caching"))
