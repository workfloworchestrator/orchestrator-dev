# Copyright 2019-2023 SURF.
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
import operator
from collections.abc import Iterator
from pprint import pformat
from typing import Annotated, Generator, List, TypeAlias, cast
from uuid import UUID

import structlog
from annotated_types import Ge, Le, doc
from deepdiff import DeepDiff
from orchestrator.core.db import (
    ProductTable,
    ResourceTypeTable,
    SubscriptionInstanceRelationTable,
    SubscriptionInstanceTable,
    SubscriptionInstanceValueTable,
    SubscriptionTable,
    db,
)
from orchestrator.core.domain import SubscriptionModel
from orchestrator.core.domain.base import ProductBlockModel
from orchestrator.core.forms import FormPage
from orchestrator.core.services import subscriptions
from orchestrator.core.types import SubscriptionLifecycle
from pydantic import ConfigDict
from pydantic_core.core_schema import ValidationInfo
from sqlalchemy import select
from sqlalchemy.orm import aliased

from db.models import CustomerTable
from pydantic_forms.types import State, SummaryData, UUIDstr
from pydantic_forms.validators import Choice, MigrationSummary, migration_summary

logger = structlog.get_logger(__name__)

Vlan = Annotated[int, Ge(2), Le(4094), doc("VLAN ID.")]

AllowedNumberOfL2vpnPorts = Annotated[int, Ge(2), Le(8), doc("Allowed number of L2vpn ports.")]


def subscriptions_by_product_type(product_type: str, status: List[SubscriptionLifecycle]) -> List[SubscriptionTable]:
    """
    retrieve_subscription_list_by_product This function lets you retreive a
    list of all subscriptions of a given product type. For example, you could
    call this like so:

    >>> subscriptions_by_product_type("Node", [SubscriptionLifecycle.ACTIVE, SubscriptionLifecycle.PROVISIONING])
    [SubscriptionTable(su...note=None), SubscriptionTable(su...note=None)]

    You now have a list of all active Node subscription instances and can then
    use them in your workflow.

    Args:
        product_type (str): The prouduct type in the DB (i.e. Node, User, etc.)
        status (List[SubscriptionLifecycle]): The lifecycle states you want returned (i.e.
        SubscriptionLifecycle.ACTIVE)

    Returns:
        List[SubscriptionTable]: A list of all the subscriptions that match
        your criteria.
    """
    subscriptions = (
        SubscriptionTable.query.join(ProductTable)
        .filter(ProductTable.product_type == product_type)
        .filter(SubscriptionTable.status.in_(status))
        .all()
    )
    return subscriptions


def subscriptions_by_product_type_and_instance_value(
    product_type: str, resource_type: str, value: str, status: List[SubscriptionLifecycle]
) -> List[SubscriptionTable]:
    """Retrieve a list of Subscriptions by product_type, resource_type and value.

    Args:
        product_type: type of subscriptions
        resource_type: name of the resource type
        value: value of the resource type
        status: lifecycle status of the subscriptions

    Returns: Subscription or None

    """
    return (
        SubscriptionTable.query.join(ProductTable)
        .join(SubscriptionInstanceTable)
        .join(SubscriptionInstanceValueTable)
        .join(ResourceTypeTable)
        .filter(ProductTable.product_type == product_type)
        .filter(SubscriptionInstanceValueTable.value == value)
        .filter(ResourceTypeTable.resource_type == resource_type)
        .filter(SubscriptionTable.status.in_(status))
        .all()
    )


def node_selector(enum: str = "NodesEnum") -> type[Choice]:
    node_subscriptions = subscriptions_by_product_type("Node", [SubscriptionLifecycle.ACTIVE])
    nodes = {
        str(subscription.subscription_id): subscription.description
        for subscription in sorted(node_subscriptions, key=lambda node: node.description)
    }
    return Choice(enum, zip(nodes.keys(), nodes.items()))  # type:ignore


def summary_form(product_name: str, summary_data: SummaryData) -> Generator:
    ProductSummary: TypeAlias = cast(type[MigrationSummary], migration_summary(summary_data))

    class SummaryForm(FormPage):
        model_config = ConfigDict(title=f"{product_name} summary")

        product_summary: ProductSummary

    yield SummaryForm


def create_summary_form(user_input: dict, product_name: str, fields: List[str]) -> Generator:
    columns = [[str(user_input[nm]) for nm in fields]]
    yield from summary_form(product_name, SummaryData(labels=fields, columns=columns))  # type: ignore


def modify_summary_form(user_input: dict, block: ProductBlockModel, fields: List[str]) -> Generator:
    before = [str(getattr(block, nm)) for nm in fields]  # type: ignore[attr-defined]
    after = [str(user_input[nm]) for nm in fields]
    yield from summary_form(
        block.subscription.product.name if block.subscription else "No Product Name Found",
        SummaryData(labels=fields, headers=["Before", "After"], columns=[before, after]),
    )


def pretty_print_deepdiff(diff: DeepDiff) -> str:
    return pformat(diff.to_dict(), indent=2, compact=False)


def _get_subscription_ids_from_info(info: ValidationInfo, port_field_name: str) -> list[str] | None:
    match info.data.get(port_field_name):
        case list() | tuple() | set() as iterable:
            return list(iterable)
        case str() as scalar:
            return [scalar]
        case None:
            return None
        case _ as invalid:
            raise ValueError(f"Cannot convert value {invalid} in field {port_field_name} to list of subscription ids")


def _get_subscription(subscription_id: UUID | UUIDstr) -> SubscriptionTable:
    return db.session.scalar(select(SubscriptionTable).where(SubscriptionTable.subscription_id == subscription_id))


def customer_selector() -> type[Choice]:
    stmt = select(CustomerTable.customer_id, CustomerTable.fullname).order_by(CustomerTable.fullname)
    rows = db.session.execute(stmt).all()
    customers = {str(row.customer_id): row.fullname for row in rows}
    return Choice("CustomersEnum", zip(customers.keys(), customers.items()))  # type: ignore
