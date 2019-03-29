import pickle
import os

# set configuration
# folder	folder to store log files
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
