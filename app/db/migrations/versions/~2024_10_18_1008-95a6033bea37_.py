"""Add funding_type to fund table

Revision ID: 95a6033bea37
Revises: da30746cec39
Create Date: 2024-10-18 10:08:54.071885

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "95a6033bea37"
down_revision = "da30746cec39"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    funding_type_enum = postgresql.ENUM("COMPETITIVE", "UNCOMPETED", "EOI", name="fundingtype")
    funding_type_enum.create(op.get_bind())
    with op.batch_alter_table("fund", schema=None) as batch_op:
        batch_op.add_column(sa.Column("funding_type", funding_type_enum, nullable=True))
    op.execute(sa.text("UPDATE fund SET funding_type='COMPETITIVE'"))
    with op.batch_alter_table("fund", schema=None) as batch_op:
        batch_op.alter_column("funding_type", nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table("fund", schema=None) as batch_op:
        batch_op.drop_column("funding_type")
    funding_type_enum.drop(op.get_bind())

    # ### end Alembic commands ###
