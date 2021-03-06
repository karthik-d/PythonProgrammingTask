"""
Authorization decorators to enforce authorization
on request on demand by resouces
"""

from functools import wraps
import types
from flask import request

from todoapp.core.utils.auth import AUTH_TOKEN_FIELD, validate_token
from .custom_fields import Scope

from .exception import (
	TokenRequiredException, 
	InvalidTokenException,
	ActionForbiddenException
)


class RequestAuth:
	"""
	Class to memoize the the token and its scope
	by reading from the DB.
	Instantiated as and instance variable of 
	the Resource-Classes decorated by @require_token
	Makes the scope accessible to the 
	decorators of Resource methods.
	Helps to catch Token absence exceptions early
	"""

	def __init__(self, *args, **kwargs):
		super(RequestAuth, self).__init__()
		self.token_dict = None
		self.set_token_dict()

	def set_token_dict(self):
		"""
		Memoize the dictionary containing the request token
		and its scope (and id).
		If multiple tokens are supplied, stores the token with
		highest access scope
		Throws error if request doesn't contain a valid token
		"""

		if self.token_dict is None:
			print(request.headers)
			print(request.data)
			print(request.values)
			print(request.json)
			tokens_supplied = request.headers.get(AUTH_TOKEN_FIELD, None)
			if tokens_supplied is None:
				raise TokenRequiredException
			tokens_supplied = tokens_supplied.split(',')
			best_scope = -1
			best_token_d = None
			for token_in in tokens_supplied:
				token_d = validate_token(token_in)
				if token_d is None:
					raise InvalidTokenException
				if token_d.get('scope') > best_scope:
					best_scope = token_d.get('scope')
					best_token_d = token_d
			self.token_dict = best_token_d

	def get_scope(self):
		return self.token_dict.get('scope')


def require_token(ResourceClass):
	"""
	Decorator function to create a wrapper around
	Resource-Classes that checks for
	a valid api-token in the request-header
	Raises error otherwise if not found
	Else, an instance of RequestAuth to the 
	Resource-Class
	"""
	base_ctor = ResourceClass.__init__
	def mod_ctor(self, *args, **kwargs):
		base_ctor(self, *args, **kwargs)
		self.request_auth = RequestAuth()
	ResourceClass.__init__ = mod_ctor	
	return ResourceClass


def require_accesslevel(reqd_scope):
	"""
	Decorator function to wrap around Rosource methods
	that checks themir access requirements against 
	the scope of the request token.
	+ scope: MINIMUM required access-level (0, 1, 2)
	"""
	
	def decorator(resource_handler):
		def make_error_msg():
			if reqd_scope == 1:
				msg = "Action requires Read-Write scope"
			elif reqd_scope == 2:
				msg = "Action requires Admin scope"
			return msg

		# Make self explicit to expose the object
		# Pass it back to the method
		@wraps(resource_handler)
		def wrapper(self, *args, **kwargs):
			if not hasattr(self, 'request_auth'):
				# If token_meta is not part of the class yet.
				# create an instance variable
				self.request_auth = RequestAuth()
			scope = self.request_auth.get_scope()
			if scope<reqd_scope :
				raise ActionForbiddenException(make_error_msg())
			return resource_handler(self, *args, **kwargs)

		return wrapper
	return decorator

