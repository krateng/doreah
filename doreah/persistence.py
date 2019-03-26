import pickle
import os

# set configuration
# defaultextension	files with this extension will be regarded as valid files. can be overwritten per request.
# comments			whether files may include commenting (indicated by #)
# multitab			whether fields can be separated by multiple tabs (this makes empty fields impossible except when trailing)
def config(folder="storage"):
	global _folder
	_folder = folder

# initial config on import, set everything to default
config()


def save(data,name,folder=_folder):

	filename = os.path.join(folder,name + ".gilly")

	fl = open(filename,"wb")
	stream = pickle.dumps(data)
	fl.write(stream)
	fl.close()

def load(name,folder=_folder):

	filename = os.path.join(folder,name + ".gilly")

	try:
		fl = open(filename,"rb")
		ob = pickle.loads(fl.read())
	except: ob = None
	finally:
		fl.close()

	return ob
