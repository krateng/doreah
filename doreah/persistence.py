import pickle
import os

from ._internal import defaultarguments, gopen, doreahconfig

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
def save(data,name,folder):
	"""Saves the supplied data structure to disk"""

	filename = os.path.join(folder,name + ".gilly")

	fl = gopen(filename,"wb")
	stream = pickle.dumps(data)
	fl.write(stream)
	fl.close()

@defaultarguments(_config,folder="folder")
def load(name,folder):
	"""Loads a data structure from disk"""

	filename = os.path.join(folder,name + ".gilly")

	try:
		fl = gopen(filename,"rb")
		ob = pickle.loads(fl.read())
	except: ob = None
	finally:
		fl.close()

	return ob



# now check local configuration file
_config.update(doreahconfig("persistence"))
