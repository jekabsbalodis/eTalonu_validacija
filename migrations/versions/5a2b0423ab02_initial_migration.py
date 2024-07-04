"""Initial migration.

Revision ID: 5a2b0423ab02
Revises: 
Create Date: 2024-07-04 11:59:53.291432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a2b0423ab02'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('validacijas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parks', sa.String(length=10), nullable=True),
    sa.Column('transp_veids', sa.String(length=32), nullable=True),
    sa.Column('gar_nr', sa.Integer(), nullable=True),
    sa.Column('mars_nos', sa.Text(), nullable=True),
    sa.Column('marsruts', sa.String(length=10), nullable=True),
    sa.Column('virziens', sa.String(length=10), nullable=True),
    sa.Column('talona_id', sa.Integer(), nullable=True),
    sa.Column('laiks', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('validacijas')
    # ### end Alembic commands ###
