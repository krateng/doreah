from ._internal import DEFAULT, defaultarguments, DoreahConfig
import zipfile
import os
import urllib.request
import shutil
import distutils.dir_util

config = DoreahConfig("control")


class Controller:
	def __init__(self,procname,source_url,source_path,custom_functions={}):
		self.source_url = source_url
		self.source_path = source_path
		self.custom_functions = custom_functions

	def evoke(self):
		if sys.argv[1] == "start": self._start()
		elif sys.argv[1] == "restart": self._start()
		elif sys.argv[1] == "stop": self._stop()
		elif sys.argv[1] == "update": self._update()
		elif sys.argv[1] == "install": installhere()
		else: print("Valid commands:","start","restart","stop","update","install",*[k for k in self.custom_functions])

	def _update(self):

		if not gotodir(): return False

		if os.path.exists("./.dev"):
			print("Better not overwrite the development server!")
			return

		print("Updating...")

		os.system("wget " + self.source_url)
		with zipfile.ZipFile("./master.zip","r") as z:


			for f in z.namelist():
				if f.startswith(self.source_path):
					z.extract(f)
			for dir,_,files in os.walk("./" + self.source_path):
				for f in files:
					origfile = os.path.join(dir,f)
					newfile = os.path.join(dir[(len(self.source_path)+1):],f)
					os.renames(origfile,newfile) #also prunes empty directory

		os.remove("./master.zip")


		distutils.dir_util.copy_tree("./maloja-master/","./",verbose=2)
		shutil.rmtree("./maloja-master")
		print("Done!")

		os.chmod("./maloja",os.stat("./maloja").st_mode | stat.S_IXUSR)

		print("Make sure to update required modules! (" + yellow("pip3 install -r requirements.txt --upgrade --no-cache-dir") + ")")

		if stop(): start() #stop returns whether it was running before, in which case we restart it


	def generate_bash_completion(self):
		pass
