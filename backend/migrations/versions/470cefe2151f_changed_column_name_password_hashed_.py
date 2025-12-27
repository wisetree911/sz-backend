"""changed column name password -> hashed_password

Revision ID: 470cefe2151f
Revises: 0673f6bc7472
Create Date: 2025-12-27 19:44:18.438435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '470cefe2151f'
down_revision: Union[str, Sequence[str], None] = '0673f6bc7472'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "password",
        new_column_name="hashed_password",
        existing_type=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        new_column_name="password",
        existing_type=sa.Text(),
        existing_nullable=False,
    )