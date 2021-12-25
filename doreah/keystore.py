from ._internal import DoreahConfig


config = DoreahConfig("keystore",
)


class KeyStore:
	"""Object that represents keys and their identifiers stored by a user. They are accessible via a web interface
	and written to a permanent file."""

	def __init__(self,file="keystore.yml",save_endpoint="/keys"):
		self.file = file
		self.keys = {}
		self.save_endpoint = save_endpoint
		self.load_from_file()

	def add_key(self,key,identifier):
		self.keys[identifier] = key
		self.write_to_file()

	def check_key(self,key):
		return (key in self.keys.values())

	def load_from_file(self):
		try:
			with open(self.file) as filed:
				self.keys = yaml.safe_load(filed)
		except FileNotFoundError:
			self.write_to_file()

	def write_to_file(self):
		with open(self.file,"w") as filed:
			yaml.dump(self.keys,filed)
