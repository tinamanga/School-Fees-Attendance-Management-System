"""Add user_id to Student"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '534fdf0b945b'
down_revision = '1df57839fb9d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_students_user_id_users',
            'users',
            ['user_id'],
            ['id']
        )
        batch_op.create_unique_constraint(
            'uq_students_user_id',
            ['user_id']
        )


def downgrade():
    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.drop_constraint('uq_students_user_id', type_='unique')
        batch_op.drop_constraint('fk_students_user_id_users', type_='foreignkey')
        batch_op.drop_column('user_id')
