# Dictat Authorization Policies using Open Policy Agent (OPA)
# TODO Phase 2: Implement comprehensive authorization rules

package dictat

import future.keywords.if
import future.keywords.in

# Default deny
default allow = false

# Helper: Check if user is admin
is_admin if {
    input.user.role == "admin"
}

# Helper: Check if user is doctor
is_doctor if {
    input.user.role == "doctor"
}

# Helper: Check if user is secretary
is_secretary if {
    input.user.role == "secretary"
}

# Helper: Check if user owns resource
owns_resource if {
    input.resource.owner_id == input.user.id
}

# Admin can do everything
allow if {
    is_admin
}

# ============================================================================
# Dictation Policies
# ============================================================================

# Doctors can create dictations
allow if {
    is_doctor
    input.action == "create"
    input.resource.type == "dictation"
}

# Doctors can read their own dictations
allow if {
    is_doctor
    input.action == "read"
    input.resource.type == "dictation"
    owns_resource
}

# Doctors can update their own dictations
allow if {
    is_doctor
    input.action == "update"
    input.resource.type == "dictation"
    owns_resource
}

# Doctors can delete their own dictations
allow if {
    is_doctor
    input.action == "delete"
    input.resource.type == "dictation"
    owns_resource
}

# Secretaries can read available dictations
allow if {
    is_secretary
    input.action == "read"
    input.resource.type == "dictation"
}

# Secretaries can claim dictations
allow if {
    is_secretary
    input.action == "claim"
    input.resource.type == "dictation"
}

# Secretaries can stream audio for assigned dictations
allow if {
    is_secretary
    input.action == "stream_audio"
    input.resource.type == "dictation"
    input.resource.assigned_to == input.user.id
}

# ============================================================================
# Transcription Policies
# ============================================================================

# Secretaries can create transcriptions for their assigned dictations
allow if {
    is_secretary
    input.action == "create"
    input.resource.type == "transcription"
    input.context.dictation_assigned_to == input.user.id
}

# Secretaries can update their own transcriptions
allow if {
    is_secretary
    input.action == "update"
    input.resource.type == "transcription"
    owns_resource
}

# Secretaries can submit their own transcriptions
allow if {
    is_secretary
    input.action == "submit"
    input.resource.type == "transcription"
    owns_resource
}

# Doctors can read transcriptions for their dictations
allow if {
    is_doctor
    input.action == "read"
    input.resource.type == "transcription"
    input.context.dictation_owner_id == input.user.id
}

# Doctors can approve/reject transcriptions for their dictations
allow if {
    is_doctor
    input.action in ["approve", "reject"]
    input.resource.type == "transcription"
    input.context.dictation_owner_id == input.user.id
}

# ============================================================================
# User Management Policies
# ============================================================================

# Users can read their own profile
allow if {
    input.action == "read"
    input.resource.type == "user"
    input.resource.id == input.user.id
}

# Users can update their own profile
allow if {
    input.action == "update"
    input.resource.type == "user"
    input.resource.id == input.user.id
}

# ============================================================================
# Audit Log Policies
# ============================================================================

# Only admins can query audit logs
allow if {
    is_admin
    input.action == "read"
    input.resource.type == "audit_log"
}

# ============================================================================
# GDPR Policies
# ============================================================================

# Users can export their own data
allow if {
    input.action == "data_export"
    input.resource.type == "gdpr"
}

# Users can delete their own account
allow if {
    input.action == "delete_account"
    input.resource.type == "gdpr"
}

# Users can manage their own consent
allow if {
    input.action in ["read_consent", "update_consent"]
    input.resource.type == "gdpr"
}

# TODO Phase 2: Add more granular policies
# - Prevent deletion of dictations with active transcriptions
# - Enforce status transition rules
# - Add time-based access controls
# - Implement data retention policies
