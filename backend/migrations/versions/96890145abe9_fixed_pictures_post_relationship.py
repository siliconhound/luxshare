"""fixed pictures/post relationship

Revision ID: 96890145abe9
Revises: 5cd0ddf96219
Create Date: 2018-09-06 23:07:19.361648

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96890145abe9'
down_revision = '5cd0ddf96219'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('picture', sa.Column('post_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'picture', 'post', ['post_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'picture', type_='foreignkey')
    op.drop_column('picture', 'post_id')
    # ### end Alembic commands ###
