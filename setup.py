import setuptools
import importlib

packagename = "doreah"

module = importlib.import_module(packagename)
pkginfo = importlib.import_module(".__pkginfo__",package=packagename)

try:
	ghname = pkginfo.links["github"]
except:
	ghname = pkginfo.name

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=pkginfo.name,
    version=".".join(str(n) for n in pkginfo.version),
    author=pkginfo.author["name"],
    author_email=pkginfo.author["email"],
    description=pkginfo.desc,
	license="GPLv3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/" + pkginfo.author["github"] + "/" + ghname,
    packages=[packagename],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
	python_requires=">=3.5",
	install_requires=pkginfo.requires,
	package_data={'': pkginfo.resources},
	include_package_data=True,
	entry_points = {
		"console_scripts":[
			cmd + " = " + pkginfo.name + "." + pkginfo.commands[cmd]
			for cmd in pkginfo.commands
		]
	}
)


import os
os.system("git tag v" + ".".join(str(n) for n in pkginfo.version))
