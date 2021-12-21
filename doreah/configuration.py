from ._internal import DEFAULT, defaultarguments, DoreahConfig
import math
import string
import re
import os
from jinja2 import Environment, PackageLoader, select_autoescape

## for these configuration objects:
## 		NONE always is equivalent to the setting not being specified - i.e. fallback to default
##		FALSE can be used as a sentinel regardless of type
##
##		parsing and conversion of values should be done client-side. the server only checks if valid and rejects if not




config = DoreahConfig("configuration",
)


JINJAENV = Environment(
	loader=PackageLoader('doreah', 'res/configuration'),
	autoescape=select_autoescape(['html', 'xml'])
)


class Configuration:


	def __init__(self,settings,configfile="settings.ini",save_endpoint="/settings",env_prefix=None):
		flatten = {key.lower():settings[category][key] for category in settings for key in settings[category]}
		self.categories = {cat:[k for k in settings[cat]] for cat in settings}
		self.types = {k:flatten[k][0] for k in flatten}
		self.names = {k:flatten[k][1] for k in flatten}
		self.descs = {k:flatten[k][3] for k in flatten if len(flatten[k]) > 3}

		self.usersettings = {}
		self.environment = {}
		self.defaults = {k:flatten[k][2] for k in flatten}
		#self.expire = {k:flatten[k][3] if len(flatten[k])>3 else -1 for k in flatten}

		self.configfile = configfile
		self.save_endpoint = save_endpoint
		self.env_prefix = env_prefix

		self.load_environment()
		self.load_from_file()

	def update(self,settings):
		for k in settings:
			if settings[k] is None: del self.usersettings[k]
			else: self.usersettings[k] = self.types[k].sanitize(settings[k])
		self.write_to_file()



	def get_user(self,key):
		return self.usersettings.get(key.lower())
	def get_env(self,key):
		return self.environment.get(key.lower())
	def get_default(self,key):
		return self.defaults.get(key.lower())


	# this method gets the setting only if it's not the web/file-adjustable one
	def get_fallback(self,key):
		for layer in (self.get_env,self.get_default):
			val = layer(key)
			if val is not None: return val
		return None

	# this method gets the setting only if it has in any way been user-specified
	def get_specified(self,key):
		for layer in (self.get_user,self.get_env):
			val = layer(key)
			if val is not None: return val
		return None

	# get the one that's valid
	def get_active(self,key):
		v = self.get_user(key)
		if v is None: v = self.get_fallback(key)
		return v

	def __getitem__(self,key):
		# special case to support easier transition from settings module
		if isinstance(key,tuple):
			return (self[k] for k in key)
		return self.get_active(key)
		#if key in self.usersettings: return self.usersettings[key]
		#if key in self.defaults: return self.defaults[key]
		#return None

	def __setitem__(self,key,value):
		self.usersettings[key] = value
		self.write_to_file()

	def __iter__(self):
		return (k for k in self.defaults)

	def todict(self):
		d = {k:self.defaults[k] for k in self.defaults}
		d.update(self.usersettings)
		return d

	def html(self):
		template = JINJAENV.get_template("settings.jinja")
		return template.render({"configuration":self})

	def load_environment(self):
		if self.env_prefix is not None:
			for k in os.environ:
				if k.startswith(self.env_prefix.upper()):
					sk = k[len(self.env_prefix):].lower()
					if sk in self.types:
						self.environment[sk] = self.types[sk].fromstring(os.environ[k])
			#self.environment = {k[len(self.env_prefix):].lower():os.environ[k] for k in os.environ if k.startswith(self.env_prefix.upper())}

	def load_from_file(self):
		ext = self.configfile.split(".")[-1].lower()
		try:
			settings = formats.loaders[ext].load_file(self.configfile)
			settings = {k.lower():settings[k] for k in settings}
			settings = {
				k:settings[k] for k in settings if
				k in self.types and (self.types[k].validate(settings[k]) or settings[k] is False)
			}
			self.usersettings = settings
		except:
			print("Could not load file",self.configfile)

	def write_to_file(self):
		ext = self.configfile.split(".")[-1].lower()
		try:
			formats.loaders[ext].write_file(self.configfile,self.usersettings)
		except:
			print("Could not write file",self.configfile)
			raise


	def render_help(self,targetfile,top_text=""):
		template = JINJAENV.get_template("settings.md.jinja")
		txt = template.render({"configuration":self,"top_text":top_text})
		with open(targetfile,"w") as fd:
			fd.write(txt)

# this is just a namespace, not a real class
class types:

	class SettingType:
		def __init__(self):
			pass

		def __desc__(self):
			return "Generic Datatype"

		# render the html element for the web interface
		def html(self,active,default,user,setting):
			template = JINJAENV.get_template(self.jinjafile())
			return template.render({"type":self,"active":active,"default":default,"user":user,"setting":setting})

		def jinjafile(self):
			return "types/" + self.__class__.__name__ + ".jinja"

		# block invalid values
		def sanitize(self,input):
			if self.validate(input) or input is False: # False is always allowed
				return input
			else:
				return self.default

		# return how it should be displayed in an html settings field
		def html_value(self,value):
			return value

		# parse string inputs
		def fromstring(self,input):
			return input

	class Integer(SettingType):
		regex = "[0-9]+"
		default = 0

		def __init__(self,min=-math.inf,max=math.inf):
			self.min = min
			self.max = max

		def __desc__(self):
			return "Integer"

		def validate(self,input):
			return isinstance(input,int) and input >= self.min and input <= self.max

		def fromstring(self,input):
			try: return int(input)
			except: return None

	class String(SettingType):
		regex = "([^'\"]*)"
		default = ""

		def __init__(self,minlength=0,maxlength=math.inf):
			self.minlength = minlength
			self.maxlength = maxlength

		def __desc__(self):
			return "String"

		def validate(self,input):
			return isinstance(input,str) and len(input) >= self.minlength and len(input) <= self.maxlength

		def html_value(self,value):
			if value in [None,False]: return ""
			else: return value

	class ASCIIString(String):
		regex = r"\w*"

		def __desc__(self):
			return "ASCII String"

		def validate(self,input):
			return isinstance(input,str) and len(input) >= self.minlength and len(input) <= self.maxlength

	class Choice(SettingType):
		def __init__(self,options=()):
			self.options = options

		def __desc__(self):
			return "Choice"

		def validate(self,input):
			return input in self.options

	class MultiChoice(Choice):

		def __desc__(self):
			return "Multiple Choice"
		def validate(self,input):
			return all([i in self.options for i in input])

	class Set(SettingType):
		default = []

		def __init__(self,type,minmembers=0,maxmembers=math.inf):
			self.type = type
			self.minmembers = minmembers
			self.maxmembers = maxmembers

		def __desc__(self):
			return "Set"

		def validate(self,input):
			return len(input) <= self.maxmembers and len(input) >= self.minmembers and all(self.type.validate(m) for m in input)

	class List(SettingType):
		default = []

		def __init__(self,type,minmembers=0,maxmembers=math.inf):
			self.type = type
			self.minmembers = minmembers
			self.maxmembers = maxmembers

		def __desc__(self):
			return "List"

		def validate(self,input):
			return len(input) <= self.maxmembers and len(input) >= self.minmembers and all(self.type.validate(m) for m in input)

	class Boolean(SettingType):
		default = False

		def __desc__(self):
			return "Boolean"

		def validate(self,input):
			return input in [True,False]

		def fromstring(self,input):
			if input.lower() in ['true','yes','y','on']: return True
			if input.lower() in ['false','no','n','off']: return False
			return None


class formats:
	class GenericHandler:

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
		import yaml
		def load_descriptor(self,descriptor):
			return yaml.safe_load(descriptor)

	class JSONHandler(GenericHandler):
		import json
		def load_descriptor(self,descriptor):
			return json.load(descriptor)

	class INIHandler(GenericHandler):

		boolx = lambda x: True if x.lower() in ['true','yes','y'] else False if x.lower() in ['false','no','n'] else None
		regex_key = 					re.compile(r"([a-zA-Z][\w]+)"	) # at least 2 characters
		regex_values = [
			("singlequoted",	str,	re.compile(r"'([^']*)'")),
			("doublequoted",	str,	re.compile(r'"([^"]*)"')),
			("boolean",			boolx,	re.compile(r"(false|no|n|true|yes|y)",re.IGNORECASE)),
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
				lines.append(k.upper() + " = " + val)
			lines.append("")

			return "\n".join(lines)


	loaders = {
		"yaml":YAMLHandler(),
		"yml":YAMLHandler(), #yes, two instances for no reason other than cleaner code
		"json":JSONHandler(),
		"ini":INIHandler()
	}
