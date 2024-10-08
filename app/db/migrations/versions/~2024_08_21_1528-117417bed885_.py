"""empty message

Revision ID: 117417bed885
Revises: ed84bb152ee3
Create Date: 2024-08-21 15:28:58.583369

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "117417bed885"
down_revision = "ed84bb152ee3"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("lizt", schema=None) as batch_op:
        batch_op.add_column(sa.Column("title", sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("lizt", schema=None) as batch_op:
        batch_op.drop_column("title")

    # ### end Alembic commands ###
