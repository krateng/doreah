import os
from functools import wraps

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

	return open(filepath,mode)



# reads module configuration from file
def doreahconfig(module):
	from .settings import get_settings
	s = get_settings(files=[".doreah"],prefix=module + ".",cut_prefix=True)
	return s




class DoreahConfig:

	def __init__(self,module):
		self.module = module
		self.configuration = {}

	def _readfile(self):
		from .settings import get_settings
		s = get_settings(files=[".doreah"],prefix=self.module + ".",cut_prefix=True)
		self.configuration.update(s)

	# set configuration
	def __call__(self,**kwargs):
		self.configuration.update(kwargs)

	def _initial(self,ignore_file=False,**kwargs):
		self(**kwargs) # set initial values
		if not ignore_file:
			self._readfile() # overwrite from .doreah file

	def __getitem__(self,key):
		return self.configuration[key]

	def __repr__(self):
		return "Configuration for " + self.module + ": " + repr(self.configuration)
