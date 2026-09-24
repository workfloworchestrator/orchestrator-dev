
from orchestrator.core.domain.base import SubscriptionModel
from orchestrator.core.types import SubscriptionLifecycle

from products.product_blocks.file import FileBlock, FileBlockInactive, FileBlockProvisioning

class FileInactive(SubscriptionModel, is_base=True):
    file: FileBlockInactive


class FileProvisioning(FileInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    file: FileBlockProvisioning


class File(FileProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    file: FileBlock
