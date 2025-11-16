"""Initial database schema with User, Dictation, Transcription, AuditLog

Revision ID: 001
Revises:
Create Date: 2025-11-16 02:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema"""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('DOCTOR', 'SECRETARY', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # Create dictations table
    op.create_table(
        'dictations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('secretary_id', sa.Integer(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'REVIEWED', 'REJECTED', name='dictationstatus'), nullable=False, server_default='PENDING'),
        sa.Column('priority', sa.Enum('LOW', 'NORMAL', 'HIGH', 'URGENT', name='dictationpriority'), nullable=False, server_default='NORMAL'),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('patient_reference', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['secretary_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dictations_id'), 'dictations', ['id'], unique=False)
    op.create_index(op.f('ix_dictations_doctor_id'), 'dictations', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_dictations_secretary_id'), 'dictations', ['secretary_id'], unique=False)
    op.create_index(op.f('ix_dictations_status'), 'dictations', ['status'], unique=False)
    op.create_index(op.f('ix_dictations_priority'), 'dictations', ['priority'], unique=False)
    op.create_index(op.f('ix_dictations_created_at'), 'dictations', ['created_at'], unique=False)

    # Create transcriptions table
    op.create_table(
        'transcriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dictation_id', sa.Integer(), nullable=False),
        sa.Column('secretary_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.Enum('DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'REVISED', name='transcriptionstatus'), nullable=False, server_default='DRAFT'),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_autosave_at', sa.DateTime(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['dictation_id'], ['dictations.id'], ),
        sa.ForeignKeyConstraint(['secretary_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcriptions_id'), 'transcriptions', ['id'], unique=False)
    op.create_index(op.f('ix_transcriptions_dictation_id'), 'transcriptions', ['dictation_id'], unique=True)
    op.create_index(op.f('ix_transcriptions_secretary_id'), 'transcriptions', ['secretary_id'], unique=False)
    op.create_index(op.f('ix_transcriptions_reviewer_id'), 'transcriptions', ['reviewer_id'], unique=False)
    op.create_index(op.f('ix_transcriptions_status'), 'transcriptions', ['status'], unique=False)

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.Enum(
            'LOGIN', 'LOGOUT', 'LOGIN_FAILED', 'PASSWORD_CHANGED', 'PASSWORD_RESET',
            'USER_CREATED', 'USER_UPDATED', 'USER_DELETED', 'USER_ACTIVATED', 'USER_DEACTIVATED',
            'DICTATION_CREATED', 'DICTATION_VIEWED', 'DICTATION_UPDATED', 'DICTATION_DELETED',
            'DICTATION_CLAIMED', 'DICTATION_AUDIO_STREAMED',
            'TRANSCRIPTION_CREATED', 'TRANSCRIPTION_VIEWED', 'TRANSCRIPTION_UPDATED',
            'TRANSCRIPTION_DELETED', 'TRANSCRIPTION_SUBMITTED', 'TRANSCRIPTION_APPROVED',
            'TRANSCRIPTION_REJECTED',
            'DATA_EXPORT_REQUESTED', 'DATA_EXPORT_COMPLETED', 'DATA_DELETION_REQUESTED',
            'DATA_DELETION_COMPLETED', 'CONSENT_GIVEN', 'CONSENT_WITHDRAWN',
            'ACCESS_DENIED', 'PERMISSION_CHANGED',
            name='auditaction'
        ), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('request_id', sa.String(length=36), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_resource_type'), 'audit_logs', ['resource_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_resource_id'), 'audit_logs', ['resource_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_request_id'), 'audit_logs', ['request_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('audit_logs')
    op.drop_table('transcriptions')
    op.drop_table('dictations')
    op.drop_table('users')

    # Drop enums
    sa.Enum(name='auditaction').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='transcriptionstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='dictationpriority').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='dictationstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
