# Copyright 2019-2025 SURF, ESnet, GÉANT.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from orchestrator.core import OrchestratorCore
from orchestrator.core.settings import AppSettings
from oauth2_lib.settings import oauth2lib_settings
from oauth2_lib.fastapi import OIDCUserModel

import db  # noqa: F401  Side-effects: registers CustomerTable with ALL_DB_MODELS
import products  # noqa: F401  Side-effects
import workflows  # noqa: F401  Side-effects
from graphql_utils import CUSTOM_GRAPHQL_MODELS, custom_subscription_interface
from services.identity import MinimalAuthentication, MinimalAuthorization, MinimalGraphqlAuthorization

app = OrchestratorCore(base_settings=AppSettings())
app.register_graphql(
    subscription_interface=custom_subscription_interface,
    graphql_models=CUSTOM_GRAPHQL_MODELS,
)
app.register_authentication(MinimalAuthentication(
    openid_url=oauth2lib_settings.OIDC_BASE_URL,
    openid_config_url=oauth2lib_settings.OIDC_CONF_URL,
    resource_server_id=oauth2lib_settings.OAUTH2_RESOURCE_SERVER_ID,
    resource_server_secret=oauth2lib_settings.OAUTH2_RESOURCE_SERVER_SECRET,
    oidc_user_model_cls=OIDCUserModel,
))
app.register_authorization(MinimalAuthorization())
app.register_graphql_authorization(MinimalGraphqlAuthorization())
