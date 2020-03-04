from ._internal import DEFAULT, defaultarguments, DoreahConfig
import os

config = DoreahConfig("filesystem",
)


def relative_file_list(pth,exclude_dotfiles=True):
	for (dirpath,dirnames,filenames) in os.walk(pth):
		reldir = os.path.relpath(dirpath,start=pth)
		for f in filenames:
			if f.startswith(".") and exclude_dotfiles: continue
			relfilepath = os.path.join(reldir, f)
			if relfilepath.startswith("./"): relfilepath = relfilepath[2:]
			yield relfilepath

def directory_dict(pth,file_values=FileWrapper,exclude_dotfiles=True):
	contents = {}
	for e in os.listdir(pth):
		if e.startswith(".") and exclude_dotfiles: continue
		fullpth = os.path.join(pth,e)
		if os.path.isdir(fullpth):
			contents[e] = directory_dict(fullpth)
		else:
			contents[e] = file_values(fullpth)
	return contents

class FileWrapper:
	def __init__(self,pth):
		self.pth = pth

	def open(self,mode="r"):
		return open(self.pth,mode)
