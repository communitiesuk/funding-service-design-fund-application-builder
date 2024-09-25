"""empty message

Revision ID: 4ec629449867
Revises: ab7d40d652d5
Create Date: 2024-08-19 13:03:32.320669

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "4ec629449867"
down_revision = "ab7d40d652d5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TYPE componenttype ADD VALUE 'PARA';")
    op.execute("ALTER TYPE componenttype ADD VALUE 'DATE_PARTS_FIELD';")
    op.execute("ALTER TYPE componenttype ADD VALUE 'CHECKBOXES_FIELD';")
    op.execute("ALTER TYPE componenttype ADD VALUE 'CLIENT_SIDE_FILE_UPLOAD_FIELD';")
    op.execute("ALTER TYPE componenttype ADD VALUE 'WEBSITE_FIELD';")
    op.execute("ALTER TYPE componenttype ADD VALUE 'TELEPHONE_NUMBER_FIELD';")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Note: PostgreSQL does not support removing values from enums directly.
    # To fully support downgrade, consider creating a new enum without the values and swapping them,
    # or use a workaround that suits your database version and requirements.
    # ### end Alembic commands ###
    pass
