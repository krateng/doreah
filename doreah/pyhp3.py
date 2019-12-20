from bs4 import BeautifulSoup
from copy import deepcopy
import re
import os
import hashlib
import copy

from ._internal import DEFAULT, defaultarguments, DoreahConfig


config = DoreahConfig("pyhp",
	interpret=str,
	precompile=True
)



precompiled = {}

@defaultarguments(config,interpret="interpret",precompile="precompile")
def file(path,d={},interpret=DEFAULT,noroot=False,precompile=DEFAULT):
	"""Parses a pyhp source file and returns the generated html code.

	:param string path: Location of the pyhp source file
	:param dict d: Variables dictionary
	:param function interpret: Function that determines string representations of variables
	:param bool precompile: Whether compiled pyhp pages should be cached in memory for faster page generation
	:return: HTML source
	"""

	filepath = os.path.abspath(path)
	directory = os.path.dirname(filepath)

	with open(path,"r") as f:
		content = f.read()

	if precompile:

		h = hashlib.md5()
		h.update(content.encode())
		check = h.digest()
		if filepath in precompiled and precompiled[filepath]["checksum"] == check:
			pass
		else:
			precompiled[filepath] = {"object":BeautifulSoup(content,"html.parser"),"checksum":check}
		content = copy.copy(precompiled[filepath]["object"])



	return parse(content,d,interpret=interpret,directory=directory,noroot=noroot)


def _file(path,d,interpret=DEFAULT,noroot=False):

	with open(path,"r") as f:
		content = f.read()

	directory = os.path.dirname(os.path.abspath(path))

	return _parse(content,d,interpret=interpret,directory=directory,noroot=noroot)


@defaultarguments(config,interpret="interpret")
def parse(src,d={},interpret=DEFAULT,directory=None,noroot=False):
	"""Parses pyhp source and returns the generated html code.

	:param string src: Source string
	:param dict d: Variables dictionary
	:param function interpret: Function that determines string representations of variables
	:return: HTML source
	"""

	doc = _parse(src,d,interpret=interpret,directory=directory,noroot=noroot)


	#raw = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
	#raw = etree.tostring(doc,encoding="unicode",method="html").replace("&gt;",">").replace("&lt;","<")
	return doc.decode()

# to tree
def _parse(src,d,interpret=DEFAULT,directory=None,noroot=False):


	if isinstance(src,str):
		doc = BeautifulSoup(src,"html.parser")
	elif isinstance(src,BeautifulSoup):
		doc = src
	else:
		raise Exception
	doc = _parse_node(doc,d,interpret,directory=directory)[0]
	#result = list(doc.children)

	if noroot:
		return list(doc.children)
	else:
		return doc




from inspect import signature as sig
from inspect import Parameter
from types import FunctionType as newfunc

pyhpnodes = {}

#decorator for nodes
def pyhpnode(name):
	def decorator(func):
		params = sig(func).parameters
		pyhpnodes[name] = (
			func.__code__, #code
			params, #all parameters
			[p for p in params if params[p].default is Parameter.empty], #required parameters
			{k:params[k].default for k in params if params[k].default is not Parameter.empty} # optionals with defaults
		)
	return decorator

def run_pyhpnode(code,node,d,params,defaults,directory,interpret):
	globs = {
		"children":node.children, #directly expose subnodes
		"node":node,
		"environment":d, # the dict
		"directory":directory,
		"interpret":interpret,
		# builtins like print
		**__builtins__,
		# necessary imports
		"os":os,
		"_file":file
	}
	func = newfunc(code,globs)
	return func(**{p + "_":params[p] for p in params},**defaults)

from . import _pyhp_nodes

print(pyhpnodes)


def _parse_node(node,d,interpret,directory=None):

	if isinstance(node,str): return [node]


	## parse pyhp nodes

	if node.name == "pyhp":
		nodeattributes = [a + "_" for a in node.attrs]
		print("This node has attributes",nodeattributes)
		for nodetype in pyhpnodes:
			(code,params,required,optional) = pyhpnodes[nodetype]
			if all(r in nodeattributes for r in required) and all(r in params for r in nodeattributes):
				print(nodetype,"has a valid signature!")
				return run_pyhpnode(code,node,d,node.attrs,optional,directory,interpret)

			else:
				print("Node has signature",nodeattributes,"but " + nodetype + " requires",params)


	## parse normal nodes

	else:

		## replace attributes (not necessary in pyhp nodes)

		if hasattr(node,"attrs"):
			for name,value in node.attrs.items():
				if isinstance(value,list): value = " ".join(value)
				vars = re.findall("{.*?}",value)
				for v in vars:
					vname = v[1:-1]
					try:
						value = value.replace(v,interpret(eval(vname,d)))
					except:
						pass
						print("Error parsing:",v,"in attribute")

				node.attrs[name] = value



		subnodes = [n for n in node]
		newsubnodes = []
		for subnode in subnodes:
			sn = subnode.extract()
			newsubnodes += _parse_node(sn,d,interpret,directory=directory)

		for nsn in newsubnodes:
			node.append(nsn)


		return [node]



def _attr(node,name):
	res = node.get(name)
	try:
		return res.replace(" gr "," > ").replace(" ls "," < ")
	except:
		return res





### run test server

from .control import mainfunction

@mainfunction({"p":"port","h":"host"},shield=True)
def run_testserver(port=1337,host="::"):
	from bottle import get, run, static_file
	from doreah.pyhp import file
	import os

	@get("/<path:path>")
	def serve_file(path):

		if os.path.exists(path + ".pyhp"):
			return file(path + ".pyhp")
		if os.path.exists(path):
			return static_file(path,root="")
		if os.path.exists(path + ".html"):
			return static_file(path + ".html",root="")

		return static_file(path,root="") # will produce proper error


	run(host=host,port=port)
