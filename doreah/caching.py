import math
import datetime
from threading import Thread

from ._internal import defaultarguments, doreahconfig

_config = {}

_caches = {}

def config(maxsize=math.inf,maxage=60*60*24*1,maxage_negative=60*60*24*1,lazy_refresh=True):

	global _config
	_config["maxsize"] = maxsize
	_config["maxage"] = maxage
	_config["maxage_negative"] = maxage_negative
	_config["lazy_refresh"] = lazy_refresh


config()


class Cache:

	@defaultarguments(_config,maxsize="maxsize",maxage="maxage",maxage_negative="maxage_negative")
	def __init__(self,maxsize,maxage,maxage_negative):
		self.maxsize = maxsize
		self.maxage = maxage
		self.maxage_negative = maxage_negative

		self.cache = {}
		self.times = {}

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

		if key not in self.cache: raise KeyError()

		value = self.cache[key]

		if allow_expired: return value

		now_stamp = int(datetime.datetime.utcnow().timestamp())
		cache_stamp = self.times.get(key)



		if value is None and (now_stamp - cache_stamp) < self.maxage_negative: return value
		if value is not None and (now_stamp - cache_stamp) < self.maxage: return value

		raise KeyError()

	def add(self,key,value):

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


		if len(self.cache) > self.maxsize:
			#flush anyway expired entries
			self.flush()
		if len(self.cache) > self.maxsize:
			#expire oldest entry
			keys = list(self.times.keys())
			keys.sort(key=lambda k:self.times[k])
			delkey = keys[0]
			del self.cache[delkey]
			del self.times[delkey]

	def flush(self):

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


# decorator
@defaultarguments(_config,maxsize="maxsize",maxage="maxage",maxage_negative="maxage_negative",lazy_refresh="lazy_refresh")
def cached(maxsize,maxage,maxage_negative,lazy_refresh):

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
