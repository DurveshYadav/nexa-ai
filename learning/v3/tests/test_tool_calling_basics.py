import pytest
from pydantic import ValidationError

from learning.v3.tool_calling_basics import (
    execute_tool,
    simulate_llm_tool_call,
    execute_secure_tool_call,
    execute_provider_tool_call,
    build_provider_tool_result_message,
    execute_secure_provider_tool_call,
    build_secure_provider_tool_result_message,
    validate_tool_call_batch,
    execute_multiple_tools, check_tool_approval
)


def test_execute_valid_product_tool():
    result = execute_tool(
        "get_product_details",
        {"product_id": "PROD-101"},
    )

    assert result["success"] is True
    assert result["data"]["name"] == "Wireless Headphones"
    assert result["data"]["price"] == 2999


def test_execute_tool_rejects_invalid_product_id():
    with pytest.raises(ValidationError):
        execute_tool(
            "get_product_details",
            {"product_id": "INVALID"},
        )


def test_simulate_llm_tool_call_rejects_unknown_tool():
    with pytest.raises(ValueError, match="Unknown tool"):
        simulate_llm_tool_call({
            "name": "delete_customer",
            "arguments": {},
        })

def test_user_can_access_own_order():
    result = execute_secure_tool_call(
        authenticated_user_id="USER-001",
        tool_name="get_order_status",
        arguments={"order_id": "ORD-10025"},
    )

    assert result["success"] is True


def test_user_cannot_access_another_users_order():
    result = execute_secure_tool_call(
        authenticated_user_id="USER-001",
        tool_name="get_order_status",
        arguments={"order_id": "ORD-10026"},
    )

    assert result["success"] is False
    assert result["error"]["code"] == "ACCESS_DENIED"


def test_user_without_permission_cannot_access_products():
    result = execute_secure_tool_call(
        authenticated_user_id="USER-999",
        tool_name="get_product_details",
        arguments={"product_id": "PROD-101"},
    )

    assert result["success"] is False
    assert result["error"]["code"] == "SECURITY_DENIED"

def test_provider_tool_call_executes_successfully():
    provider_call = {
        "id": "call_test_001",
        "type": "function",
        "function": {
            "name": "get_product_details",
            "arguments": '{"product_id": "PROD-101"}',
        },
    }

    result = execute_provider_tool_call(provider_call)

    assert result["tool_call_id"] == "call_test_001"
    assert result["result"]["success"] is True


def test_provider_tool_call_rejects_invalid_json():
    provider_call = {
        "id": "call_test_002",
        "type": "function",
        "function": {
            "name": "get_product_details",
            "arguments": '{"product_id": ',
        },
    }

    with pytest.raises(ValueError, match="invalid JSON"):
        execute_provider_tool_call(provider_call)


def test_provider_tool_result_preserves_call_id():
    execution_result = {
        "tool_call_id": "call_test_003",
        "tool_name": "get_product_details",
        "result": {
            "success": True,
            "data": {"name": "Wireless Headphones"},
        },
    }

    message = build_provider_tool_result_message(execution_result)

    assert message["role"] == "tool"
    assert message["tool_call_id"] == "call_test_003"
    assert "Wireless Headphones" in message["content"]

def test_secure_provider_call_denies_unauthorized_user():
    provider_call = {
        "id": "call_denied_test_001",
        "type": "function",
        "function": {
            "name": "get_product_details",
            "arguments": '{"product_id": "PROD-101"}',
        },
    }

    result = execute_secure_provider_tool_call(
        authenticated_user_id="USER-999",
        provider_call=provider_call,
    )

    assert result["tool_call_id"] == "call_denied_test_001"
    assert result["result"]["success"] is False
    assert result["result"]["error"]["code"] == "SECURITY_DENIED"


def test_secure_provider_error_can_be_returned_to_provider():
    execution_result = {
        "tool_call_id": "call_denied_test_002",
        "tool_name": "get_product_details",
        "result": {
            "success": False,
            "error": {
                "code": "SECURITY_DENIED",
                "message": "Permission denied.",
            },
        },
    }

    message = build_secure_provider_tool_result_message(
        execution_result
    )

    assert message["role"] == "tool"
    assert message["tool_call_id"] == "call_denied_test_002"
    assert "SECURITY_DENIED" in message["content"]

def test_tool_choice_none_rejects_requested_tool():
    result = validate_tool_call_batch(
        tool_choice="none",
        requested_tools=["get_product_details"],
    )

    assert result["allowed"] is False


def test_tool_choice_required_rejects_empty_batch():
    result = validate_tool_call_batch(
        tool_choice="required",
        requested_tools=[],
    )

    assert result["allowed"] is False


def test_specific_tool_choice_accepts_matching_tool():
    result = validate_tool_call_batch(
        tool_choice="get_product_details",
        requested_tools=["get_product_details"],
    )

    assert result["allowed"] is True


def test_specific_tool_choice_rejects_different_tool():
    result = validate_tool_call_batch(
        tool_choice="get_product_details",
        requested_tools=["get_order_status"],
    )

    assert result["allowed"] is False

def test_multiple_tool_calls_continue_after_failure():
    calls = [
        {
            "name": "get_order_status",
            "arguments": {"order_id": "ORD-10025"},
        },
        {
            "name": "get_product_details",
            "arguments": {"product_id": "INVALID"},
        },
        {
            "name": "delete_customer",
            "arguments": {},
        },
        {
            "name": "get_product_details",
            "arguments": {"product_id": "PROD-101"},
        },
    ]

    results = execute_multiple_tools(calls)

    assert len(results) == 4
    assert results[0]["execution_success"] is True
    assert results[1]["error"]["code"] == "VALIDATION_ERROR"
    assert results[2]["error"]["code"] == "TOOL_CALL_ERROR"
    assert results[3]["execution_success"] is True


def test_multiple_tool_calls_preserve_call_order():
    calls = [
        {
            "name": "get_order_status",
            "arguments": {"order_id": "ORD-10025"},
        },
        {
            "name": "get_product_details",
            "arguments": {"product_id": "PROD-101"},
        },
    ]

    results = execute_multiple_tools(calls)

    assert results[0]["tool_call_number"] == 1
    assert results[1]["tool_call_number"] == 2

def test_read_tool_does_not_require_approval():
    assert check_tool_approval(
        "get_order_status",
        user_approved=False,
    ) is True


def test_cancel_order_requires_approval():
    assert check_tool_approval(
        "cancel_order",
        user_approved=False,
    ) is False


def test_cancel_order_allowed_after_approval():
    assert check_tool_approval(
        "cancel_order",
        user_approved=True,
    ) is True
    

def test_audit_log_records_successful_order_access():
    from learning.v3.tool_calling_basics import SECURITY_AUDIT_LOG

    SECURITY_AUDIT_LOG.clear()

    result = execute_secure_tool_call(
        authenticated_user_id="USER-001",
        tool_name="get_order_status",
        arguments={"order_id": "ORD-10025"},
    )

    assert result["success"] is True
    event = SECURITY_AUDIT_LOG[-1]

    assert event["permission_granted"] is True
    assert event["approval_granted"] is True
    assert event["execution_allowed"] is True
    assert event["resource_authorized"] is True
    assert event["execution_completed"] is True


def test_audit_log_records_resource_access_denial():
    from learning.v3.tool_calling_basics import SECURITY_AUDIT_LOG

    SECURITY_AUDIT_LOG.clear()

    result = execute_secure_tool_call(
        authenticated_user_id="USER-001",
        tool_name="get_order_status",
        arguments={"order_id": "ORD-10026"},
    )

    assert result["success"] is False
    assert result["error"]["code"] == "ACCESS_DENIED"

    event = SECURITY_AUDIT_LOG[-1]

    assert event["permission_granted"] is True
    assert event["execution_allowed"] is True
    assert event["resource_authorized"] is False
    assert event["execution_completed"] is False


def test_audit_log_records_successful_product_lookup():
    from learning.v3.tool_calling_basics import SECURITY_AUDIT_LOG

    SECURITY_AUDIT_LOG.clear()

    result = execute_secure_tool_call(
        authenticated_user_id="USER-001",
        tool_name="get_product_details",
        arguments={"product_id": "PROD-101"},
    )

    assert result["success"] is True
    event = SECURITY_AUDIT_LOG[-1]

    assert event["permission_granted"] is True
    assert event["execution_allowed"] is True
    assert event["resource_authorized"] is True
    assert event["execution_completed"] is True


def test_provider_tool_call_rejects_missing_id():
    provider_call = {
        "function": {
            "name": "get_product_details",
            "arguments": '{"product_id": "PROD-101"}',
        },
    }

    with pytest.raises(ValueError, match="valid ID"):
        execute_provider_tool_call(provider_call)


def test_provider_tool_call_rejects_missing_function():
    provider_call = {
        "id": "call_missing_function",
    }

    with pytest.raises(ValueError, match="function object"):
        execute_provider_tool_call(provider_call)


def test_provider_tool_call_rejects_non_string_arguments():
    provider_call = {
        "id": "call_invalid_arguments",
        "function": {
            "name": "get_product_details",
            "arguments": {"product_id": "PROD-101"},
        },
    }

    with pytest.raises(TypeError, match="JSON string"):
        execute_provider_tool_call(provider_call)


def test_provider_tool_call_rejects_json_array():
    provider_call = {
        "id": "call_json_array",
        "function": {
            "name": "get_product_details",
            "arguments": '["PROD-101"]',
        },
    }

    with pytest.raises(TypeError, match="JSON object"):
        execute_provider_tool_call(provider_call)


def test_secure_provider_call_rejects_missing_id():
    provider_call = {
        "function": {
            "name": "get_product_details",
            "arguments": '{"product_id": "PROD-101"}',
        },
    }

    with pytest.raises(ValueError, match="valid ID"):
        execute_secure_provider_tool_call(
            authenticated_user_id="USER-001",
            provider_call=provider_call,
        )


def test_secure_provider_call_rejects_invalid_json():
    provider_call = {
        "id": "call_secure_invalid_json",
        "function": {
            "name": "get_product_details",
            "arguments": '{"product_id": ',
        },
    }

    with pytest.raises(ValueError, match="invalid JSON"):
        execute_secure_provider_tool_call(
            authenticated_user_id="USER-001",
            provider_call=provider_call,
        )


def test_secure_provider_call_rejects_non_string_arguments():
    provider_call = {
        "id": "call_secure_bad_arguments",
        "function": {
            "name": "get_product_details",
            "arguments": {"product_id": "PROD-101"},
        },
    }

    with pytest.raises(TypeError, match="JSON string"):
        execute_secure_provider_tool_call(
            authenticated_user_id="USER-001",
            provider_call=provider_call,
        )


def test_secure_provider_call_rejects_json_array():
    provider_call = {
        "id": "call_secure_json_array",
        "function": {
            "name": "get_product_details",
            "arguments": '["PROD-101"]',
        },
    }

    with pytest.raises(TypeError, match="decode to an object"):
        execute_secure_provider_tool_call(
            authenticated_user_id="USER-001",
            provider_call=provider_call,
        )
