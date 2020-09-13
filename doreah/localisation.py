from ._internal import DEFAULT, defaultarguments, DoreahConfig

import os
import yaml

config = DoreahConfig("localisation",
	folder="localisation",
	default="en_GB"
)


locs = {}

for f in os.listdir(config["folder"]):
	if f.endswith(".yml"):
		with open (os.path.join(config["folder"],f)) as locfile:
			data = yaml.safe_load(locfile)
			locs[f.split(".")[0]] = data

print(locs)

localize = {
	lang:lambda x,lang=lang:_localize(x,lang) for lang in locs
}

def _localize(key,lang):
	if key in locs[lang]["strings"]:
		return locs[lang]["strings"][key]
	elif "inherit" in locs[lang]:
		return _localize(key,locs[lang]["inherit"])
	else:
		return locs[config["default"]]

class Newstr(str):
	def localize(self,lang,**keys):
		return _localize(str,lang).format(**keys)

__builtins__.__dict__["str"] = Newstr
