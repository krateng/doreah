import pickle
import yaml


from ._internal import DEFAULT, defaultarguments, DoreahConfig

config = DoreahConfig("database")
config._initial()



class Ref:
	def __init__(self,cls,backref=None,exclusive=False):
		self.cls = cls
		self.backref = backref
		self.exclusive = exclusive

class MultiRef(Ref):
	pass

class Database:

	def getall(self,cls):
		return self.class_to_objects.get(cls)

	def get(self,id):
		return self.id_to_object[id]

	def __init__(self_db,file="database.ddb"):
		print("Initializing database...")
		self_db.file = file

		self_db.id_to_object = {}
		self_db.class_to_objects = {}

		self_db.loadarea = {}
		self_db.load()

		# every instance creates a class to inherit from
		class obj:
			def __repr__(self):
				for attr in ["name","title","identifier"]:
					try:
						name = getattr(self,attr)
						break
					except:
						pass
				else:
					name = "Unknown"
				return "<[" + str(self.uid) + "] " + self.__class__.__name__  + " '" + name + "'>"

			def __init_subclass__(cls):
				# register class
				self_db.class_to_objects[cls] = []
				print("New database class defined:",cls)

				# create constructor
				types = cls.__annotations__
				def init(self,types=types,force_uid=None,**vars):
					for v in vars:
						# set attributes according to keyword arguments
						assert isinstance(vars[v],types[v])
						setattr(self,v,vars[v])

					# set defaults
					for v in types:
						if v not in vars:
							setattr(self,v,types[v]()) # can just call type to get a version of it, e.g. list() -> []

					# register object with Database
					self.uid = force_uid if force_uid is not None else \
						max(self_db.id_to_object) + 1 if len(self_db.id_to_object) > 0 else 0
					self_db.id_to_object[self.uid] = self
					self_db.class_to_objects[cls].append(self)

				cls.__init__ = init



				# add to referenced classes
				for v in types:
					if v in cls.__dict__:
						classvar = cls.__dict__[v]
						if isinstance(classvar,Ref) and classvar.backref is not None:
							# make getter method that checks instances of THIS object for references to the target object


							# 1 to 1
							if classvar.exclusive and not isinstance(classvar,MultiRef):
								def find_object_that_references_me(self,attr=v):
									for obj in self_db.class_to_objects[cls]:
										if obj.__getattribute__(attr) is self: return obj
								prop = property(find_object_that_references_me)

							# many to 1
							elif not classvar.exclusive and not isinstance(classvar,MultiRef):
								def find_objects_that_reference_me(self,attr=v):
									for obj in self_db.class_to_objects[cls]:
										if obj.__getattribute__(attr) is self: yield obj
								prop = property(find_objects_that_reference_me)

							# 1 to many
							elif classvar.exclusive and isinstance(classvar,MultiRef):
								def find_object_that_references_me_among_others(self,attr=v):
									for obj in self_db.class_to_objects[cls]:
										if self in obj.__getattribute__(attr): return obj
								prop = property(find_object_that_references_me_among_others)

							# many to many
							elif not classvar.exclusive and isinstance(classvar,MultiRef):
								def find_objects_that_reference_me_among_others(self,attr=v):
									for obj in self_db.class_to_objects[cls]:
										if self in obj.__getattribute__(attr): yield obj
								prop = property(find_objects_that_reference_me_among_others)


							setattr(classvar.cls,classvar.backref,prop)


				# after every class is defined, check if we can create new objects
				self_db.inject()

		self_db.DBObject = obj


	def save(self_db):

		d = {}
		for cls in self_db.class_to_objects:
			d[cls.__name__] = []
			for obj in self_db.class_to_objects[cls]:
				objd = {"uid":obj.uid}
				for var in cls.__annotations__:
					objd[var] = yamlify(getattr(obj,var))
				d[cls.__name__].append(objd)

		with open(self_db.file,"w") as f:
			yaml.dump(d,f)

		print("Database saved to disk.")


	def load(self_db):
		try:
			with open(self_db.file,"r") as f:
				self_db.loadarea = yaml.safe_load(f)
				# temporary storage until proper classes are defined
			print("Database loaded into memory.")
			self_db.inject()
		except:
			print("No existing database found.")




	def inject(self_db):
		classnames = [c for c in self_db.loadarea]

		# go through classes twice in case later classes enable references in earlier ones
		# twice is enough because we run this after every new class definition
		for clsname in classnames + list(reversed(classnames)):
			# check if class of this name exists
			classes = [c for c in self_db.class_to_objects if c.__name__ == clsname]
			if len(classes) > 0:
				cls = classes[0]

				for instance in self_db.loadarea[clsname]:


					for attr in cls.__annotations__:

						if hasattr(cls,attr) and isinstance(getattr(cls,attr),MultiRef) and all(isinstance(el,int) for el in instance[attr]):
							# convert uid to actual reference
							try:
								uids = instance[attr]
								instance[attr] = [self_db.get(uid) for uid in uids]
							except KeyError as exc:
								break
						elif hasattr(cls,attr) and isinstance(getattr(cls,attr),Ref) and isinstance(instance[attr],int):
							# convert uid to actual reference
							try:
								uid = instance[attr]
								instance[attr] = self_db.get(uid)
							except KeyError as exc:
								break
					else:
						# no break, so all references have been converted, we can use this object!
						uid = instance.pop("uid")
						cls(**instance,force_uid=uid)

						# delete from load area
						self_db.loadarea[clsname] = [i for i in self_db.loadarea[clsname] if i is not instance]






def yamlify(obj):
	if type(obj) in [str,int]: return obj
	if obj == [] or obj == {}: return obj

	try:
		return {k:yamlify(obj[k]) for k in obj}
	except:
		pass

	try:
		return [yamlify(e) for e in obj]
	except:
		pass

	return obj.uid
