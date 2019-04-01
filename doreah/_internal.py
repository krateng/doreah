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



### change decorator, use default object instead (sentinel) for better documentation
