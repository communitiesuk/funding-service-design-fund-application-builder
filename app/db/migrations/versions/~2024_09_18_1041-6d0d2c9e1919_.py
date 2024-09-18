"""Update round table fields in sync with fund store

Revision ID: 6d0d2c9e1919
Revises: 846793bff0d3
Create Date: 2024-09-18 10:41:47.250586

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6d0d2c9e1919'
down_revision = '846793bff0d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('round', schema=None) as batch_op:
        batch_op.add_column(sa.Column('application_reminder_sent', sa.Boolean(), nullable=False,
                                      server_default=sa.text('false')))
        batch_op.add_column(sa.Column('contact_us_banner_json', postgresql.JSON(none_as_null=True,
                                                                                astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('reference_contact_page_over_email', sa.Boolean(), nullable=False,
                                      server_default=sa.text('false')))
        batch_op.add_column(sa.Column('contact_email', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('contact_phone', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('contact_textphone', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('support_times', sa.String(), nullable=False,
                                      server_default=''))
        batch_op.add_column(sa.Column('support_days', sa.String(), nullable=False,
                                      server_default=''))
        batch_op.add_column(sa.Column('instructions_json', postgresql.JSON(none_as_null=True,
                                                                           astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('feedback_link', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('project_name_field_id', sa.String(), nullable=False,
                                      server_default=''))
        batch_op.add_column(sa.Column('application_guidance_json', postgresql.JSON(none_as_null=True,
                                                                                   astext_type=sa.Text()), nullable=True
                                      ))
        batch_op.add_column(sa.Column('guidance_url', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('all_uploaded_documents_section_available', sa.Boolean(),
                                      nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('application_fields_download_available', sa.Boolean(),
                                      nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('display_logo_on_pdf_exports', sa.Boolean(),
                                      nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('mark_as_complete_enabled', sa.Boolean(),
                                      nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('is_expression_of_interest', sa.Boolean(),
                                      nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('feedback_survey_config', postgresql.JSON(none_as_null=True,
                                                                                astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('eligibility_config', postgresql.JSON(none_as_null=True,
                                                                            astext_type=sa.Text()), nullable=True))
        batch_op.add_column(sa.Column('eoi_decision_schema', postgresql.JSON(none_as_null=True,
                                                                             astext_type=sa.Text()), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('round', schema=None) as batch_op:
        batch_op.drop_column('eoi_decision_schema')
        batch_op.drop_column('eligibility_config')
        batch_op.drop_column('feedback_survey_config')
        batch_op.drop_column('is_expression_of_interest')
        batch_op.drop_column('mark_as_complete_enabled')
        batch_op.drop_column('display_logo_on_pdf_exports')
        batch_op.drop_column('application_fields_download_available')
        batch_op.drop_column('all_uploaded_documents_section_available')
        batch_op.drop_column('guidance_url')
        batch_op.drop_column('application_guidance_json')
        batch_op.drop_column('project_name_field_id')
        batch_op.drop_column('feedback_link')
        batch_op.drop_column('instructions_json')
        batch_op.drop_column('support_days')
        batch_op.drop_column('support_times')
        batch_op.drop_column('contact_textphone')
        batch_op.drop_column('contact_phone')
        batch_op.drop_column('contact_email')
        batch_op.drop_column('reference_contact_page_over_email')
        batch_op.drop_column('contact_us_banner_json')
        batch_op.drop_column('application_reminder_sent')

    # ### end Alembic commands ###
