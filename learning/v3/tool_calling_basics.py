import json
"""
NexaAI V3 - Phase 3
Topic: Basic Tool / Function Calling
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class GetOrderStatusInput(BaseModel):
    """Validate arguments supplied to the get_order_status tool."""

    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^ORD-[A-Za-z0-9]+$",
        description="Unique order identifier",
    )



class GetProductDetailsInput(BaseModel):
    """Validate arguments supplied to the product details tool."""

    model_config = ConfigDict(extra="forbid")

    product_id: str = Field(
        min_length=5,
        max_length=30,
        pattern=r"^PROD-[A-Za-z0-9]+$",
        description="Unique product identifier",
    )

def get_order_status(order_id: str) -> dict[str, Any]:
    """
    Retrieve the current status of an order.

    Learning example:
    Uses in-memory sample data instead of a real database.
    """

    orders = {
        "ORD-10025": {
            "order_id": "ORD-10025",
            "status": "shipped",
            "tracking_number": "TRK-98765",
        },
        "ORD-10026": {
            "order_id": "ORD-10026",
            "status": "processing",
            "tracking_number": None,
        },
    }

    order = orders.get(order_id)

    if order is None:
        return {
            "success": False,
            "error": {
                "code": "ORDER_NOT_FOUND",
                "message": "Order not found.",
            },
        }

    return {
        "success": True,
        "data": order,
    }





def get_product_details(product_id: str) -> dict[str, Any]:
    """Retrieve product details from sample in-memory data."""

    products = {
        "PROD-101": {
            "product_id": "PROD-101",
            "name": "Wireless Headphones",
            "price": 2999,
            "availability": "in_stock",
        },
        "PROD-102": {
            "product_id": "PROD-102",
            "name": "Bluetooth Speaker",
            "price": 1999,
            "availability": "in_stock",
        },
    }

    product = products.get(product_id)

    if product is None:
        return {
            "success": False,
            "error": {
                "code": "PRODUCT_NOT_FOUND",
                "message": "Product not found.",
            },
        }

    return {
        "success": True,
        "data": product,
    }

def demonstrate_validation() -> None:
    """Demonstrate valid and invalid tool arguments."""

    test_cases = [
        {
            "name": "Valid order ID",
            "arguments": {"order_id": "ORD-10025"},
        },
        {
            "name": "Missing order ID",
            "arguments": {},
        },
        {
            "name": "Invalid order ID",
            "arguments": {"order_id": "INVALID"},
        },
        {
            "name": "Unexpected argument",
            "arguments": {
                "order_id": "ORD-10025",
                "admin": True,
            },
        },
    ]

    for test_case in test_cases:
        print(f"\n========== {test_case['name']} ==========")

        try:
            validated = GetOrderStatusInput.model_validate(
                test_case["arguments"]
            )
            print("VALID:", validated.model_dump())

        except ValidationError as exc:
            print("REJECTED:")
            print(exc)




# ==========================================
# STEP 4: TOOL REGISTRY
# ==========================================

TOOL_REGISTRY = {
    "get_order_status": {
        "schema": GetOrderStatusInput,
        "handler": get_order_status,
        "description": "Retrieve the current status of an order.",
    },
    "get_product_details": {
        "schema": GetProductDetailsInput,
        "handler": get_product_details,
        "description": "Retrieve product details using a product ID.",
    },
}



def build_provider_tool_definitions() -> list[dict[str, Any]]:
    """
    Convert the internal tool registry into provider-style definitions.

    Python handlers remain private to the backend.
    """

    definitions = []

    for tool_name, tool_config in TOOL_REGISTRY.items():
        definitions.append({
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_config["description"],
                "parameters": (
                    tool_config["schema"].model_json_schema()
                ),
                "strict": True,
            },
        })

    return definitions


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Execute an approved tool after validating its arguments.

    This is a local learning executor.
    Authentication and authorization are not implemented here.
    """

    # 1. Check whether the requested tool is registered.
    registered_tool = TOOL_REGISTRY.get(tool_name)

    if registered_tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")

    # 2. Validate the argument container.
    if not isinstance(arguments, dict):
        raise TypeError("Tool arguments must be a dictionary.")

    # 3. Retrieve the input schema and handler.
    input_schema = registered_tool["schema"]
    handler = registered_tool["handler"]

    # 4. Validate arguments using Pydantic.
    validated_input = input_schema.model_validate(arguments)

    # 5. Execute only the registered handler.
    return handler(**validated_input.model_dump())



# Simulated database ownership records.
# In production, ownership must come from the database.
ORDER_OWNERS = {
    "ORD-10025": "USER-001",
    "ORD-10026": "USER-002",
}


def execute_order_status_for_user(
    authenticated_user_id: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate order input and authorize access using trusted backend identity.

    authenticated_user_id must come from backend authentication,
    never from LLM-generated arguments.
    """

    validated_input = GetOrderStatusInput.model_validate(arguments)
    order_id = validated_input.order_id

    owner_id = ORDER_OWNERS.get(order_id)

    if owner_id is None:
        return {
            "success": False,
            "error": {
                "code": "ORDER_NOT_FOUND",
                "message": "Order not found.",
            },
        }

    if owner_id != authenticated_user_id:
        return {
            "success": False,
            "error": {
                "code": "ACCESS_DENIED",
                "message": "You are not authorized to access this order.",
            },
        }

    return execute_tool("get_order_status", arguments)


def demonstrate_order_authorization() -> None:
    """Demonstrate authorized and unauthorized order access."""

    arguments = {"order_id": "ORD-10025"}

    print("\\n========== AUTHORIZED USER ==========")
    print(
        execute_order_status_for_user(
            authenticated_user_id="USER-001",
            arguments=arguments,
        )
    )

    print("\\n========== UNAUTHORIZED USER ==========")
    print(
        execute_order_status_for_user(
            authenticated_user_id="USER-999",
            arguments=arguments,
        )
    )

    print("\\n========== NONEXISTENT ORDER ==========")
    print(
        execute_order_status_for_user(
            authenticated_user_id="USER-001",
            arguments={"order_id": "ORD-99999"},
        )
    )



def execute_provider_tool_call(
    provider_call: dict[str, Any],
) -> dict[str, Any]:
    """Parse and execute one provider-style function call."""

    if not isinstance(provider_call, dict):
        raise TypeError("Provider tool call must be a dictionary.")

    call_id = provider_call.get("id")
    function = provider_call.get("function")

    if not isinstance(call_id, str) or not call_id:
        raise ValueError("Provider call must contain a valid ID.")

    if not isinstance(function, dict):
        raise ValueError("Provider call must contain a function object.")

    tool_name = function.get("name")
    raw_arguments = function.get("arguments")

    if not isinstance(tool_name, str) or not tool_name:
        raise ValueError("Function name is missing or invalid.")

    if not isinstance(raw_arguments, str):
        raise TypeError("Function arguments must be a JSON string.")

    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise ValueError("Function arguments contain invalid JSON.") from exc

    if not isinstance(arguments, dict):
        raise TypeError("Decoded function arguments must be a JSON object.")

    result = simulate_llm_tool_call({
        "name": tool_name,
        "arguments": arguments,
    })

    return {
        "tool_call_id": call_id,
        "tool_name": tool_name,
        "result": result,
    }

def execute_secure_provider_tool_call(
    authenticated_user_id: str,
    provider_call: dict[str, Any],
    user_approved: bool = False,
) -> dict[str, Any]:
    if not isinstance(provider_call, dict):
        raise TypeError("Provider call must be a dictionary.")

    call_id = provider_call.get("id")
    function = provider_call.get("function")

    if not isinstance(call_id, str) or not call_id:
        raise ValueError("Provider call must contain a valid ID.")

    if not isinstance(function, dict):
        raise ValueError("Provider call must contain function details.")

    tool_name = function.get("name")
    raw_arguments = function.get("arguments")

    if not isinstance(tool_name, str) or not tool_name:
        raise ValueError("Provider call must contain a tool name.")

    if not isinstance(raw_arguments, str):
        raise TypeError("Provider arguments must be a JSON string.")

    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise ValueError("Provider arguments contain invalid JSON.") from exc

    if not isinstance(arguments, dict):
        raise TypeError("Provider arguments must decode to an object.")

    result = execute_secure_tool_call(
        authenticated_user_id=authenticated_user_id,
        tool_name=tool_name,
        arguments=arguments,
        user_approved=user_approved,
    )

    return {
        "tool_call_id": call_id,
        "tool_name": tool_name,
        "result": result,
    }

def build_secure_provider_tool_result_message(
    secure_execution_result: dict[str, Any],
) -> dict[str, str]:
    if not isinstance(secure_execution_result, dict):
        raise TypeError("Execution result must be a dictionary.")

    call_id = secure_execution_result.get("tool_call_id")

    if not isinstance(call_id, str) or not call_id:
        raise ValueError("Execution result must contain a valid tool-call ID.")

    return build_provider_tool_result_message(
        secure_execution_result
    )

def simulate_secure_tool_calling_cycle(
    authenticated_user_id: str,
    user_message: str,
) -> dict[str, Any]:
    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError("User message cannot be empty.")

    tool_definitions = build_provider_tool_definitions()

    # Simulated provider response.
    provider_call = {
        "id": "call_cycle_secure_001",
        "type": "function",
        "function": {
            "name": "get_product_details",
            "arguments": '{"product_id": "PROD-101"}',
        },
    }

    execution_result = execute_secure_provider_tool_call(
        authenticated_user_id=authenticated_user_id,
        provider_call=provider_call,
    )

    tool_message = build_secure_provider_tool_result_message(
        execution_result
    )

    tool_result = execution_result["result"]

    if tool_result["success"]:
        product = tool_result["data"]

        final_answer = (
            f"{product['name']} costs ₹{product['price']} "
            f"and is currently {product['availability']}."
        )
    else:
        final_answer = (
            "I could not retrieve the requested product details."
        )

    return {
        "user_message": user_message,
        "tool_definitions": tool_definitions,
        "provider_call": provider_call,
        "execution_result": execution_result,
        "tool_message": tool_message,
        "assistant_final_answer": final_answer,
    }

def build_provider_tool_result_message(
    execution_result: dict[str, Any],
) -> dict[str, str]:
    """Format a backend tool result as a provider-style tool message."""

    call_id = execution_result.get("tool_call_id")
    result = execution_result.get("result")

    if not isinstance(call_id, str) or not call_id:
        raise ValueError("Execution result must contain a valid tool-call ID.")

    return {
        "role": "tool",
        "tool_call_id": call_id,
        "content": json.dumps(result),
    }


def execute_multiple_tools(
    tool_calls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Execute multiple tool calls sequentially with separate status fields."""

    results = []

    for index, tool_call in enumerate(tool_calls, start=1):
        try:
            result = simulate_llm_tool_call(tool_call)

            tool_success = None
            if isinstance(result, dict):
                business_status = result.get("success")
                if isinstance(business_status, bool):
                    tool_success = business_status

            results.append({
                "tool_call_number": index,
                "execution_success": True,
                "tool_success": tool_success,
                "result": result,
            })

        except ValidationError as exc:
            results.append({
                "tool_call_number": index,
                "execution_success": False,
                "tool_success": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "details": exc.errors(),
                },
            })

        except (ValueError, TypeError) as exc:
            results.append({
                "tool_call_number": index,
                "execution_success": False,
                "tool_success": None,
                "error": {
                    "code": "TOOL_CALL_ERROR",
                    "message": str(exc),
                },
            })

    return results


def demonstrate_multiple_tool_calls() -> None:
    """Demonstrate sequential execution of multiple tools."""

    tool_calls = [
        {
            "name": "get_order_status",
            "arguments": {"order_id": "ORD-10025"},
        },
        {
            "name": "get_product_details",
            "arguments": {"product_id": "PROD-101"},
        },
    ]

    print()
    print("========== MULTIPLE TOOL EXECUTION ==========")

    results = execute_multiple_tools(tool_calls)

    for result in results:
        print(result)


def simulate_complete_tool_calling_cycle(
    user_message: str,
) -> dict[str, Any]:
    """Demonstrate the complete simulated LLM tool-calling lifecycle."""

    if not isinstance(user_message, str) or not user_message.strip():
        raise ValueError("User message cannot be empty.")

    print("\n========== COMPLETE TOOL-CALLING CYCLE ==========")
    print("USER:", user_message)

    # Step 1: Backend prepares definitions for the provider.
    tool_definitions = build_provider_tool_definitions()
    print("\nSTEP 1: Provider received tool definitions")
    print([item["function"]["name"] for item in tool_definitions])

    # Step 2: Simulate the provider requesting a tool.
    provider_call = {
        "id": "call_cycle_001",
        "type": "function",
        "function": {
            "name": "get_product_details",
            "arguments": '{"product_id": "PROD-101"}',
        },
    }

    print("\nSTEP 2: Simulated provider requested a tool")
    print(provider_call)

    # Step 3: Backend executes the provider tool call.
    execution_result = execute_provider_tool_call(provider_call)

    print("\nSTEP 3: Backend executed the tool")
    print(execution_result)

    # Step 4: Backend formats the result for the provider.
    tool_message = build_provider_tool_result_message(execution_result)

    print("\nSTEP 4: Tool result sent back to provider")
    print(tool_message)

    # Step 5: Simulate the provider's final assistant response.
    tool_result = execution_result["result"]

    if tool_result.get("success"):
        product = tool_result["data"]
        final_answer = (
            f"{product['name']} costs ₹{product['price']} "
            f"and is currently {product['availability']}."
        )
    else:
        final_answer = "I could not retrieve the requested product details."

    print("\nSTEP 5: Final assistant response")
    print(final_answer)

    return {
        "user_message": user_message,
        "tool_call": provider_call,
        "execution_result": execution_result,
        "tool_message": tool_message,
        "final_answer": final_answer,
    }



def validate_tool_choice(
    tool_choice: str,
    requested_tool: str | None = None,
) -> bool:
    """Simulate basic tool-choice policy validation."""

    available_tools = set(TOOL_REGISTRY)

    if tool_choice == "auto":
        return True

    if tool_choice == "none":
        return False

    if tool_choice == "required":
        return True

    if tool_choice in available_tools:
        if requested_tool != tool_choice:
            return False
        return True

    raise ValueError(f"Unsupported tool choice: {tool_choice}")



def validate_tool_call_batch(
    tool_choice: str,
    requested_tools: list[str],
) -> dict[str, Any]:
    """Validate a complete batch against the selected tool-choice policy."""

    if not isinstance(requested_tools, list):
        raise TypeError("Requested tools must be a list.")

    available_tools = set(TOOL_REGISTRY)

    if any(
        not isinstance(name, str) or not name
        for name in requested_tools
    ):
        return {"allowed": False, "reason": "Invalid tool name."}

    if any(name not in available_tools for name in requested_tools):
        return {"allowed": False, "reason": "Unknown tool requested."}

    if tool_choice == "none":
        allowed = len(requested_tools) == 0
    elif tool_choice in ("auto", "required"):
        allowed = True
        if tool_choice == "required" and not requested_tools:
            return {
                "allowed": False,
                "reason": "At least one tool call is required.",
            }
    elif tool_choice in available_tools:
        allowed = (
            len(requested_tools) == 1
            and requested_tools[0] == tool_choice
        )
    else:
        raise ValueError(f"Unsupported tool choice: {tool_choice}")

    return {
        "allowed": allowed,
        "requested_tools": requested_tools,
        "reason": (
            "Tool calls accepted."
            if allowed
            else "Requested calls violate tool-choice policy."
        ),
    }



TOOL_SECURITY_POLICIES = {
    "get_order_status": {
        "requires_approval": False,
        "permission": "orders:read",
    },
    "get_product_details": {
        "requires_approval": False,
        "permission": "products:read",
    },
    "cancel_order": {
        "requires_approval": True,
        "permission": "orders:cancel",
    },
}


def get_tool_security_policy(tool_name: str) -> dict[str, Any]:
    """Return security policy for an allowlisted tool."""

    policy = TOOL_SECURITY_POLICIES.get(tool_name)

    if policy is None:
        raise ValueError(f"No security policy for tool: {tool_name}")

    return policy

USER_PERMISSIONS = {
    "USER-001": {
        "orders:read",
        "products:read",
    },
    "USER-002": {
        "products:read",
    },
    "ADMIN-001": {
        "orders:read",
        "products:read",
        "orders:cancel",
    },
}


def check_tool_permission(
    authenticated_user_id: str,
    tool_name: str,
) -> bool:
    policy = get_tool_security_policy(tool_name)
    required_permission = policy["permission"]

    user_permissions = USER_PERMISSIONS.get(
        authenticated_user_id,
        set(),
    )

    return required_permission in user_permissions

def check_tool_approval(
    tool_name: str,
    user_approved: bool = False,
) -> bool:
    policy = get_tool_security_policy(tool_name)

    if not policy["requires_approval"]:
        return True

    return user_approved

SECURITY_AUDIT_LOG: list[dict[str, Any]] = []


def record_security_audit_event(
    authenticated_user_id: str,
    tool_name: str,
    permission_granted: bool,
    approval_granted: bool,
) -> dict[str, Any]:
    event = {
        "user_id": authenticated_user_id,
        "tool_name": tool_name,
        "permission_granted": permission_granted,
        "approval_granted": approval_granted,
        "execution_allowed": (
            permission_granted and approval_granted
        ),
        "resource_authorized": None,
        "execution_completed": False,
    }

    SECURITY_AUDIT_LOG.append(event)

    return event

def validate_tool_security(
    authenticated_user_id: str,
    tool_name: str,
    user_approved: bool = False,
) -> dict[str, Any]:
    permission_granted = check_tool_permission(
        authenticated_user_id,
        tool_name,
    )

    approval_granted = check_tool_approval(
        tool_name,
        user_approved,
    )

    audit_event = record_security_audit_event(
        authenticated_user_id=authenticated_user_id,
        tool_name=tool_name,
        permission_granted=permission_granted,
        approval_granted=approval_granted,
    )

    if not permission_granted:
        reason = "Permission denied."

    elif not approval_granted:
        reason = "User approval required."

    else:
        reason = "Security validation passed."

    return {
        "allowed": audit_event["execution_allowed"],
        "reason": reason,
        "audit_event": audit_event,
    }

def execute_tool_with_security(
    authenticated_user_id: str,
    tool_name: str,
    arguments: dict[str, Any],
    user_approved: bool = False,
) -> dict[str, Any]:
    security_result = validate_tool_security(
        authenticated_user_id=authenticated_user_id,
        tool_name=tool_name,
        user_approved=user_approved,
    )

    if not security_result["allowed"]:
        return {
            "success": False,
            "error": {
                "code": "SECURITY_DENIED",
                "message": security_result["reason"],
            },
        }

    result = execute_tool(tool_name, arguments)

    return {
        "success": True,
        "data": result,
    }

def execute_secure_tool_call(
    authenticated_user_id: str,
    tool_name: str,
    arguments: dict[str, Any],
    user_approved: bool = False,
) -> dict[str, Any]:
    if tool_name not in TOOL_REGISTRY:
        return {
            "success": False,
            "error": {
                "code": "UNKNOWN_TOOL",
                "message": f"Unknown tool: {tool_name}",
            },
        }

    try:
        validated_input = TOOL_REGISTRY[tool_name]["schema"].model_validate(
            arguments
        )

        security_result = validate_tool_security(
            authenticated_user_id=authenticated_user_id,
            tool_name=tool_name,
            user_approved=user_approved,
        )

        if not security_result["allowed"]:
            return {
                "success": False,
                "error": {
                    "code": "SECURITY_DENIED",
                    "message": security_result["reason"],
                },
            }

        validated_arguments = validated_input.model_dump()

        if tool_name == "get_order_status":
            result = execute_order_status_for_user(
                authenticated_user_id,
                validated_arguments,
            )

            resource_authorized = result.get("success") is True

        else:
            resource_authorized = True

            result = TOOL_REGISTRY[tool_name]["handler"](
                **validated_arguments
            )

        audit_event = security_result["audit_event"]
        audit_event["resource_authorized"] = resource_authorized
        audit_event["execution_completed"] = (
            result.get("success") is True
            if isinstance(result, dict)
            else False
        )

        return result

    except ValidationError as exc:
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "details": exc.errors(),
            },
        }

    except (TypeError, ValueError) as exc:
        return {
            "success": False,
            "error": {
                "code": "EXECUTION_ERROR",
                "message": str(exc),
            },
        }
    
def demonstrate_tool_executor() -> None:
    """Demonstrate execution of multiple registered tools."""

    print("\n========== ORDER TOOL ==========")
    print(
        execute_tool(
            "get_order_status",
            {"order_id": "ORD-10025"},
        )
    )

    print("\n========== PRODUCT TOOL ==========")
    print(
        execute_tool(
            "get_product_details",
            {"product_id": "PROD-101"},
        )
    )

    print("\n========== UNKNOWN TOOL TEST ==========")
    try:
        execute_tool("delete_customer", {})
    except ValueError as exc:
        print("REJECTED:", exc)

    print("\n========== INVALID ORDER INPUT ==========")
    try:
        execute_tool(
            "get_order_status",
            {"order_id": "INVALID"},
        )
    except ValidationError as exc:
        print("REJECTED:", exc)

    print("\n========== INVALID PRODUCT INPUT ==========")
    try:
        execute_tool(
            "get_product_details",
            {"product_id": "INVALID"},
        )
    except ValidationError as exc:
        print("REJECTED:", exc)

    print("\n========== UNKNOWN PRODUCT TEST ==========")
    print(
        execute_tool(
            "get_product_details",
            {"product_id": "PROD-999"},
        )
    )


def simulate_llm_tool_call(tool_call: dict[str, Any]) -> dict[str, Any]:
    """
    Simulate a tool-call request returned by an LLM.

    This is a local simulation, not a real provider API response.
    """

    if not isinstance(tool_call, dict):
        raise TypeError("Tool call must be a dictionary.")

    tool_name = tool_call.get("name")
    arguments = tool_call.get("arguments")

    if not isinstance(tool_name, str) or not tool_name:
        raise ValueError("Tool call must contain a valid tool name.")

    if not isinstance(arguments, dict):
        raise TypeError("Tool call arguments must be a dictionary.")

    return execute_tool(tool_name, arguments)




def demonstrate_llm_tool_call() -> None:
    """Demonstrate valid and malformed simulated LLM requests."""

    test_requests = [
        {
            "name": "Valid request",
            "request": {
                "name": "get_product_details",
                "arguments": {"product_id": "PROD-101"},
            },
        },
        {
            "name": "Missing tool name",
            "request": {"arguments": {"product_id": "PROD-101"}},
        },
        {
            "name": "Unknown tool",
            "request": {
                "name": "delete_customer",
                "arguments": {},
            },
        },
        {
            "name": "Missing arguments",
            "request": {"name": "get_product_details"},
        },
        {
            "name": "Arguments are not a dictionary",
            "request": {
                "name": "get_product_details",
                "arguments": ["PROD-101"],
            },
        },
        {
            "name": "Invalid product ID",
            "request": {
                "name": "get_product_details",
                "arguments": {"product_id": "INVALID"},
            },
        },
    ]

    for test_case in test_requests:
        print()
        print(f"========== {test_case['name']} ==========")

        try:
            result = simulate_llm_tool_call(test_case["request"])
            print("RESULT:", result)
        except ValidationError as exc:
            print("VALIDATION REJECTED:", exc.errors())
        except (ValueError, TypeError) as exc:
            print("REQUEST REJECTED:", str(exc))


if __name__ == "__main__":
    print("\n========== BASIC TOOL EXECUTION ==========")
    print(get_order_status("ORD-10025"))

    demonstrate_validation()
    demonstrate_tool_executor()
    demonstrate_order_authorization()
    demonstrate_multiple_tool_calls()
    demonstrate_llm_tool_call()
