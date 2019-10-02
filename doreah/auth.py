from ._internal import DEFAULT, defaultarguments, DoreahConfig
from .database import Database, Ref
from .pyhp import file as pyhpfile

import secrets
import time
from nimrodel import EAPI
from threading import Lock
from bottle import response as bottleresponse
from bottle import request, HTTPResponse, redirect
import pkg_resources

config = DoreahConfig("auth",
	multiuser=True,
	cookieprefix="doreahauth"
)


db = Database(file="authdb.ddb")
cookie_token_name = config["cookieprefix"] + "_sessiontoken"
authapi = EAPI(path="auth",delay=True)

CHALLENGE_BITS = 32
TOKEN_BITS = 32


COMMON = 3590390094909444
GENERATOR = 2
MODULO = """
	FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1
	29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD
	EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245
	E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED
	EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D
	C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F
	83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D
	670C354E 4ABC9804 F1746C08 CA18217C 32905E46 2E36CE3B
	E39E772C 180E8603 9B2783A2 EC07A28F B5C55DF0 6F4C52C9
	DE2BCBF6 95581718 3995497C EA956AE5 15D22618 98FA0510
	15728E5A 8AACAA68 FFFFFFFF FFFFFFFF
"""


CYCLE_CHALLENGE = 120
SESSION_EXPIRE = 360000

### DERIVED

COMMON = hex(COMMON)
MODULO = int(MODULO.replace(" ","").replace("\n","").replace("\t",""),16)


challenge_current = None
challenge_old = None
stop_issue = 0
expire = 0
lock = Lock()
updatelock = Lock()







def combine(a,b):
	a = int(a,16)
	b = int(b,16)
	#return (a ** b) % P
	result = pow(a,b,MODULO)
	return hex(result)[2:]


class User(db.DBObject):
	__primary__ = "username",
	username: str
	pubkey: str


	def setpw(self,password):
		pw = str.encode(password).hex()
		pw1 = combine(hex(GENERATOR),pw)
		pub = combine(pw1,COMMON)
		self.pubkey = pub
		db.save()

	def validate_challenge(self,challenge,response):
		update()
		lock.acquire()
		if challenge not in [challenge_current, challenge_old]:
			lock.release()
			print("Invalid challenge")
			return False

		pub = str(self.pubkey)

		if combine(pub,challenge) == combine(response,COMMON):
			# invalidate challenges
			stop_issue = 0
			expire = 0
			update()

			lock.release()
			return True

		else:
			print("Invalid response")
			lock.release()
			return False

if not config["multiuser"]:
	defaultuser = User(username="")


sessions = {} #token -> timestamp expire
class Session(db.DBObject):
	token: str
	timestamp: float
	user: User = Ref(User,exclusive=False)



def update():
	updatelock.acquire()
	global challenge_current, stop_issue, expire
	now = time.time()
	if now > expire:
		challenge_old = None
		challenge_current = generate_challenge()
		stop_issue = now + CYCLE_CHALLENGE
		expire = stop_issue + CYCLE_CHALLENGE
	elif now > stop_issue:
		challenge_old = challenge_current
		challenge_current = generate_challenge()
		stop_issue = expire #expire value of old challenge is stop issue value of new
		expire = stop_issue + CYCLE_CHALLENGE
	updatelock.release()
	db.save()

def generate_challenge():
	return secrets.token_hex(CHALLENGE_BITS)

def generate_token():
	return secrets.token_hex(TOKEN_BITS)

@authapi.get("challenge")
def get_challenge():
	global challenge_current, stop_issue, expire
	update()
	return {"challenge":challenge_current, "modulo":MODULO,"generator":GENERATOR}


@authapi.post("authenticate")
def get_token(user,challenge,response):
	if not config["multiuser"]:
		u = defaultuser
	else:
		u = db.getby(User,username=user)
	if u.validate_challenge(challenge,response):
		token = generate_token()
		#sessions[token] = time.time() + SESSION_EXPIRE
		Session(token=token,timestamp=time.time() + SESSION_EXPIRE,user=u)
		bottleresponse.set_header("Set-Cookie",cookie_token_name + "=" + token)# + "; HttpOnly")
		db.save()
		return {"token":token,"cookie_name":cookie_token_name}
	else:
		return {"error":"Access denied."}


def check(request):
	token = request.get_cookie(cookie_token_name)
	if token is None: return False
	for ses in db.getall(Session):
		if ses.token == token:
			session = ses
			break
	else:
		return False
	if session.timestamp < time.time(): return False

	session.timestamp = time.time() + SESSION_EXPIRE
	return True

def authenticated(func):

	def newfunc(*args,**kwargs):
		if check(request):
			return func(*args,**kwargs)
		else:
			redirect("/")

	return newfunc


def get_login_page(stylesheets=[]):
	return pyhpfile(pkg_resources.resource_filename(__name__,"res/login.pyhp"),{"get_challenge":get_challenge,"css":stylesheets})


db.save()
