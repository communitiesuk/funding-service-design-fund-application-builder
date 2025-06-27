"""Remove children column from a component

Revision ID: 60c0a648f835
Revises: 8bb21a84a0e2
Create Date: 2025-06-26 15:47:17.345948

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "60c0a648f835"
down_revision = "8bb21a84a0e2"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("component", schema=None) as batch_op:
        batch_op.drop_column("children")

    with op.batch_alter_table("round", schema=None) as batch_op:
        batch_op.alter_column(
            "section_base_path",
            existing_type=sa.INTEGER(),
            server_default=sa.text("nextval('section_base_path_seq')"),
            existing_nullable=True,
        )


def downgrade():
    with op.batch_alter_table("round", schema=None) as batch_op:
        batch_op.alter_column(
            "section_base_path",
            existing_type=sa.INTEGER(),
            server_default=sa.text("nextval('section_base_path_seq'::regclass)"),
            existing_nullable=True,
        )

    with op.batch_alter_table("component", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("children", postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True)
        )
