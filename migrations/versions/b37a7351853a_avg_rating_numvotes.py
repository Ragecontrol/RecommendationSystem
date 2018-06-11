"""avg rating numvotes

Revision ID: b37a7351853a
Revises: a5e1e0042c0e
Create Date: 2018-06-09 17:13:45.460516

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b37a7351853a'
down_revision = 'a5e1e0042c0e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('film', sa.Column('averageRating', sa.Float(), nullable=True))
    op.add_column('film', sa.Column('numVotes', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('film', 'numVotes')
    op.drop_column('film', 'averageRating')
    # ### end Alembic commands ###
