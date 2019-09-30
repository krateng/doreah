import datetime
import inspect
import os

from ._internal import defaultarguments, gopen, DoreahConfig


_queue = []
_locked = False


# logfolder			folder to store logfiles in
# timeformat		strftime format for log files
# defaultmodule		name for the main running script
# verbosity			higher means more (less important) messages are shown on console
config = DoreahConfig("logging",
	logfolder="logs",
	timeformat="%Y/%m/%d %H:%M:%S",
	defaultmodule="main",
	verbosity=0
)



def _colorcodes(color):
	if color is None: return "",""
	names = {
		"red":(255,0,0),
		"green":(0,255,0),
		"blue":(0,0,255)
	}
	if color in names:
		color = names[color]
	if isinstance(color,str) and color.startswith("#"):
		color = int(color[1:3],16),int(color[3:5],16),int(color[5:7],16)

	start = "\033[38;2;" + ";".join(str(c) for c in color) + "m"
	end = "\033[0m"
	return start,end


def log(*entries,module=None,heading=None,indent=0,importance=0,color=None):
	"""Logs all supplied arguments, separate line for each. Only writes to logfile if importance value is lower than the set verbosity value.

	:param string entries: All log entries, one line per entry
	:param string module: Custom category. Log entry will be prepended by this string in the console and be written to this file on disk. Defaults to actual name of the python module.
	:param integer heading: Heading category. Headings will be visually distinguished from normal entries.
	:param integer indent: Indent to be added to entry
	:param integer importance: Low means important. If this value is higher than the verbosity, entry will not be shown on console.
	:param string color: Color-codes console output. Can be a hex string, a RGB tuple or the name of a color."""

	now = datetime.datetime.utcnow().strftime(config["timeformat"])


	colorprefix,colorsuffix = _colorcodes(color)

	# log() can be used to add empty line
	if len(entries) == 0: entries = ("",)

	# make it easier to log data structures and such
	entries = tuple([str(msg) for msg in entries])

	# header formating
	if heading == 2:
		entries = ("","","####") + entries + ("####","")
	elif heading == 1:
		entries = ("","","","# # # # #","") + entries + ("","# # # # #","","")

	# indent
	prefix = "\t" * indent

	# module name
	if module is None:
		try:
			module = inspect.getmodule(inspect.stack()[1][0]).__name__
			if module == "__main__": module = config["defaultmodule"]
		except:
			module = "interpreter"

	global _locked, _queue
	if _locked:
		for msg in entries:
			_queue.append({"time":now,"prefix":prefix,"msg":msg,"module":module,"console":(importance <= config["verbosity"])})
	else:
		# console output
		if (importance <= config["verbosity"]):
			for msg in entries:
				print(colorprefix + "[" + module + "] " + prefix + msg + colorsuffix)

		# file output
		logfilename = config["logfolder"] + "/" + module + ".log"
		#os.makedirs(os.path.dirname(logfilename), exist_ok=True)
		with gopen(logfilename,"a") as logfile:
			for msg in entries:
				logfile.write(now + "  " + prefix + msg + "\n")


def flush():
	"""Outputs and empties the complete backlog."""
	global _queue
	for entry in _queue:
		# console output
		if entry["console"]:
			print("[" + entry["module"] + "] " + entry["prefix"] + entry["msg"])

		# file output
		logfilename = config["logfolder"] + "/" + entry["module"] + ".log"
		#os.makedirs(os.path.dirname(logfilename), exist_ok=True)
		with gopen(logfilename,"a") as logfile:
			logfile.write(entry["time"] + "  " + entry["prefix"] + entry["msg"] + "\n")

	_queue = []

# Quicker way to add header
def logh1(*args,**kwargs):
	"""Logs a top-level header. Otherwise, same arguments as :func:`log`"""
	return log(*args,**kwargs,header=1)
def logh2(*args,**kwargs):
	"""Logs a second-level header. Otherwise, same arguments as :func:`log`"""
	return log(*args,**kwargs,header=2)
