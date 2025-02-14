"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade():
    op.drop_column('problems', 'sample_input')
    op.drop_column('problems', 'sample_output')

def downgrade():
    op.add_column('problems', sa.Column('sample_input', sa.Text(), nullable=True))
    op.add_column('problems', sa.Column('sample_output', sa.Text(), nullable=True))

