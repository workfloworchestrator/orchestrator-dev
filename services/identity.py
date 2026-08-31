#TODO move
from http import HTTPStatus

import jwt
import structlog
from starlette.requests import HTTPConnection
from httpx import AsyncClient
from oauth2_lib.fastapi import Authorization, GraphqlAuthorization, OIDCAuth, OIDCUserModel, RequestPath
from fastapi import HTTPException
from jwt.exceptions import ExpiredSignatureError

from settings import settings

logger = structlog.get_logger(__name__)

class MinimalUserInfoModel(OIDCUserModel):
    # Add any extra claims here
    REGISTERED_CLAIMS = OIDCUserModel.REGISTERED_CLAIMS + []

    @property
    def name(self):
        """Defer to our user_name implementation.

        resolve_user_name in orch-core now does this:
        if resolved_user:
            return resolved_user.name if resolved_user.name else resolved_user.user_name
        """
        return self.user_name

    @property
    def user_name(self):
        return self.preferred_username

class MinimalAuthorization(Authorization):
    async def authorize(self, request: HTTPConnection, user: OIDCUserModel) -> bool | None:
        #TODO should this take an AuthContext, or is that only workflow/step decorators???
        return True

class MinimalGraphqlAuthorization(GraphqlAuthorization):
    async def authorize(self, request: HTTPConnection, method: str, user: OIDCUserModel) -> bool | None:
        #TODO should this take an AuthContext, or is that only workflow/step decorators???
        return True

class MinimalAuthentication(OIDCAuth):
    #TODO this probably needs to use the updated interface instead of OIDCUserModel...
    async def userinfo(self, async_request: AsyncClient, token: str) -> OIDCUserModel:
        user_model = None

        try:
            #TODO perhaps no /auth/?
            #OAUTH2_ISSUER: str = "https://127.0.01:8085/auth/realms/esnetldap"
            #TODO what's this do?
            #OAUTH2_JWT_OPTIONS: dict = {"verify_aud": False}
            #TODO only initialize this once per class, or initialize elsewhere
            jwk_client = jwt.PyJWKClient(settings.OAUTH2_CERT_URL, cache_keys=True)

            signing_key = jwk_client.get_signing_key_from_jwt(token)

            decoded_token = jwt.decode(
                token,
                signing_key.key,
                algorithms=settings.OAUTH2_SIGNING_ALGORITHMS,
                #TODO should we add anything here?
                #issuer=OAUTH2_ISSUER,
                #options=OAUTH2_JWT_OPTIONS,
            )

            user_model = MinimalUserInfoModel(**decoded_token)
        except ExpiredSignatureError:
            message = "Unable to decode token, token has expired"
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=message)
        except Exception as e:
            message = "Unable to decode token"
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=message)

        return user_model
