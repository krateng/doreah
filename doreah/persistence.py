import pickle
import os
import math
import zlib
import random

from ._internal import DEFAULT, defaultarguments, gopen, doreahconfig

_config = {}

# set configuration
# folder	folder to store log files
def config(folder="storage"):
	"""Configures default values for this module.

	These defaults define behaviour of function calls when respective arguments are omitted. Any call of this function will overload the configuration in the .doreah file of the project. This function must be called with all configurations, as any omitted argument will reset to default, even if it has been changed with a previous function call."""
	global _config
	_config["folder"] = folder


# initial config on import, set everything to default
config()


@defaultarguments(_config,folder="folder")
def save(data,name,folder=DEFAULT):
	"""Saves the supplied data structure to disk.

	:param data: Object to be serialized and saved to disk
	:param string name: File name to be used
	:param string folder: Custom folder to save the file in"""

	filename = os.path.join(folder,name)

	try:
		with gopen(filename,"wb") as fl:
			stream = pickle.dumps(data)
			fl.write(stream)
	except:
		pass

@defaultarguments(_config,folder="folder")
def load(name,folder=DEFAULT):
	"""Loads a data structure from disk.

	:param string name: File name to be read
	:param string folder: Custom folder where the file is stored
	:return: Data object"""

	filename = os.path.join(folder,name)

	try:
		with gopen(filename,"rb") as fl:
			ob = pickle.loads(fl.read())
	except: ob = None

	return ob

@defaultarguments(_config,folder="folder")
def delete(name,folder=DEFAULT):
	"""Deletes a serialized data structure from disk.

	:param string name: File name
	:param string folder: Custom folder where the file is stored"""

	filename = os.path.join(folder,name)
	try:
		os.remove(filename)
	except:
		pass

@defaultarguments(_config,folder="folder")
def size(name,folder=DEFAULT):
	"""Returns the size of a serialized object.

	:param string name: File name
	:param string folder: Custom folder where the file is stored"""

	filename = os.path.join(folder,name)
	return os.path.getsize(filename)


# need a deterministic hash function
def _hash(val):
	if isinstance(val,int):
		return val
	elif isinstance(val,str):
		return zlib.adler32(bytes(val,encoding='UTF-8'))
	elif isinstance(val,dict):
		return _hash(tuple((k,val[k]) for k in sorted(val)))
	elif isinstance(val,tuple) or isinstance(val,list):
		x = 10
		i = 1
		for element in val:
			x = ((x * _hash(element)) ** i)
			i += 1
		return x

	try:
		return zlib.adler32(val)
	except: pass
	try:
		return zlib.adler32(bytes(val))
	except: pass



class DiskDict:
	"""Dictionary-like object that stores its authorative information completely on disk.

	:param integer maxmemory: Soft memory limit (in bytes), not meant for precision
	:param integer maxstorage: Soft disk space limit (in bytes), not meant for precision
	:param string name: Directory name used for storage"""

	def __init__(self,maxmemory=math.inf,maxstorage=1024*1024*1024*4,name="diskdict"):

		self.maxmemory = maxmemory
		self.maxstorage = maxstorage

		self.name = name
		self.folder = os.path.join(_config["folder"],name)


		self.cache = {}
		self.cache_unhashable = {}



	def __getitem__(self,key):
		return self.get(key)
	def __setitem__(self,key,value):
		return self.add(key,value)
	def __delitem__(self,key):
		pass

	def __str__(self):
		return "{" + ",".join([str(key) + ":" + str(self.cache[key]) for key in self.cache] + ["etc."]) + "}"

	def get(self,key):
		"""Get the value of a key.

		:param key: Key to be retrieved
		:return: Value of the requested key
		:raises KeyError: No valid entry for the key found."""

		hashvalue = str(_hash(key))
		try:
			return self.cache[key]
		except: pass
		try:
			return self.cache_unhashable[hashvalue]
		except: pass

		if os.path.exists(os.path.join(self.folder,hashvalue)):
			possibilities = os.listdir(os.path.join(self.folder,hashvalue))
			for p in possibilities:
				result = load(os.path.join(self.name,hashvalue,p))
				if result[0] == key:
					val = result[1]
					try:
						self.cache[key] = val
					except TypeError:
						self.cache_unhashable[hashvalue] = val
					return val

		raise KeyError()



	def add(self,key,value):
		"""Add an entry.

		:param key: Key to be added
		:param value: Value of this entry"""

		hashvalue = str(_hash(key))
		name = str(random.uniform(1000000000,9999999999)).replace(".","")
		save((key,value),os.path.join(self.name,hashvalue,name))


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






# now check local configuration file
_config.update(doreahconfig("persistence"))
