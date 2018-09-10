class InvalidTokenError(Exception):
    pass

class TokenCompromisedError(Exception):
    pass

class RevokedTokenError(Exception):
    pass

class AccessTokenNotExpiredError(Exception):
    pass