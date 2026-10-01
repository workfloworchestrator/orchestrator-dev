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

_JWK_CLIENT: jwt.PyJWKClient | None = None

def get_jwk_client() -> jwt.PyJWKClient:
    global _JWK_CLIENT
    if _JWK_CLIENT is None:
        _JWK_CLIENT = jwt.PyJWKClient(settings.OAUTH2_CERT_URL, cache_keys=True)
    return _JWK_CLIENT

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
        # Add any authorization logic for the REST API (not workflows) here
        return True

class MinimalGraphqlAuthorization(GraphqlAuthorization):
    async def authorize(self, request: HTTPConnection, method: str, user: OIDCUserModel) -> bool | None:
        # Add any authorization logic for the GraphQL API (not workflows) here
        return True

class MinimalAuthentication(OIDCAuth):
    async def userinfo(self, async_request: AsyncClient, token: str) -> OIDCUserModel:
        user_model = None

        try:
            # Normally, you would want to include OAUTH2_ISSUER to verify the iss parameter (RFC 9207)
            # https://www.rfc-editor.org/rfc/rfc9207.html
            # However, HTTPS isn't currently active on the dev keycloak instance.
            # OAUTH2_ISSUER: str = "https://keycloak:8085/auth/realms/orchestrator"
            jwk_client = get_jwk_client()

            signing_key = jwk_client.get_signing_key_from_jwt(token)

            decoded_token = jwt.decode(
                token,
                signing_key.key,
                algorithms=settings.OAUTH2_SIGNING_ALGORITHMS,
                #issuer=OAUTH2_ISSUER, # See above
                options={"verify_aud": True},
            )

            user_model = MinimalUserInfoModel(**decoded_token)
        except ExpiredSignatureError:
            message = "Unable to decode token, token has expired"
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=message)
        except Exception as e:
            message = "Unable to decode token"
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=message)

        return user_model
