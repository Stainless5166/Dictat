# OPA Policy Tests for Dictat Authorization

package dictat

import future.keywords.if

# ============================================================================
# Admin Tests
# ============================================================================

test_admin_can_do_everything if {
    allow with input as {
        "user": {"id": 1, "role": "admin"},
        "action": "delete",
        "resource": {"type": "dictation", "id": 1, "owner_id": 2},
    }
}

# ============================================================================
# Dictation Tests - Doctor
# ============================================================================

test_doctor_can_create_dictation if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "create",
        "resource": {"type": "dictation"},
    }
}

test_doctor_can_read_own_dictation if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "read",
        "resource": {"type": "dictation", "id": 1, "owner_id": 1},
    }
}

test_doctor_cannot_read_other_dictation if {
    not allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "read",
        "resource": {"type": "dictation", "id": 2, "owner_id": 2},
    }
}

test_doctor_can_update_own_dictation if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "update",
        "resource": {"type": "dictation", "id": 1, "owner_id": 1},
    }
}

test_doctor_can_delete_own_dictation if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "delete",
        "resource": {"type": "dictation", "id": 1, "owner_id": 1},
    }
}

# ============================================================================
# Dictation Tests - Secretary
# ============================================================================

test_secretary_can_read_dictations if {
    allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "read",
        "resource": {"type": "dictation", "id": 1},
    }
}

test_secretary_can_claim_dictation if {
    allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "claim",
        "resource": {"type": "dictation", "id": 1},
    }
}

test_secretary_cannot_create_dictation if {
    not allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "create",
        "resource": {"type": "dictation"},
    }
}

test_secretary_cannot_delete_dictation if {
    not allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "delete",
        "resource": {"type": "dictation", "id": 1},
    }
}

test_secretary_can_stream_assigned_audio if {
    allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "stream_audio",
        "resource": {"type": "dictation", "id": 1, "assigned_to": 2},
    }
}

test_secretary_cannot_stream_unassigned_audio if {
    not allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "stream_audio",
        "resource": {"type": "dictation", "id": 1, "assigned_to": 3},
    }
}

# ============================================================================
# Transcription Tests - Secretary
# ============================================================================

test_secretary_can_create_transcription if {
    allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "create",
        "resource": {"type": "transcription"},
        "context": {"dictation_assigned_to": 2},
    }
}

test_secretary_cannot_create_transcription_for_unassigned if {
    not allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "create",
        "resource": {"type": "transcription"},
        "context": {"dictation_assigned_to": 3},
    }
}

test_secretary_can_update_own_transcription if {
    allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "update",
        "resource": {"type": "transcription", "id": 1, "owner_id": 2},
    }
}

test_secretary_can_submit_own_transcription if {
    allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "submit",
        "resource": {"type": "transcription", "id": 1, "owner_id": 2},
    }
}

# ============================================================================
# Transcription Tests - Doctor
# ============================================================================

test_doctor_can_read_own_dictation_transcription if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "read",
        "resource": {"type": "transcription", "id": 1},
        "context": {"dictation_owner_id": 1},
    }
}

test_doctor_can_approve_own_dictation_transcription if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "approve",
        "resource": {"type": "transcription", "id": 1},
        "context": {"dictation_owner_id": 1},
    }
}

test_doctor_can_reject_own_dictation_transcription if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "reject",
        "resource": {"type": "transcription", "id": 1},
        "context": {"dictation_owner_id": 1},
    }
}

test_doctor_cannot_approve_other_dictation_transcription if {
    not allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "approve",
        "resource": {"type": "transcription", "id": 1},
        "context": {"dictation_owner_id": 2},
    }
}

# ============================================================================
# User Management Tests
# ============================================================================

test_user_can_read_own_profile if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "read",
        "resource": {"type": "user", "id": 1},
    }
}

test_user_cannot_read_other_profile if {
    not allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "read",
        "resource": {"type": "user", "id": 2},
    }
}

test_user_can_update_own_profile if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "update",
        "resource": {"type": "user", "id": 1},
    }
}

# ============================================================================
# Audit Log Tests
# ============================================================================

test_only_admin_can_read_audit_logs if {
    allow with input as {
        "user": {"id": 1, "role": "admin"},
        "action": "read",
        "resource": {"type": "audit_log"},
    }
}

test_doctor_cannot_read_audit_logs if {
    not allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "read",
        "resource": {"type": "audit_log"},
    }
}

test_secretary_cannot_read_audit_logs if {
    not allow with input as {
        "user": {"id": 2, "role": "secretary"},
        "action": "read",
        "resource": {"type": "audit_log"},
    }
}

# ============================================================================
# GDPR Tests
# ============================================================================

test_user_can_export_own_data if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "data_export",
        "resource": {"type": "gdpr"},
    }
}

test_user_can_delete_own_account if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "delete_account",
        "resource": {"type": "gdpr"},
    }
}

test_user_can_manage_consent if {
    allow with input as {
        "user": {"id": 1, "role": "doctor"},
        "action": "read_consent",
        "resource": {"type": "gdpr"},
    }
}

# ============================================================================
# Default Deny Tests
# ============================================================================

test_default_deny if {
    not allow with input as {
        "user": {"id": 1, "role": "unknown_role"},
        "action": "some_action",
        "resource": {"type": "some_resource"},
    }
}

test_unauthenticated_deny if {
    not allow with input as {
        "action": "read",
        "resource": {"type": "dictation"},
    }
}
