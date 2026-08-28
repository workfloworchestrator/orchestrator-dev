from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.types import SubscriptionLifecycle

from pydantic import computed_field


class FileBlockInactive(ProductBlockModel, product_block_name="File"):
    file_name: str | None = None
    contents: str | None = None


class FileBlockProvisioning(FileBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    file_name: str | None = None
    contents: str | None = None

    @computed_field  # type: ignore[misc]
    @property
    def title(self) -> str:
        return f"file {self.file_name}"


class FileBlock(FileBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    file_name: str | None = None
    contents: str | None = None
