name = "doreah"
desc = "Small toolkit of utilities for python projects"

version = 1,6,5
versionstr = ".".join(str(n) for n in version)

author = {
	"name": "Johannes Krattenmacher",
	"email": "python@krateng.dev",
	"github": "krateng"
}

requires = [
	"lxml",
	"mechanicalsoup",
	"requests",
	"pyyaml",
	"beautifulsoup4"
]
resources = [
	'res/login.pyhp'
]

commands = {
	"pyhpserver":"pyhp2:run_testserver"
}
