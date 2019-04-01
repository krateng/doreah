import pickle
import os

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

	filename = os.path.join(folder,name + ".gilly")

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

	filename = os.path.join(folder,name + ".gilly")

	try:
		with gopen(filename,"rb") as fl:
			ob = pickle.loads(fl.read())
	except: ob = None

	return ob



# now check local configuration file
_config.update(doreahconfig("persistence"))
