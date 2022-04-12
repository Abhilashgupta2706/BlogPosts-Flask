"""Added profile pic for user

Revision ID: 14c9ca03562d
Revises: 
Create Date: 2022-04-12 14:04:28.285818

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14c9ca03562d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user_profile_pic', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'user_profile_pic')
    # ### end Alembic commands ###