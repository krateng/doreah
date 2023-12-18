from ._internal import DEFAULT, defaultarguments, DoreahConfig


import secrets
import bcrypt
import time
from nimrodel import EAPI
from threading import Lock
from bottle import response as bottleresponse
from bottle import request, HTTPResponse, redirect
from jinja2 import Environment, PackageLoader, select_autoescape

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import sqlalchemy as sql
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey


SESSION_EXPIRE = 3600000
TOKEN_LENGTH = 64
DEFAULT_USER = 'admin'
DEFAULT_PASSWORD = 'admin'


Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	uid = Column(Integer,primary_key=True)
	handle = Column(String)
	salt = Column(LargeBinary)
	hash = Column(String)
	sessions = relationship("Session",back_populates="user")

	def authenticate(self,password):
		if not password: return False
		password_bytes = password.encode('utf-8')
		hashed_password = bcrypt.hashpw(password_bytes, self.salt)
		return hashed_password == self.hash

	def set_password(self,password):
		if not password: return False
		password_bytes = password.encode('utf-8')
		salt = bcrypt.gensalt()
		hashed_password = bcrypt.hashpw(password_bytes, salt)
		self.salt = salt
		self.hash = hashed_password
		return True



class Session(Base):
	__tablename__ = 'sessions'
	uid = Column(Integer,primary_key=True)
	user_id = Column(Integer,ForeignKey('users.uid'))
	user = relationship("User",back_populates="sessions")
	session_token = Column(String)
	expire = Column(Integer)

	def __init__(self,user):
		self.user = user
		self.session_token = secrets.token_hex(TOKEN_LENGTH)
		self.expire = int(time.time()) + SESSION_EXPIRE

	def refresh(self):
		self.expire = int(time.time()) + SESSION_EXPIRE



class AuthManager:
	def __init__(self,cookieprefix="doreahauth",defaultpw=DEFAULT_PASSWORD,dbfile="auth.sqlite",stylesheets=(),singleuser=False):
		self.cookieprefix = cookieprefix
		self.dbfile = dbfile
		self.stylesheets = stylesheets
		self.singleuser = singleuser

		self.jinjaenv = Environment(
			loader=PackageLoader('doreah', 'resources/auth'),
			autoescape=select_autoescape(['html', 'xml'])
		)

		self.cookie_token_name = f"{self.cookieprefix}_sessiontoken"
		self.authapi = EAPI(path="auth",delay=True)

		self.engine = sql.create_engine(f"sqlite:///{self.dbfile}", echo = False)
		Base.metadata.create_all(self.engine)
		self.session = sessionmaker(bind=self.engine)

		if singleuser:
			with self.session() as sess:
				user = sess.query(User).where(User.handle == DEFAULT_USER).first() or self.create_user(handle=DEFAULT_USER,password=defaultpw)
			self.defaultuser = user

		self.authapi.post('authenticate')(self.get_token)

	def create_user(self,handle,password):
		with self.session() as sess:
			user = User(handle=handle)
			user.set_password(password)
			sess.add(user)
			sess.commit()
		return user

	def login(self,handle,password):
		with self.session() as sess:
			user = sess.query(User).where(User.handle==handle).first()
			if user.authenticate(password):
				usersession = Session(user=user)
				sess.add(usersession)
				sess.commit()
				return usersession.session_token

	def get_login_page(self):
		template = self.jinjaenv.get_template("login.html.jinja")
		return template.render({"lock_user":self.singleuser,"css":self.stylesheets})

	def get_token(self,user,password):
		if self.singleuser:
			user = DEFAULT_USER

		result = self.login(user,password)
		if result:
			bottleresponse.set_header("Set-Cookie",self.cookie_token_name + "=" + result)
			bottleresponse.status = 200
			return {
				'token': result,
				'cookie_name': self.cookie_token_name
			}
		else:
			bottleresponse.status = 403
			return {
				"error":"Access denied."
			}

	def check_session(self,token):
		with self.session() as sess:
			session = sess.query(Session).where(Session.session_token==token).first()
			if session:
				session.refresh()
				return session.user


	def check_request(self,request):
		token = request.get_cookie(self.cookie_token_name)
		if token is None: return False
		if user := self.check_session(token):
			return {'doreah_native_auth_check':True,'user':user}

		return False

		session.timestamp = time.time() + SESSION_EXPIRE
		return {'doreah_native_auth_check':True}

	def authenticated_function(self,alternate=(lambda x,y,z: False),api=False,pass_auth_result_as=None):
		"""Decorator to protect call of a function.

		:param function alternate: In addition to doreah's checking, also allow access if this function evaluates to truthy.
		:param boolean api: Whether this is an API function as opposed to a website
		:param string pass_auth_result_as: Keyword argument as which the auth result should be passed to the function."""

		def decorator(func):
			def newfunc(*args,**kwargs):
				auth_check = alternate(request,args,kwargs) or self.check_request(request)

				if auth_check:
					if pass_auth_result_as:
						return func(*args,**kwargs,**{pass_auth_result_as:auth_check})
					else:
						return func(*args,**kwargs)
				else:
					if api:
						bottleresponse.status = 403
						return {
							"status":"failure",
							"error":{
								'type':'authentication_fail',
								'desc':"Invalid or missing authentication"
							}
						}
					else:
						return self.get_login_page()

			newfunc.__annotations__ = func.__annotations__
			newfunc.__doc__ = func.__doc__
			return newfunc

		return decorator




