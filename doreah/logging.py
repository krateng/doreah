import datetime
import inspect
import os

from ._color import _ANSICOLOR


class Logger:
	def __init__(self,logfolder="./logs",timeformat="%Y/%m/%d %H:%M:%S",defaultmodule="main",only_leaf_module=True,verbosity=0,maxsize=4*1024*1024):
		self.logfolder = logfolder
		self.timeformat = timeformat
		self.defaultmodule = defaultmodule
		self.only_leaf_module = only_leaf_module
		self.verbosity = verbosity
		self.maxsize = maxsize

		self.queue = []
		self.locked = False

	def log(self,*entries,module=None,indent=0,importance=0,color=None):
		"""Logs all supplied arguments, separate line for each. Only writes to logfile if importance value is lower than the set verbosity value.

		:param string entries: All log entries, one line per entry
		:param string module: Custom category. Log entry will be prepended by this string in the console and be written to this file on disk. Defaults to actual name of the python module.
		:param integer indent: Indent to be added to entry
		:param integer importance: Low means important. If this value is higher than the verbosity, entry will not be shown on console.
		:param string color: Color-codes console output. Can be a hex string, an RGB tuple or the name of a color."""

		now = datetime.datetime.utcnow().strftime(self.timeformat)

		# log() can be used to add empty line
		if len(entries) == 0: entries = ("",)

		# make it easier to log data structures and such
		entries = tuple([str(msg) for msg in entries])

		# indent
		prefix = "\t" * indent

		# module name
		if module is None:
			try:
				moduleobj = inspect.getmodule(inspect.stack()[1][0])
				module = getattr(moduleobj,"__logmodulename__",moduleobj.__name__)
				if self.only_leaf_module: module = module.split(".")[-1]
				if module == "__main__": module = self.defaultmodule
			except Exception:
				module = "interpreter"

		for msg in entries:
			self.queue.append({
				'time':now,
				'prefix':prefix,
				'color':color,
				'msg':msg,
				'module':module,
				'console':(importance <= self.verbosity)
			})

		if self.locked:
			pass
		else:
			self.flush()

	def flush(self):
		"""Outputs and empties the complete backlog."""
		for entry in self.queue:
			# console output
			if entry["console"]:
				colorprefix,colorsuffix = _ANSICOLOR(entry['color'])
				print(f"{colorprefix}[{entry['module']}] {entry['prefix']}{entry['msg']}{colorsuffix}")

			# file output
			if self.logfolder is not None:
				logfilename = f"{self.logfolder}/{entry['module']}.log"
				os.makedirs(os.path.dirname(logfilename), exist_ok=True)
				with open(logfilename,"a") as logfile:
					logfile.write(f"{entry['time']}  {entry['prefix']}{entry['msg']}\n")
				self.trim(logfilename)

		self.queue = []

	def trim(self,filename):

		try:
			#sanity check for old version logfiles
			if os.path.getsize(filename) > (self.maxsize * 4):
				os.remove(filename)

			elif os.path.getsize(filename) > self.maxsize:
				with open(filename,"r") as sourcefile:
					lines = sourcefile.readlines()
					delete = int(len(lines)/2)
				with open(filename,"w") as targetfile:
					targetfile.writelines(lines[delete:])

		except Exception:
			pass


defaultlogger = Logger()
log = defaultlogger.log
