# -*- coding: utf-8 -*-

"""
Ubi API Authentication, views and utilities:
1. Basic Authentication.
2. JSON Web Token Based Authentication.
"""

import jwt
import base64
from datetime import timedelta

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from ubiexceptions.generic import BasicAuthException, JWTAuthException
from config import ubiconf


def get_token(request):
    username, password = request.username, request.password  # make sure BasicAuthMixin is mixed-in to the view.
    current_dtm = now()
    payload = {
        'username': username,
        'password': password,
        'iat': current_dtm,
        'exp': current_dtm + timedelta(seconds=ubiconf.JWT_EXPIRY_TIME),
    }
    token = jwt.encode(payload, ubiconf.JWT_SECRET, algorithm=ubiconf.JWT_ALGORITHM)
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token


class BasicAuthMixin(View):
    """
    Add this mixin to the views where basic authentication is needed
    """

    www_basic_realm = 'ubi_basic_authentication'

    def basic_authenticate(self, request):
        use_auth = True
        auth = request.META.get('HTTP_AUTHORIZATION')
        if not auth or not auth.startswith('Basic'):
            # see if the credentials are passed as request's GET params
            username, password = request.GET.get('username') or None, request.GET.get('password') or None

            if username is None or password is None:
                raise BasicAuthException('Invalid Basic Authentication Body', 401)
            use_auth = False

        try:
            if use_auth:
                basic_auth_token = auth.split('Basic ')[1]
                decoded_token = base64.b64decode(basic_auth_token)
                if isinstance(decoded_token, bytes):
                    username, password = decoded_token.decode('utf-8').split(':')
                else:
                    username, password = decoded_token.split(':')
            if username == ubiconf.UBI_BASIC_AUTH['username'] and password == ubiconf.UBI_BASIC_AUTH['password']:
                return username, password
            raise BasicAuthException('Invalid Credentials', 403)
        except (ValueError, TypeError, IndexError):  # Error decoding the token using base64
            raise BasicAuthException('Token Can Not Be Decoded', 403)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        try:
            username, password = self.basic_authenticate(request)
            request.username, request.password = username, password  # we'll use this to create JSON Web Token.
        except BasicAuthException as err:
            response = JsonResponse({
                'status': err.status_code,
                'message': err.message
            }, status=err.status_code, content_type='application/json')
            if err.status_code == 401:  # As per W3 standards, the response must include WWW-Authenticate header.
                response['WWW-Authenticate'] = 'Basic realm="{0}"'.format(self.www_basic_realm)
            return response
        return super(BasicAuthMixin, self).dispatch(request, *args, **kwargs)


class JWTAuthMixin(View):
    """
    Add this mixin to the views where JWT based authentication is required.
    Token must be provided either in query_params or the request's Authorization Header:
    A. Query Param: the key should be passed as 'token'.
        For Example: ...&token=<jwt.based.token..>
    B. Request Authorization Header: Include the token in Auth Header.
        For Example: Authorization: Bearer <jwt.based.token..>
    """

    www_token_realm = 'ubi_jwt_authentication'

    def get_token(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION') or ''
        if not auth or not auth.startswith('Bearer'):
            # looks like there is no auth token in Auth Header. Try to get it from GET query param.
            return request.GET.get('token')
        return auth.split('Bearer ')[1]

    def jwt_authenticate(self, request):
        try:
            token = self.get_token(request)  # getting token either from request's Auth Header or GET query Parameter.
            if not token:
                raise JWTAuthException('No JSONWebToken Provided', 401)
            payload = jwt.decode(token, ubiconf.JWT_SECRET, algorithms=ubiconf.JWT_ALGORITHM)
            username, password = payload.get('username'), payload.get('password')
            if username == ubiconf.UBI_BASIC_AUTH['username'] and password == ubiconf.UBI_BASIC_AUTH['password']:
                return username, password
            raise JWTAuthException('Invalid JSONWebToken Credentials', 403)
        except IndexError:
            raise JWTAuthException('Empty JSONWebToken Provided', 403)
        except jwt.ExpiredSignature:
            raise JWTAuthException('JSONWebToken Session Has Expired', 403)
        except jwt.DecodeError:
            raise JWTAuthException('JSONWebToken Can Not BE Decoded', 401)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        try:
            request.username, request.password = self.jwt_authenticate(request)
        except JWTAuthException as err:
            response = JsonResponse({
                'status': err.status_code,
                'message': err.message
            }, status=err.status_code, content_type='application/json')
            if err.status_code == 401:  # As per W3 standards, the response must include WWW-Authenticate header.
                response['WWW-Authenticate'] = 'Bearer realm="{0}"'.format(self.www_token_realm)
            return response
        return super(JWTAuthMixin, self).dispatch(request, *args, **kwargs)


class GetJWT(BasicAuthMixin, View):
    """
    This view can be used to get the jwt token using username and password passed in post body or in query params.
    Example using requests module:
    res = requests.get('www.example.com/auth', auth=('<username>', '<password>'))
    """

    def get(self, request):
        token = get_token(request)
        return JsonResponse({'username': request.username, 'token': token}, status=200, content_type='application/json')

    def post(self, request):
        token = get_token(request)
        return JsonResponse({'username': request.username, 'token': token}, status=200, content_type='application/json')
        
