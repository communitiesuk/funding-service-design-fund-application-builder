"""Add ggis field to fund

Revision ID: 185439eb14e7
Revises: eaf8ef40627c
Create Date: 2024-11-06 13:37:36.119246

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "185439eb14e7"
down_revision = "eaf8ef40627c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("fund", schema=None) as batch_op:
        batch_op.add_column(sa.Column("ggis_scheme_reference_number", sa.String(length=255), nullable=True))

    with op.batch_alter_table("round", schema=None) as batch_op:
        batch_op.alter_column(
            "section_base_path",
            existing_type=sa.INTEGER(),
            server_default=sa.text("nextval('section_base_path_seq')"),
            existing_nullable=True,
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("round", schema=None) as batch_op:
        batch_op.alter_column(
            "section_base_path",
            existing_type=sa.INTEGER(),
            server_default=sa.text("nextval('section_base_path_seq'::regclass)"),
            existing_nullable=True,
        )

    with op.batch_alter_table("fund", schema=None) as batch_op:
        batch_op.drop_column("ggis_scheme_reference_number")

    # ### end Alembic commands ###