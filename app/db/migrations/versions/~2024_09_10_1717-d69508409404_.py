"""empty message

Revision ID: d69508409404
Revises: 117417bed885
Create Date: 2024-09-10 17:17:58.014693

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "d69508409404"
down_revision = "117417bed885"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE componenttype ADD VALUE 'MULTILINE_TEXT_FIELD';")


def downgrade():
    pass
