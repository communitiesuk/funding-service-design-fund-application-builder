"""empty message

Revision ID: ca6ccf18956b
Revises: da30746cec39
Create Date: 2024-10-18 03:44:16.320217

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ca6ccf18956b'
down_revision = 'da30746cec39'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.add_column(sa.Column('section', postgresql.JSON(none_as_null=True, astext_type=sa.Text()), nullable=True))

    with op.batch_alter_table('round', schema=None) as batch_op:
        batch_op.alter_column('application_reminder_sent',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               existing_nullable=False)
        batch_op.alter_column('reference_contact_page_over_email',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               existing_nullable=False)
        batch_op.alter_column('support_times',
               existing_type=sa.VARCHAR(),
               server_default=None,
               existing_nullable=False)
        batch_op.alter_column('support_days',
               existing_type=sa.VARCHAR(),
               server_default=None,
               existing_nullable=False)
        batch_op.alter_column('project_name_field_id',
               existing_type=sa.VARCHAR(),
               server_default=None,
               existing_nullable=False)
        batch_op.alter_column('all_uploaded_documents_section_available',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               existing_nullable=False)
        batch_op.alter_column('application_fields_download_available',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               existing_nullable=False)
        batch_op.alter_column('display_logo_on_pdf_exports',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               existing_nullable=False)
        batch_op.alter_column('mark_as_complete_enabled',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               existing_nullable=False)
        batch_op.alter_column('is_expression_of_interest',
               existing_type=sa.BOOLEAN(),
               server_default=None,
               existing_nullable=False)
        batch_op.alter_column('section_base_path',
               existing_type=sa.INTEGER(),
               server_default=sa.text("nextval('section_base_path_seq')"),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('round', schema=None) as batch_op:
        batch_op.alter_column('section_base_path',
               existing_type=sa.INTEGER(),
               server_default=sa.text("nextval('section_base_path_seq'::regclass)"),
               existing_nullable=True)
        batch_op.alter_column('is_expression_of_interest',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               existing_nullable=False)
        batch_op.alter_column('mark_as_complete_enabled',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               existing_nullable=False)
        batch_op.alter_column('display_logo_on_pdf_exports',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               existing_nullable=False)
        batch_op.alter_column('application_fields_download_available',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               existing_nullable=False)
        batch_op.alter_column('all_uploaded_documents_section_available',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               existing_nullable=False)
        batch_op.alter_column('project_name_field_id',
               existing_type=sa.VARCHAR(),
               server_default=sa.text("''::character varying"),
               existing_nullable=False)
        batch_op.alter_column('support_days',
               existing_type=sa.VARCHAR(),
               server_default=sa.text("''::character varying"),
               existing_nullable=False)
        batch_op.alter_column('support_times',
               existing_type=sa.VARCHAR(),
               server_default=sa.text("''::character varying"),
               existing_nullable=False)
        batch_op.alter_column('reference_contact_page_over_email',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               existing_nullable=False)
        batch_op.alter_column('application_reminder_sent',
               existing_type=sa.BOOLEAN(),
               server_default=sa.text('false'),
               existing_nullable=False)

    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.drop_column('section')

    # ### end Alembic commands ###
