from ._internal import DEFAULT, defaultarguments, DoreahConfig
import math
import string
import re
from jinja2 import Environment, PackageLoader, select_autoescape

config = DoreahConfig("configuration",
)


JINJAENV = Environment(
	loader=PackageLoader('doreah', 'res/configuration'),
	autoescape=select_autoescape(['html', 'xml'])
)


class Configuration:

	def __init__(self,settings,configfiles=("settings.ini",)):
		flatten = {key.lower():settings[category][key] for category in settings for key in settings[category]}
		self.categories = {cat:[k for k in settings[cat]] for cat in settings}
		self.types = {k:flatten[k][0] for k in flatten}
		self.names = {k:flatten[k][1] for k in flatten}
		self.defaults = {k:flatten[k][2] for k in flatten}
		self.expire = {k:flatten[k][3] if len(flatten[k])>3 else -1 for k in flatten}

		self.configfiles = configfiles

		self.user_overrides = {}
		self.load_from_files()




	def __getitem__(self,key):
		if key in self.user_overrides: return self.user_overrides[key]
		if key in self.defaults: return self.defaults[key]
		return None

	def __iter__(self):
		return (k for k in self.defaults)

	def todict(self):
		d = {k:self.defaults[k] for k in self.defaults}
		d.update(self.user_overrides)
		return d

	def html(self):
		template = JINJAENV.get_template("settings.jinja")
		return template.render({"configuration":self})

	def load_from_files(self):
		for f in self.configfiles:
			settings = self.load_from_file(f)
			self.user_overrides.update(settings)


	def load_from_file(self,filename):
		ext = filename.split(".")[-1].lower()
		try:
			settings = formats.loaders[ext].load_file(filename)
			settings = {k.lower():settings[k] for k in settings}
			settings = {
				k:settings[k] for k in settings if
				k in self.types and self.types[k].validate(settings[k])
			}
			return settings
		except:
			print("Could not load file",filename)
			return {}


# this is just a namespace, not a real class
class types:

	class SettingType:
		def html(self,default,user):
			template = JINJAENV.get_template(self.jinjafile())
			return template.render({"type":self,"default":default,"user":user})

		def jinjafile(self):
			return "types/" + self.__class__.__name__ + ".jinja"

	class Integer(SettingType):
		regex = "[0-9]+"

		def __init__(self,min=-math.inf,max=math.inf):
			self.min = min
			self.max = max

		def validate(self,input):
			return isinstance(input,int) and input >= self.min and input <= self.max

	class String(SettingType):
		regex = "([^'\"]*)"

		def __init__(self,minlength=0,maxlength=math.inf):
			self.minlength = minlength
			self.maxlength = maxlength

		def validate(self,input):
			return isinstance(input,str) and len(input) >= self.minlength and len(input) <= self.maxlength

	class ASCIIString(String):
		regex = r"\w*"

		def validate(self,input):
			return isinstance(input,str) and len(input) >= self.minlength and len(input) <= self.maxlength

	class Choice(SettingType):
		def __init__(self,options=()):
			self.options = options

		def validate(self,input):
			return input in self.options

	class Set(SettingType):
		def __init__(self,type,minmembers=0,maxmembers=math.inf):
			self.type = type
			self.minmembers = minmembers
			self.maxmembers = maxmembers

		def validate(self,input):
			return len(input) <= self.maxmembers and len(input) >= self.minmembers and all(self.type.validate(m) for m in input)


class formats:
	class GenericHandler:
		def load_file(self,filename):
			with open(filename) as descriptor:
				return self.load_descriptor(descriptor)

		def load_descriptor(self,descriptor):
			txt = descriptor.read()
			return self.load_text(txt)

	class YAMLHandler(GenericHandler):
		import yaml
		def load_descriptor(self,descriptor):
			return yaml.safe_load(descriptor)

	class JSONHandler(GenericHandler):
		import json
		def load_descriptor(self,descriptor):
			return json.load(descriptor)

	class INIHandler(GenericHandler):

		regex_key = 					re.compile(r"([a-zA-Z][\w]+)"	) # at least 2 characters
		regex_values = [
			("singlequoted",	str,	re.compile(r"'([^']*)'")),
			("doublequoted",	str,	re.compile(r'"([^"]*)"')),
			("identifier",		str,	re.compile(r"([a-zA-Z][\w]+)")),
			("integer",			int,	re.compile(r"([\d]+)")),
			("float",			float,	re.compile(r"([\d]+[.]?[\d]*)"))
		]
		regex_separator = 				re.compile(r"[ \t]*=[ \t]*")

		regex_value = re.compile("(" + "|".join(exp.pattern for nm,ty,exp in regex_values) + ")")
		regex_fullline = re.compile("".join(exp.pattern for exp in [
			regex_key,
			regex_separator,
			regex_value
		]))


		def load_text(self,txt):
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

	loaders = {
		"yaml":YAMLHandler(),
		"yml":YAMLHandler(), #yes, two instances for no reason other than cleaner code
		"json":JSONHandler(),
		"ini":INIHandler()
	}

exampleconfig = Configuration(
	settings={
		"Group":{
			"name":(types.String(),					"Group Name",		"Fellowship of the Ring"),
			"employer":(types.String(),				"Employer",			"Council of Elrond"),
			"members":(types.Set(types.String()),	"Members",			["Gandalf","Aragorn","Boromir","Legolas","Gimli","Frodo","Samwise","Peregrin","Meriadoc"])
		},
		"Mission":{
			"start":(types.String(),				"Start Point",		"Rivendell"),
			"target":(types.String(),				"Target",			"Mount Doom"),
			"timebudget":(types.Integer(min=4),		"Estimated Days",	360)
		}
	}

)

from bottle import run, get

@get("/")
def settingspage():
	return exampleconfig.html()

run(port=8080,server="waitress")
