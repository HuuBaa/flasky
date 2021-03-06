"""add body_html

Revision ID: 3069688836ab
Revises: bb94629c9d48
Create Date: 2017-08-19 18:37:46.883686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3069688836ab'
down_revision = 'bb94629c9d48'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('body_html', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'body_html')
    # ### end Alembic commands ###
