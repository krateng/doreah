import yaml
import random
from jinja2 import Environment, PackageLoader, select_autoescape


jinjaenv = Environment(
	loader=PackageLoader('doreah', 'resources/keystore'),
	autoescape=select_autoescape(['html', 'xml'])
)



charset = list(range(10)) + list("abcdefghijklmnopqrstuvwxyz") + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
def randomstring(length):
	return "".join(str(random.choice(charset)) for _ in range(length))


class KeyStore:
	"""Object that represents keys and their identifiers stored by a user. They are accessible via a web interface
	and written to a permanent file."""

	def __init__(self,file="keystore.yml",save_endpoint="/keys",key_length=64):
		self.file = file
		self.keys = {}
		self.save_endpoint = save_endpoint
		self.key_length = key_length
		self.load_from_file()

	def __len__(self):
		return self.keys.__len__()
	def __getitem__(self,identifier):
		return self.keys[identifier]
	def __setitem__(self,identifier,value):
		self.keys[identifier] = value
		self.write_to_file()

	def __iter__(self):
		return (identifier for identifier in self.keys)

	def check_key(self,key):
		return (key in self.keys.values())

	def check_and_identify_key(self,key):
		for identifier in self.keys:
			if self.keys[identifier] == key:
				return identifier
		return False

	def generate_key(self,identifier):
		key = randomstring(self.key_length)
		self.keys[identifier] = key
		self.write_to_file()
		return key

	def add_key(self,identifier,key):
		self.keys[identifier] = key
		self.write_to_file()

	def delete_key(self,identifier):
		del self.keys[identifier]
		self.write_to_file()

	def update(self,dict):
		for identifier in dict:
			if dict[identifier] is None:
				self.delete_key(identifier)
			else:
				self.add_key(identifier,dict[identifier])

	def load_from_file(self):
		try:
			with open(self.file) as filed:
				self.keys = yaml.safe_load(filed)
		except FileNotFoundError:
			self.write_to_file()

	def write_to_file(self):
		with open(self.file,"w") as filed:
			yaml.dump(self.keys,filed)

	def html(self):
		template = jinjaenv.get_template("settings.jinja")
		return template.render({"keystore":self})
