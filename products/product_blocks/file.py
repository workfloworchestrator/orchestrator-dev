# Copyright 2019-2026 SURF, GEANT, ESnet.
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
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle

from pydantic import computed_field


class FileBlockInactive(ProductBlockModel, product_block_name="File"):
    file_name: str | None = None
    contents: str | None = None


class FileBlockProvisioning(FileBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    file_name: str
    contents: str

    @computed_field  # type: ignore[misc]
    @property
    def title(self) -> str:
        return f"file {self.file_name}"


class FileBlock(FileBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    file_name: str
    contents: str
