"""empty message

Revision ID: 2309231745
Revises: 6d0d2c9e1919
Create Date: 2024-08-19 13:03:32.320669

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "2309231745"
down_revision = "6d0d2c9e1919"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    component_types = [
        "NUMBER_FIELD",
        "DATE_FIELD",
        "DATE_TIME_FIELD",
        "DATE_TIME_PARTS_FIELD",
        "SELECT_FIELD",
        "INSET_TEXT_FIELD",
        "DETAILS_FIELD",
        "LIST_FIELD",
        "AUTO_COMPLETE_FIELD",
        "FILE_UPLOAD_FIELD",
        "MONTH_YEAR_FIELD",
        "TIME_FIELD",
    ]

    for type_name in component_types:
        op.execute(f"ALTER TYPE componenttype ADD VALUE '{type_name}';")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Note: PostgreSQL does not support removing values from enums directly.
    # To fully support downgrade, consider creating a new enum without the values and swapping them,
    # or use a workaround that suits your database version and requirements.
    # ### end Alembic commands ###
    pass
