import os

from ._internal import DEFAULT, defaultarguments, DoreahConfig


# defaultextension	files with this extension will be regarded as valid files. can be overwritten per request.
# comments			whether files may include commenting (indicated by #)
# multitab			whether fields can be separated by multiple tabs (this makes empty fields impossible except when trailing)
config = DoreahConfig("tsv",
	defaultextension=".tsv",
	comments=True,
	multitab=True
)


@defaultarguments(config,comments="comments",multitab="multitab")
def parse(filename,*args,comments=DEFAULT,multitab=DEFAULT):
	"""Parses a tsv-like file.

	:param string filename: File to be parsed
	:param string args: Data types to be read
	:param boolean comments: Whether the file may contain comments
	:param boolean multitab: Whether values can be separated by an arbitrary amount of tabs
	:return: List of entries, one entry per line, each entry a list of fields"""

	if not os.path.exists(filename):
		filename = filename + config["defaultextension"]

	f = open(filename)

	result = []
	for l in [l for l in f if (not l.startswith("#")) and (not l.strip()=="")]:
		l = l.replace("\n","")

		# if the file allows comments, we need to replace the escape sequence and properly stop parsing for inline comments
		if comments:
			l = l.split("#")[0]
			l = l.replace(r"\num","#")
			l = l.replace(r"\hashtag","#")

		# we either allow multiple tabs, or we don't (in which case empty fields are possible)
		if multitab:
			data = list(filter(None,l.split("\t")))
		else:
			data = list(l.split("\t"))

		entry = [] * len(args)
		for i in range(len(args)):
			if args[i] in ["list","ls","array"]:
				try:
					entry.append(data[i].split("␟"))
				except Exception:
					entry.append([])
			elif args[i] in ["string","str","text"]:
				try:
					entry.append(data[i])
				except Exception:
					entry.append("")
			elif args[i] in ["int","integer","num","number"]:
				try:
					entry.append(int(data[i]))
				except Exception:
					entry.append(0)
			elif args[i] in ["bool","boolean"]:
				try:
					entry.append((data[i].lower() in ["true","yes","1","y"]))
				except Exception:
					entry.append(False)
			else:
				raise TypeError()

		result.append(entry)

	f.close()
	return result

@defaultarguments(config,extension="defaultextension")
def parse_all(path,*args,extension=DEFAULT,**kwargs):
	"""Parses all valid files in a specific directory

	:param string path: Directory to search for files
	:param string args: Data types to be read
	:param string extension: Only parse files ending with this string
	:param kwargs: Parse settings to be applied, see :func:`parse`"""

	result = []
	for f in os.listdir(path + "/"):
		if (f.endswith(extension)): # use "" if all files are valid
			result += parse(path + "/" + f,*args,**kwargs)

	return result



def create(filename):
	"""Creates a file if it doesn't already exist

	:param string filename: Full filename"""

	if not os.path.exists(filename):
		open(filename,"w").close()

@defaultarguments(config,comments="comments")
def add_entry(filename,entry,comments=DEFAULT):
	"""Adds an entry to a tsv-like file

	:param string filename: Full filename
	:param iterable entry: List or tuple of fields
	:param boolean comments: Whether the file can contain comments"""

	create(filename)
	# remove all tabs and create tab-separated string
	line = "\t".join([str(field).replace("\t"," ") for field in entry])

	# replace comment symbol
	if comments: line = line.replace("#",r"\num")

	with open(filename,"a") as f:
		f.write(line + "\n")

@defaultarguments(config,comments="comments")
def add_entries(filename,entries,comments=DEFAULT):
	"""Adds several entries to a tsv-like file

	:param string filename: Full filename
	:param iterable entries: List or tuple of entries, each a list of tuple of fields
	:param boolean comments: Whether the file can contain comments"""

	create(filename)

	with open(filename,"a") as f:
		for entry in entries:
			line = "\t".join([str(field).replace("\t"," ") for field in entry])
			if comments: line = line.replace("#",r"\num")
			f.write(line + "\n")
