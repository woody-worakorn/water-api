"""Updated transaction model

Revision ID: 5d8e33c6764c
Revises: b61d5ce8eb84
Create Date: 2024-11-24 14:11:09.425170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d8e33c6764c'
down_revision: Union[str, None] = 'b61d5ce8eb84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
