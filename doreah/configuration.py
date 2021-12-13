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


	def __init__(self,settings,configfile="settings.ini",save_endpoint="/settings"):
		flatten = {key.lower():settings[category][key] for category in settings for key in settings[category]}
		self.categories = {cat:[k for k in settings[cat]] for cat in settings}
		self.types = {k:flatten[k][0] for k in flatten}
		self.names = {k:flatten[k][1] for k in flatten}
		self.defaults = {k:flatten[k][2] for k in flatten}
		self.usersettings = {}
		#self.expire = {k:flatten[k][3] if len(flatten[k])>3 else -1 for k in flatten}

		self.configfile = configfile
		self.save_endpoint = save_endpoint

		self.load_from_file()

	def update(self,settings):
		for k in settings:
			settings[k] = self.types[k].sanitize(settings[k])
		self.usersettings.update(settings)
		self.write_to_file()

	def get_user(self,key):
		return self.usersettings.get(key)
	def get_default(self,key):
		return self.defaults.get(key)
	def get_active(self,key):
		return self.get_user(key) or self.get_default(key)

	def __getitem__(self,key):
		return self.get_active(key)
		#if key in self.usersettings: return self.usersettings[key]
		#if key in self.defaults: return self.defaults[key]
		#return None

	def __iter__(self):
		return (k for k in self.defaults)

	def todict(self):
		d = {k:self.defaults[k] for k in self.defaults}
		d.update(self.usersettings)
		return d

	def html(self):
		template = JINJAENV.get_template("settings.jinja")
		return template.render({"configuration":self})

	def load_from_file(self):
		ext = self.configfile.split(".")[-1].lower()
		try:
			settings = formats.loaders[ext].load_file(self.configfile)
			settings = {k.lower():settings[k] for k in settings}
			settings = {
				k:settings[k] for k in settings if
				k in self.types and self.types[k].validate(settings[k])
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

# this is just a namespace, not a real class
class types:

	class SettingType:
		def __init__(self):
			pass

		def html(self,active,default,user,setting):
			template = JINJAENV.get_template(self.jinjafile())
			return template.render({"type":self,"active":active,"default":default,"user":user,"setting":setting})

		def jinjafile(self):
			return "types/" + self.__class__.__name__ + ".jinja"

		def sanitize(self,input):
			if self.validate(input):
				return input
			else:
				return self.default

	class Integer(SettingType):
		regex = "[0-9]+"
		default = 0

		def __init__(self,min=-math.inf,max=math.inf):
			self.min = min
			self.max = max

		def validate(self,input):
			return isinstance(input,int) and input >= self.min and input <= self.max

	class String(SettingType):
		regex = "([^'\"]*)"
		default = ""

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

	class MultiChoice(Choice):
		def validate(self,input):
			return all([i in self.options for i in input])

	class Set(SettingType):
		default = []

		def __init__(self,type,minmembers=0,maxmembers=math.inf):
			self.type = type
			self.minmembers = minmembers
			self.maxmembers = maxmembers

		def validate(self,input):
			return len(input) <= self.maxmembers and len(input) >= self.minmembers and all(self.type.validate(m) for m in input)

	class List(SettingType):
		default = []

		def __init__(self,type,minmembers=0,maxmembers=math.inf):
			self.type = type
			self.minmembers = minmembers
			self.maxmembers = maxmembers

		def validate(self,input):
			return len(input) <= self.maxmembers and len(input) >= self.minmembers and all(self.type.validate(m) for m in input)

	class Boolean(SettingType):
		default = False

		def sanitize(self,input):
			if input.lower() == "on":
				return True
			if input.lower() == "off":
				return False
			return input


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
				lines.append(k + " = " + str(data[k]))
			lines.append("")

			return "\n".join(lines)


	loaders = {
		"yaml":YAMLHandler(),
		"yml":YAMLHandler(), #yes, two instances for no reason other than cleaner code
		"json":JSONHandler(),
		"ini":INIHandler()
	}

def test():
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

	print(exampleconfig.usersettings)
	from bottle import run, get

	@get("/")
	def settingspage():
		return exampleconfig.html()

	#run(port=8080,server="waitress")

if __name__ == "__main__":
	test()
