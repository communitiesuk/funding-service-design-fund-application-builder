"""empty message

Revision ID: c3ad6fc2300d
Revises: 2309231745
Create Date: 2024-09-25 10:36:49.758320

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3ad6fc2300d"
down_revision = "2309231745"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("component", schema=None) as batch_op:
        batch_op.add_column(sa.Column("content", sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("component", schema=None) as batch_op:
        batch_op.drop_column("content")

    # ### end Alembic commands ###