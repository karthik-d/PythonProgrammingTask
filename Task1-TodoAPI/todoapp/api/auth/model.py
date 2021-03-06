from flask_restplus import fields

from .namespace import auth_nspace
from .custom_fields import Scope


TOKEN = auth_nspace.model('Token',
	{
		'id': fields.Integer(
			readonly=True,
			description='A unique identifier for the token (Auto-Generated)',
			attribute='id'
			),
		'token': fields.String(
			required=True, 
			description='A unique 36-character string',
			attribute='token'
			),
		'scope': Scope(
			required=True,
			description='Integer (0, 1, or 2) for (read-only, read-write, admin)',
			attribute='scope'
			),
		'URI': fields.Url('api.auth-token', absolute=True)
	}
)

EXCEPTION = auth_nspace.model('TokenException',
	{
		'HTTP_status': fields.Integer(
			description='The HTTP status code for the response',
			attribute='http_code'
		),
		'message': fields.String(
			description='Description of the error/exception',
			attribute='message'
		)
	}
)

AUTH_EXCEPTION = auth_nspace.model('AuthorizationException',
	{
		'HTTP_status': fields.Integer(
			description='The HTTP status code for the response',
			attribute='http_code'
		),
		'message': fields.String(
			description='Description of the error/exception',
			attribute='message'
		),
		'Token_Header_Field': fields.String(
			description='Header field-name to supply the token',
			attribute='token_field'
		),
		'Token_Generation_URL': fields.String(
			description='URL to generate API tokens',
			attribute='token_gen_url'
		)
	})