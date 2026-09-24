"""add file.

Revision ID: aaaee1f71ea9
Revises: a77227fe5455
Create Date: 2026-08-27 22:36:39.469749

"""
import sqlalchemy as sa
from alembic import op

from orchestrator.core.migrations.helpers import create_workflow, delete_workflow

# revision identifiers, used by Alembic.
revision = 'aaaee1f71ea9'
down_revision = '610caa9e4286'
branch_labels = None
depends_on = None

new_workflows = [
    {
        "name": "create_file",
        "target": "CREATE",
        "description": "Create file",
        "product_type": "File"
    }
]

def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
INSERT INTO products (name, description, product_type, tag, status) VALUES ('file', 'We manage a file on disk for you', 'File', 'file', 'active') RETURNING products.product_id
    """))
    conn.execute(sa.text("""
INSERT INTO product_blocks (name, description, tag, status) VALUES ('File', 'A managed file', 'file', 'active') RETURNING product_blocks.product_block_id
    """))
    conn.execute(sa.text("""
INSERT INTO resource_types (resource_type, description) VALUES ('file_name', 'name of file on disk') RETURNING resource_types.resource_type_id
    """))
    conn.execute(sa.text("""
INSERT INTO resource_types (resource_type, description) VALUES ('contents', 'contents of file on disk') RETURNING resource_types.resource_type_id
    """))
    conn.execute(sa.text("""
INSERT INTO product_product_blocks (product_id, product_block_id) VALUES ((SELECT products.product_id FROM products WHERE products.name IN ('file')), (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('File')))
    """))
    conn.execute(sa.text("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('File')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('file_name')))
    """))
    conn.execute(sa.text("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('File')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('contents')))
    """))
    # Add workflows
    for workflow in new_workflows:
        create_workflow(conn, workflow)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('File')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('file_name'))
    """))
    conn.execute(sa.text("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('File'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('file_name'))
    """))
    conn.execute(sa.text("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('File')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('contents'))
    """))
    conn.execute(sa.text("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('File'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('contents'))
    """))
    conn.execute(sa.text("""
DELETE FROM subscription_instance_values WHERE subscription_instance_values.resource_type_id IN (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('file_name', 'contents'))
    """))
    conn.execute(sa.text("""
DELETE FROM resource_types WHERE resource_types.resource_type IN ('file_name', 'contents')
    """))
    conn.execute(sa.text("""
DELETE FROM product_product_blocks WHERE product_product_blocks.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('file')) AND product_product_blocks.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('File'))
    """))
    conn.execute(sa.text("""
DELETE FROM subscription_instances WHERE subscription_instances.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('File'))
    """))
    conn.execute(sa.text("""
DELETE FROM product_blocks WHERE product_blocks.name IN ('File')
    """))
    conn.execute(sa.text("""
DELETE FROM processes WHERE processes.pid IN (SELECT processes_subscriptions.pid FROM processes_subscriptions WHERE processes_subscriptions.subscription_id IN (SELECT subscriptions.subscription_id FROM subscriptions WHERE subscriptions.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('file'))))
    """))
    conn.execute(sa.text("""
DELETE FROM processes_subscriptions WHERE processes_subscriptions.subscription_id IN (SELECT subscriptions.subscription_id FROM subscriptions WHERE subscriptions.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('file')))
    """))
    conn.execute(sa.text("""
DELETE FROM subscription_instances WHERE subscription_instances.subscription_id IN (SELECT subscriptions.subscription_id FROM subscriptions WHERE subscriptions.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('file')))
    """))
    conn.execute(sa.text("""
DELETE FROM subscriptions WHERE subscriptions.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('file'))
    """))
    conn.execute(sa.text("""
DELETE FROM products WHERE products.name IN ('file')
    """))
    # Delete workflows
    for workflow in new_workflows:
        delete_workflow(conn, workflow["name"])
