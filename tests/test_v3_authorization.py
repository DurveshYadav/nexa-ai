
from uuid import uuid4
import uuid

import pytest

from app.models.user import User
from app.services.v3.authorization import (
    KNOWN_AGENT_PERMISSIONS,
    build_execution_context,
)


def create_user(db, permissions=None):
    customer_id = int(uuid.uuid4().int % 1_000_000_000) + 1
    user = User(
        email=f"auth-{uuid.uuid4().hex[:10]}@example.com",
        password_hash="test-hash",
        customer_id=customer_id,
        agent_permissions=permissions,
    )

    if permissions is not None:
        user.agent_permissions = permissions

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def test_build_context_loads_database_permissions(db):
    user = create_user(
        db,
        [
            "orders:read",
            "products:read",
            "refunds:read",
        ],
    )

    context = build_execution_context(
        user_id=user.id,
        customer_id=user.customer_id,
        run_id="run-001",
        request_id="request-001",
        db=db,
    )

    assert context.user_id == user.id
    assert context.customer_id == user.customer_id
    assert context.permissions == frozenset({
        "orders:read",
        "products:read",
        "refunds:read",
    })


def test_build_context_does_not_grant_unassigned_permissions(db):
    user = create_user(db, ["orders:read"])

    context = build_execution_context(
        user_id=user.id,
        customer_id=user.customer_id,
        run_id="run-002",
        request_id="request-002",
        db=db,
    )

    assert "orders:read" in context.permissions
    assert "orders:write" not in context.permissions
    assert "refunds:write" not in context.permissions


def test_build_context_ignores_unknown_permissions(db):
    user = create_user(
        db,
        ["orders:read", "unknown:permission"],
    )

    context = build_execution_context(
        user_id=user.id,
        customer_id=user.customer_id,
        run_id="run-003",
        request_id="request-003",
        db=db,
    )

    assert context.permissions == frozenset({"orders:read"})
    assert context.permissions.issubset(KNOWN_AGENT_PERMISSIONS)


def test_build_context_rejects_missing_database():
    with pytest.raises(ValueError, match="Database session is required"):
        build_execution_context(
            user_id=1,
            customer_id=1001,
            run_id="run-004",
            request_id="request-004",
        )


def test_build_context_rejects_missing_user(db):
    with pytest.raises(ValueError, match="Authenticated user not found"):
        build_execution_context(
            user_id=-1,
            customer_id=1001,
            run_id="run-005",
            request_id="request-005",
            db=db,
        )


def test_build_context_rejects_wrong_customer_mapping(db):
    user = create_user(db)

    with pytest.raises(ValueError, match="customer mapping is invalid"):
        build_execution_context(
            user_id=user.id,
            customer_id=999999,
            run_id="run-006",
            request_id="request-006",
            db=db,
        )


def test_build_context_rejects_user_without_customer_mapping(db):
    user = create_user(db)
    user.customer_id = None
    db.commit()

    with pytest.raises(ValueError, match="customer mapping is invalid"):
        build_execution_context(
            user_id=user.id,
            customer_id=900000 + int(uuid4().hex[:8], 16),
            run_id="run-007",
            request_id="request-007",
            db=db,
        )
