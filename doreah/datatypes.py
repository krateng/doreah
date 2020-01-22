from ._internal import DEFAULT, defaultarguments, DoreahConfig


config = DoreahConfig("datatypes",
)

class DictStack:

	def __init__(self,*args,**kwargs):
		self.stack = [dict(*args,**kwargs)]
		#same options as normal dict, either kwargs for entries or one arg for dict

	def __flat__(self):
		di = {}
		for d in self.stack:
			di.update(d)
		return di

	def __setitem__(self,key,value):
		for d in reversed(self.stack):
			if key in d:
				d[key] = value
				break
		else:
			self.stack[0][key] = value

	def __getitem__(self,key):
		for d in reversed(self.stack):
			if key in d:
				return d[key]
		raise KeyError

	def __contains__(self,key):
		return self.__flat__().__contains__(key)

	def __delitem__(self,key):
		for d in reversed(self.stack):
			if key in d:
				del d[key]
		raise KeyError

	def clear(self):
		self.stack = [{}]

	def copy(self):
		return [dict(d) for d in self.stack]

	def get(self,key):
		try:
			return self.__getitem__(key)
		except:
			return None

	def has_key(self,key):
		return self.__contains__(key)

	def update(self,*args,**kwargs):
		self.stack[-1].update(*args,**kwargs)

	def __repr__(self):
		return self.__flat__().__repr__()

	def __len__(self):
		return self.__flat__().__len__()

	def keys(self):
		return self.__flat__().keys()
	def values(self):
		return self.__flat__().values()
	def items(self):
		return self.__flat__().items()

	def push(self,*args,**kwargs):
		self.stack.append(dict(*args,**kwargs))
	def pop(self):
		return self.stack.pop()

	@property
	def locl(self):
		return self.stack[-1]
	@property
	def globl(self):
		return self.stack[0]
