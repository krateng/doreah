"""Module that offers data structures that are kept persistent on the file system"""

import os, shutil
import yaml, json, configparser
import re, ast


class DiskDict(dict):
	"""This object acts as a dictionary with persistence. It is not meant for big data,
	but simple configuration files and such. Keys are always strings and case-insensitive."""

	def __init__(self,filename,readonly=False,discard_none=False):
		self.filename = filename
		self.internal_dict = {}
		self.handler = get_handler(filename)
		self.readonly = readonly
		self.discard_none = discard_none

		if os.path.exists(self.filename):
			self._sync_from_disk()

		if self.discard_none:
			self.internal_dict = {k:v for k,v in self.internal_dict.items() if v is not None}


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

	special_identifiers = [
		(True,['true','yes','y']),
		(False,['false','no','n']),
		(None,['none','null'])
	]


	def parse_dict_values(self,inputdict):
		outputdict = {}
		for key,val in inputdict.items():
			for resolve_to,values in self.special_identifiers:
				if val.lower() in values:
					val = resolve_to
					break
			else:
				try:
					val = ast.literal_eval(val)
				except Exception:
					val = val # just use as string
			outputdict[key] = val
		return outputdict

	def load_file(self,filename):
		try:
			cfg = configparser.ConfigParser(interpolation=None)
			cfg.read(filename)
			try:
				return self.parse_dict_values(cfg['MALOJA'])
			except KeyError:
				return {}
		except configparser.MissingSectionHeaderError:
			with open(filename,'r') as fd:
				return self.text_to_data("[MALOJA]\n\n" + fd.read())

	def text_to_data(self,txt):
		cfg = configparser.ConfigParser(interpolation=None)
		cfg.read_string(txt)
		return self.parse_dict_values(cfg['MALOJA'])

	def write_descriptor(self,descriptor,data):
		cfg = configparser.ConfigParser(interpolation=None)
		cfg['MALOJA'] = data
		cfg.write(descriptor)
