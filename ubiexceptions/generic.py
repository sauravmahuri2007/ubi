"""
General exception classes
"""


class InsufficientPoints(Exception):
    """
    This can be raised when there is insufficent points to buy an item
    """
    def __init__(self, *args, **kwargs):
        self.message = args and args[0] or kwargs.get('message') or 'Insufficient Point'
        try:
            self.extra_points = args and args[1] or kwargs.get('extra_points')
        except IndexError:
            self.extra_points = kwargs['extra_points']
        super(self.__class__, self).__init__(*args, **kwargs)

    def __str__(self):
        return '<%s - %s>' % (self.message, self.extra_points)


class CanNotBePurchased(Exception):
    """
    This can be raised when user selects an item which can not be purchased
    """
    def __init__(self, *args, **kwargs):
        self.message = args and args[0] or kwargs.get('message') or 'Not eligible to purchase'
        super(self.__class__, self).__init__(*args, **kwargs)

    def __str__(self):
        return '<%s>' % self.message


class BasicAuthException(Exception):

    def __init__(self, *details):
        self.message = details and details[0] or 'Basic Authentication Failed!'
        try:
            self.status_code = details and details[1] or 401
        except IndexError:
            self.status_code = 401

    def __str__(self):
        return '< %s - %s >' % (self.status_code, self.message)


class JWTAuthException(Exception):

    def __init__(self, *details):
        self.message = details and details[0] or 'JWT Based Authentication Failed!'
        try:
            self.status_code = details and details[1] or 401
        except IndexError:
            self.status_code = 401

    def __str__(self):
        return '< %s - %s >' % (self.status_code, self.message)