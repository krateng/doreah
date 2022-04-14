from ._internal import DEFAULT, defaultarguments, DoreahConfig
from .io import col
import zipfile
import os
import urllib.request
import shutil
import distutils.dir_util
import sys
import subprocess
import signal
#import inspect


config = DoreahConfig("control")


def cmd_handle(shortcuts,flags):
	cmd = sys.argv[1:]
	args = []
	kwargs = {}

	while len(cmd) > 0:
		# boolean args don't need an actual argument in the command line - their
		# presence means true
		if cmd[0].startswith("--") and cmd[0][2:] in flags:
			kwargs[cmd[0][2:]] = True
			cmd = cmd[1:]
		elif cmd[0].startswith("-") and cmd[0][1:] in shortcuts:
			#kwargs[shortcuts[cmd[0][1:]]] = cmd[1]
			#cmd = cmd[2:]
			# simply convert to real option and run again
			cmd[0] = "--" + shortcuts[cmd[0][1:]]
		elif cmd[0].startswith("--"):
			kwargs[cmd[0][2:]] = cmd[1]
			cmd = cmd[2:]
		else:
			args.append(cmd[0])
			cmd = cmd[1:]

	return args,kwargs

def mainfunction(shortcuts={},flags=[],shield=False):
	def decorator(func):
		# define a wrapper function that takes no args itself,
		# but reads them from console and passes them down
		def wrapper():
			args,kwargs = cmd_handle(shortcuts,flags)
			for var in kwargs:
				if var in func.__annotations__:
					kwargs[var] = func.__annotations__[var](kwargs[var])
			result = func(*args,**kwargs)
			# Truthy return value indicates success -> exit code 0
			return 0 if result else 1

		# if this module is the script, call that function immediately
		if func.__module__ == "__main__":
			wrapper()

		# either return the original function if used with arguments in other places,
		# or return the wrapper if the function is called from command line through
		# some other means (console script)
		return wrapper if shield else func

	return decorator


class Controller:
	def __init__(self,pkgname,processname=None,prettyname=None):
		self.pkgname = pkgname
		self.processname = processname if processname is not None else self.pkgname
		self.prettyname = prettyname if prettyname is not None else self.processname.capitalize()

		self.actions = {
			"start":self.start,
			"restart":self.restart,
			"stop":self.stop
		}


	def getInstance(self):
		try:
			output = subprocess.check_output(["pidof",self.processname])
			pid = int(output)
			return pid
		except:
			return None
	def is_running(self):
		return getInstance() is not None

	def start(self):
		try:
			p = subprocess.Popen(["python3","-m",self.pkgname + ".main"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
			print(col["green"](self.prettyname + " started!") + " PID: " + str(p.pid))
		except:
			print("Error while starting " + self.prettyname + ".")
			return False

	def restart(self):
		wasrunning = stop()
		start()
		return wasrunning

	def stop(self):
		pid = getInstance()
		if pid is None:
			print(self.prettyname + " is not running")
			return False
		else:
			os.kill(pid,signal.SIGTERM)
			print(self.prettyname + " stopped! PID: " + str(pid))
			return True
