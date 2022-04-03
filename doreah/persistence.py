"""Module that offers data structures that are kept persistent on the file system"""

import os, shutil
import yaml, json
import re


class DiskDict(dict):
	"""This object acts as a dictionary with persistence. It is not meant for big data,
	but simple configuration files and such. Keys are always strings and case-insensitive."""

	def __init__(self,filename,readonly=False):
		self.filename = filename
		self.internal_dict = {}
		self.handler = get_handler(filename)
		self.readonly = readonly

		if os.path.exists(self.filename):
			self._sync_from_disk()


		try:
			self._sync_to_disk()
		except PermissionError as e:
			self.readonly = True

	def _sync_from_disk(self):
		data = self.handler.load_file(self.filename)
		data = {k.lower():data[k] for k in data}
		self.internal_dict = data
		#self.internal_dict.update(data)
	def _sync_to_disk(self):
		if not self.readonly:
			tmpfile = self.filename + ".tmp"
			data = {k.lower():self.internal_dict[k] for k in self.internal_dict}
			self.handler.write_file(tmpfile,data)
			shutil.move(tmpfile,self.filename)

	def __repr__(self):
		return self.internal_dict.__repr__()

	def __setitem__(self,key,value):
		if self.readonly: raise PermissionError
		self._sync_from_disk()
		self.internal_dict.__setitem__(key.lower(),value)
		self._sync_to_disk()

	def __getitem__(self,key):
		self._sync_from_disk()
		return self.internal_dict.__getitem__(key.lower())

	def __delitem__(self,key):
		if self.readonly: raise PermissionError
		self._sync_from_disk()
		self.internal_dict.__delitem__(key.lower())
		self._sync_to_disk()

	def get(self,key):
		return self.internal_dict.get(key)

	# update should save to disk only once. no need to do it for every entry
	def update(self,otherdict):
		if self.readonly: raise PermissionError
		self._sync_from_disk()
		self.internal_dict.update(otherdict)
		self._sync_to_disk()




# Handlers for the different data file types.

handlers = {}

def get_handler(filename):
	ext = filename.split('.')[-1].lower()
	return handlers[ext]


class GenericHandler:
	def __init_subclass__(cls):
		for ext in cls.extensions:
			handlers[ext] = cls()

	def load_file(self,filename):
		with open(filename) as descriptor:
			return self.load_descriptor(descriptor)

	def write_file(self,filename,data):
		with open(filename,"w") as descriptor:
			return self.write_descriptor(descriptor,data)


	def load_descriptor(self,descriptor):
		txt = descriptor.read()
		return self.text_to_data(txt)

	def write_descriptor(self,descriptor,data):
		txt = self.data_to_text(data)
		return descriptor.write(txt)


class YAMLHandler(GenericHandler):
	extensions = ["yml","yaml"]

	def load_descriptor(self,descriptor):
		return yaml.safe_load(descriptor)

	def write_descriptor(self,descriptor,data):
		return yaml.dump(data,descriptor)

class JSONHandler(GenericHandler):
	extensions = ["json"]

	def load_descriptor(self,descriptor):
		return json.load(descriptor)

class INIHandler(GenericHandler):
	extensions = ["ini"]

	boolx = lambda x: True if x.lower() in ['true','yes','y'] else False if x.lower() in ['false','no','n'] else None
	nullx = lambda x: None
	regex_key = 					re.compile(r"([a-zA-Z][\w]+)"	) # at least 2 characters
	regex_values = [
		("singlequoted",	str,	re.compile(r"'([^']*)'")),
		("doublequoted",	str,	re.compile(r'"([^"]*)"')),
		("boolean",			boolx,	re.compile(r"(false|no|n|true|yes|y)",re.IGNORECASE)),
		("null",			nullx,	re.compile(r"(none|null)",re.IGNORECASE)),
		("identifier",		str,	re.compile(r"([a-zA-Z][\w]+)")),
		("integer",			int,	re.compile(r"([-+]?[\d]+)")),
		("float",			float,	re.compile(r"([\d]+[.]?[\d]*)"))
	]
	regex_separator = 				re.compile(r"[ \t]*=[ \t]*")

	regex_value = re.compile("(" + "|".join(exp.pattern for nm,ty,exp in regex_values) + ")")
	regex_fullline = re.compile("".join(exp.pattern for exp in [
		regex_key,
		regex_separator,
		regex_value
	]))


	def text_to_data(self,txt):
		result = {}
		for l in txt.split("\n"):
			match = self.regex_fullline.fullmatch(l)
			if match:
				key, val, *_ = match.groups()
				for nm,ty,exp in self.regex_values:
					match = exp.fullmatch(val)
					if match:
						val = match.groups()[0]
						result[key] = ty(val)
						break

		return result

	def data_to_text(self,data):
		lines = []
		for k in data:
			if isinstance(data[k],str):
				if '"' not in data[k]: val = f'"{data[k]}"'
				elif "'" not in data[k]: val = f"'{data[k]}'"
			else: val = str(data[k])
			lines.append(k + " = " + val)
		lines.append("")

		return "\n".join(lines)
