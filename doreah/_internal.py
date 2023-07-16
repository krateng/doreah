import os
from functools import wraps
import yaml


# This is purely for documentation
class Default:
	def __repr__(self):
		return u"<Module default>"
DEFAULT = Default()

## decorator to set default arguments that are only evaluated at runtime
def defaultarguments(defaultdict,**defaultargs):
	def decorator(func):	#actual decorator function
		@wraps(func)
		def newfunc(*args,**kwargs):
			realargs = {}

			# evaluate default values at runtime
			for k in defaultargs:
				realargs[k] = defaultdict[defaultargs[k]]

			# overwrite given arguments of function
			realargs.update(kwargs)

			# execute function with correct arguments
			return func(*args,**realargs)

		return newfunc

	return decorator


## opens file, creates it if necessary (including all folders)
def gopen(filepath,mode):
	directory = os.path.dirname(filepath)
	os.makedirs(directory, exist_ok=True)

	return open(filepath,mode,encoding="utf-8")





class DoreahConfig:

	def __init__(self,module,**defaults):
		self.module = module
		self.configuration = {}
		self.configuration.update(defaults)
		self._readfile()
		self._readpreconfig()


	def _readfile(self):
		try:
			with open(".doreah","r") as fil:
				s = yaml.safe_load(fil).get(self.module)
			if s is not None: self.configuration.update(s)
		except OSError:
			pass
		except Exception:
			print("Doreah could not read its configuration file. Your application is likely not up to date and uses the old doreah format!")

	def _readpreconfig(self):
		s = _preconfig.get(self.module)
		if s is not None: self.configuration.update(s)


	# set configuration (exposes function to configure module)
	def __call__(self,**kwargs):
		self.configuration.update(kwargs)


	def __getitem__(self,key):
		return self.configuration[key]

	def __repr__(self):
		return "Configuration for " + self.module + ": " + repr(self.configuration)

_preconfig = {}

def config(**modules):
	global _preconfig
	_preconfig.update(modules)
