"""Add parent component column into component

Revision ID: 8bb21a84a0e2
Revises: 7b151261e00d
Create Date: 2025-06-24 13:00:12.044834

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8bb21a84a0e2"
down_revision = "7b151261e00d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("component", schema=None) as batch_op:
        batch_op.add_column(sa.Column("parent_component_id", sa.UUID(), nullable=True))
        batch_op.create_foreign_key(
            batch_op.f("fk_component_parent_component_id_component"),
            "component",
            ["parent_component_id"],
            ["component_id"],
        )

    with op.batch_alter_table("round", schema=None) as batch_op:
        batch_op.alter_column(
            "section_base_path",
            existing_type=sa.INTEGER(),
            server_default=sa.text("nextval('section_base_path_seq')"),
            existing_nullable=True,
        )
        batch_op.alter_column("status", existing_type=sa.VARCHAR(), server_default=None, existing_nullable=False)


def downgrade():
    with op.batch_alter_table("round", schema=None) as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.VARCHAR(),
            server_default=sa.text("'In progress'::character varying"),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "section_base_path",
            existing_type=sa.INTEGER(),
            server_default=sa.text("nextval('section_base_path_seq'::regclass)"),
            existing_nullable=True,
        )

    with op.batch_alter_table("component", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("fk_component_parent_component_id_component"), type_="foreignkey")
        batch_op.drop_column("parent_component_id")
