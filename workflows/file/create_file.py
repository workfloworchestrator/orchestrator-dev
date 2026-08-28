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


import uuid
import json
import os
from random import randrange

from orchestrator.core.services.products import get_product_by_id
from orchestrator.core.targets import Target
from orchestrator.core.types import SubscriptionLifecycle
from orchestrator.core.workflow import StepList, begin, step
from orchestrator.core.workflows.steps import store_process_subscription
from orchestrator.core.workflows.utils import create_workflow
from pydantic import ConfigDict
from pydantic_forms.core import FormPage
from pydantic_forms.types import FormGenerator, State, UUIDstr

from products.product_types.file import FileInactive, FileProvisioning
from products.services.description import description
from workflows.shared import create_summary_form

FILE_DIR = "/home/orchestrator/minimal-files"

#TODO I probably need to handle UUID differently
def initial_input_form_generator(product_name: str, product: UUIDstr) -> FormGenerator:
    class CreateFileForm(FormPage):
        model_config = ConfigDict(title=product_name)

        file_name: str | None
        contents: str | None

    user_input = yield CreateFileForm
    user_input_dict = user_input.model_dump()

    summary_fields = ["file_name", "contents"]
    yield from create_summary_form(user_input_dict, product_name, summary_fields)

    return user_input_dict


@step("Construct Subscription model")
def construct_file_model(
    product: UUIDstr,
    file_name: str | None,
    contents: str | None,
) -> State:
    subscription = FileInactive.from_product_id(
        product_id=product,
        customer_id=str(uuid.uuid4()),
        status=SubscriptionLifecycle.INITIAL,
    )

    subscription.file.file_name = file_name
    subscription.file.contents = contents

    subscription = FileProvisioning.from_other_lifecycle(subscription, SubscriptionLifecycle.PROVISIONING)
    #????
    subscription.description = description(subscription)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,  # necessary to be able to use older generic step functions
        "subscription_description": subscription.description,
    }

@step("Ensure directory exists")
def ensure_directory_exists() -> State:
    os.makedirs(FILE_DIR, exist_ok=True)
    return {}

@step("Create file on disk")
def create_file_on_disk(subscription: FileProvisioning, file_name: str, contents: str) -> State:
    #TODO rewrite model and migration to make this non-optional
    if file_name is None:
        raise ValueError("Rewrite this")

    p = os.path.join(FILE_DIR, file_name)
    with open(p, "w") as f:
        f.write(contents)
    return {"subscription": subscription, "file_path": p}


@create_workflow("Create file", initial_input_form=initial_input_form_generator)
def create_file() -> StepList:
    return (
        begin
        >> construct_file_model
        >> ensure_directory_exists
        >> create_file_on_disk
    )
