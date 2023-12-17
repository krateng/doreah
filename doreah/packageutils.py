import os
from distutils import dir_util

from ._internal import defaultarguments, DoreahConfig

config = DoreahConfig("packageutils",
	packagename=None,
	populate=None
)


#if config["packagename"] is None: config(packagename=)

try:
	HOME_DIR = os.environ["XDG_DATA_HOME"].split(":")[0]
	assert os.path.exists(HOME_DIR)
except Exception:
	HOME_DIR = os.path.join(os.environ["HOME"],".local/share/")

DATA_DIR = None # the actual folder for this package

def _set_datafolder():
	global DATA_DIR
	if DATA_DIR is None:
		DATA_DIR = os.path.join(HOME_DIR,config["packagename"])
		os.makedirs(DATA_DIR,exist_ok=True)

def pkgdata(*args):
	_set_datafolder()
	return os.path.join(DATA_DIR,*args)

def init_datafolder():
	_set_datafolder()
	dir_util.copy_tree(config["populate"],DATA_DIR,update=False)
