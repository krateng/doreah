from ._internal import DEFAULT, defaultarguments, DoreahConfig
import os
import shutil

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



class FileWrapper:
	def __init__(self,pth):
		self.pth = pth

	def open(self,mode="r"):
		return open(self.pth,mode)

	def mtime(self):
		return int(os.path.getmtime(self.pth))

	def ext(self):
		return self.pth.split(".")[-1].lower()

	def remove(self):
		os.remove(self.pth)

###
# These don't technically represent relative paths, but absolute paths with
# context information about what they're relative to
###

class RelativePath:
	def __init__(self,relpath,root=None):
		if root is None: root = os.curdir
		self.pth = os.path.join(root,relpath)
		self.root = root
		self.relpath = relpath

	def __str__(self):
		return self.relpath

	def parentview(self):
		newroot, parent = os.path.split(self.root)
		newrel = os.path.join(parent, self.relpath)
		return self.__class__(relpath=newrel,root=newroot)

	def copyinto(self,targetdir):
		target = os.path.join(targetdir.fullpath,self.relpath)
		os.makedirs(os.path.dirname(target),exist_ok=True)
		shutil.copytree(self.pth,target)

class RelativeFile(RelativePath,FileWrapper):
	def copyinto(self,targetdir,rename=None):
		target = os.path.join(targetdir.fullpath,self.relpath)
		os.makedirs(os.path.dirname(target),exist_ok=True)
		if rename is not None: target = os.path.join(os.path.dirname(target),rename)
		shutil.copy(self.pth,target)



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


class Directory:
	def __init__(self,path,exclude_dotfiles=True):
		self.fullpath = path
		self.folderdict = {}
		for e in os.listdir(path):
			if e.startswith(".") and exclude_dotfiles: continue
			fullpth = os.path.join(path,e)
			if os.path.isdir(fullpth):
				self.folderdict[e] = Directory(fullpth)
			else:
				self.folderdict[e] = RelativeFile(e,root=self.fullpath)

	def __getitem__(self,node):
		try:
			return self.folderdict[node]
		except:
			os.makedirs(os.path.join(self.fullpath,node))
			self.folderdict[node] = {}
			return self.folderdict[node]

	def relfile(self,relpath):
		return RelativeFile(relpath=relpath,root=self.fullpath)


	# returns all files in this directory tree relative to it
	def allfiles(self,exclude=()):
		for nodename in self.folderdict:
			if nodename in exclude: continue
			node = self.folderdict[nodename]
			if isinstance(node,Directory):
				#yield from r.allfiles()
				for f in node.allfiles():
					yield f.parentview()
			else:
				yield node
