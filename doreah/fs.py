from ._internal import DEFAULT, defaultarguments, DoreahConfig

config = DoreahConfig("filesystem2",
	ignore_dotfiles=True
)


import os
import shutil
import math


# ABC

class AbstractPath:
	def parent(self):
		try:
			parenttype = self.IS_IN
		except:
			parenttype = self.__class__
		return parenttype(self.path[:-1])


class AbstractDirectory(AbstractPath):
	def mount(self,pth):
		#return self.__class__(self.path + pth.path)
		res = combines[(type(self),type(pth))]
		return res(self.path + pth.path)

	def __add__(self, other):
		return self.mount(other)

	def join(self,pth):
		return os.path.join(self.__path__(),pth)

class AbstractFile(AbstractPath):
	pass



# ABSOLUTE

class AbsolutePath(AbstractPath):
	def __init__(self,path):
		if isinstance(path,str):
			path = os.path.abspath(path)
			path = path.strip("/")
			self.path = path.split("/")
		else:
			self.path = path

	def __path__(self):
		return os.path.join("/",*self.path)

	def exists(self):
		return os.path.exists(self.__path__())


class AbsoluteDirectory(AbstractDirectory,AbsolutePath):
	def __getitem__(self,node):
		trgt = self.join(node)
		if os.path.exists(trgt):
			return AbsoluteFile(trgt)
		else:
			os.makedirs(trgt,exist_ok=True)
			return AbsoluteDirectory(trgt)

	def _listdir(self):
		return os.listdir(self.__path__())

	def files(self):
		for e in self._listdir():
			if os.path.isfile(self.join(e)):
				yield RelativeFile(e)

	def folders(self):
		for e in self._listdir():
			if not os.path.isfile(self.join(e)):
				yield RelativeDirectory(e)

	def all_files_relative(self,maxdepth=math.inf):
		"""Returns all files inside this directory, relative to it"""
		if maxdepth == 0: return
		for f in self.files():
			yield f
		for f in self.folders():
			for ff in self.mount(f).all_files_relative(maxdepth=maxdepth-1):
				yield f.mount(ff)

	def copyto(self,trgt):
		"""Copies this directory to the target directory"""
		assert not os.path.exists(trgt.__path__())
		shutil.copytree(self.__path__(),trgt.__path__())

	def copypath(self,relpth,targetdir):
		"""Copies the given relative path from this directory to the target directory, preserving the full path"""
		src = self.mount(relpth)
		trgt = targetdir.mount(relpth)
		src.copyto(trgt)



class AbsoluteFile(AbstractFile,AbsolutePath):
	IS_IN = AbsoluteDirectory

	def copyto(self,trgt):
		assert not os.path.exists(trgt.__path__())
		shutil.copy(self.__path__(),trgt.__path__())

	def open(self,mode="r"):
		return open(self.__path__(),mode=mode)


# RELATIVE

class RelativePath(AbstractPath):
	def __init__(self,path):
		if isinstance(path,str):
			path = path.strip("/")
			self.path = path.split("/")
		else:
			self.path = path


	def mountin(self,pth):
		return pth.mount(self)

	def __path__(self):
		return os.path.join(*self.path)

class RelativeDirectory(AbstractDirectory,RelativePath):
	pass

class RelativeFile(AbstractFile,RelativePath):
	IS_IN = RelativeDirectory
	pass



combines = {
	(AbsoluteDirectory,RelativeDirectory): AbsoluteDirectory,
	(AbsoluteDirectory,RelativeFile): AbsoluteFile,
	(RelativeDirectory,RelativeDirectory): RelativeDirectory,
	(RelativeDirectory,RelativeFile): RelativeFile

}
