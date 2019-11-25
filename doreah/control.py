from ._internal import DEFAULT, defaultarguments, DoreahConfig
import zipfile
import os
import urllib.request
import shutil
import distutils.dir_util
import sys
#import inspect

config = DoreahConfig("control")


def cmd_handle(shortcuts):
	cmd = sys.argv[1:]
	args = []
	kwargs = {}

	while len(cmd) > 0:
		if cmd[0].startswith("-") and cmd[0][1:] in shortcuts:
			kwargs[shortcuts[cmd[0][1:]]] = cmd[1]
			cmd = cmd[2:]
		elif cmd[0].startswith("--"):
			kwargs[cmd[0][2:]] = cmd[1]
			cmd = cmd[2:]
		else:
			args.append(cmd[0])
			cmd = cmd[1:]

	return args,kwargs

def mainfunction(shortcuts,shield=False):
	def decorator(func):
		# define a wrapper function that takes no args itself,
		# but reads them from console and passes them down
		def wrapper():
			args,kwargs = cmd_handle(shortcuts)
			for var in kwargs:
				if var in func.__annotations__:
					kwargs[var] = func.__annotations__[var](kwargs[var])
			return func(*args,**kwargs)

		# if this module is the script, call that function immediately
		if func.__module__ == "__main__":
			wrapper()

		# either return the original function if used with arguments in other places,
		# or return the wrapper if the function is called from command line through
		# some other means (console script)
		return wrapper if shield else func

	return decorator


class Controller:
	def __init__(self,procname,github_project,github_path,custom_functions={},main_script="server.py"):
		self.source_url = "https://github.com/" + github_project
		self.name = github_project.split("/")[-1]
		self.source_path = github_path
		self.custom_functions = custom_functions
		self.main_script = main_script

	def evoke(self):
		if sys.argv[1] == "start": self._start()
		elif sys.argv[1] == "restart": self._start()
		elif sys.argv[1] == "stop": self._stop()
		elif sys.argv[1] == "update": self._update()
		elif sys.argv[1] == "install": _install()
		elif sys.argv[1] in self.custom_functions:
			try:
				self.custom_functions[sys.argv[1]](sys.argv[2:])
			except:
				print("Invalid arguments.")

		else: print("Valid commands:","start","restart","stop","update","install",*[k for k in self.custom_functions])

	def _gotodir(self):
		if os.path.exists(self.main_script):
			return True
		elif os.path.exists("/opt/" + self.name + "/" + self.main_script):
			os.chdir("/opt/" + self.name)
			return True

		print("Installation could not be found.")
		return False

	def _update(self):

		if not self._gotodir(): return False

		if os.path.exists("./.dev"):
			print("Better not overwrite the development server!")
			return

		print("Updating...")

		os.system("wget " + self.source_url + "/archive/master.zip")
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


		distutils.dir_util.copy_tree("./" + self.name + "-master/","./",verbose=2)
		shutil.rmtree("./" + self.name + "-master")
		print("Done!")

		os.chmod(self.name,os.stat(self.name).st_mode | stat.S_IXUSR)

		if stop(): start() #stop returns whether it was running before, in which case we restart it


	def generate_bash_completion(self):
		pass
