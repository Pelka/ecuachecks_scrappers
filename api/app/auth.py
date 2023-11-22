from typing import Optional
from robyn import AuthenticationHandler, Request
from robyn.robyn import Identity


class BasicAuthHandler(AuthenticationHandler):
    def authenticate(self, request: Request) -> Optional[Identity]:
        token = self.token_getter.get_token(request)
        if token == "valid":
            return Identity(claims={})
        return None
