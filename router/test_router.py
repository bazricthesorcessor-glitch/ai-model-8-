"""
Router tests - verify service bus behavior and message dispatch.
Tests the new service registry + dispatcher pattern.
"""

from router import Message, Response, dispatch, send_to_service, register_service


def fake_executor(message: Message) -> Response:
    """Fake executor service handler."""
    return Response(
        source="executor",
        success=True,
        result={"received": message.payload}
    )


def fake_query_maker(message: Message) -> Response:
    """Fake query maker service handler."""
    return Response(
        source="query_maker",
        success=True,
        result={"queries": ["query1", "query2"]}
    )


def test_dispatch_registered_service():
    """Test dispatching message to a registered service."""
    # Clear and register fresh
    register_service("executor", fake_executor)

    msg = Message(
        source="scout",
        target="executor",
        action="dispatch_tool",
        payload={"tool": "screenshot"}
    )

    response = dispatch(msg)

    assert response.success is True
    assert response.source == "executor"
    assert response.result["received"]["tool"] == "screenshot"
    print("✓ Dispatch registered service")


def test_dispatch_unknown_service():
    """Test error when dispatching to unregistered service."""
    msg = Message(
        source="scout",
        target="nonexistent_service",
        action="dispatch_tool",
        payload={}
    )

    response = dispatch(msg)

    assert response.success is False
    assert response.error is not None
    assert "nonexistent_service" in response.error or "not found" in response.error.lower()
    print("✓ Unknown service error")


def test_multiple_registered_services():
    """Test registering and dispatching to multiple services."""
    register_service("executor", fake_executor)
    register_service("query_maker", fake_query_maker)

    # Dispatch to executor
    msg1 = Message(
        source="scout",
        target="executor",
        action="dispatch_tool",
        payload={"cmd": "ls"}
    )
    response1 = dispatch(msg1)
    assert response1.source == "executor"
    assert response1.success is True

    # Dispatch to query_maker
    msg2 = Message(
        source="scout",
        target="query_maker",
        action="run_query_maker",
        payload={"intent": "list files"}
    )
    response2 = dispatch(msg2)
    assert response2.source == "query_maker"
    assert response2.success is True
    print("✓ Multiple registered services")


def test_message_fields_preserved():
    """Test that message fields are preserved through dispatch."""
    def capture_handler(message: Message) -> Response:
        # Return the full message to test field preservation
        return Response(
            source="executor",
            success=True,
            result={
                "payload": message.payload,
                "context": message.context,
                "action": message.action
            }
        )

    register_service("executor", capture_handler)

    msg = Message(
        source="scout",
        target="executor",
        action="dispatch_tool",
        payload={"key": "value"},
        context={"prev_result": "data"}
    )

    response = dispatch(msg)

    # Handler preserves all message fields
    assert response.result["payload"]["key"] == "value"
    assert response.result["context"]["prev_result"] == "data"
    assert response.result["action"] == "dispatch_tool"
    print("✓ Message fields preserved")


def test_handler_exception_handling():
    """Test that service exceptions are caught and returned as errors."""
    def failing_handler(message: Message) -> Response:
        raise ValueError("Handler failed")

    register_service("failing_service", failing_handler)

    msg = Message(
        source="scout",
        target="failing_service",
        action="dispatch_tool",
        payload={}
    )

    response = dispatch(msg)

    assert response.success is False
    assert response.error is not None
    assert "failed" in response.error.lower() or "exception" in response.error.lower()
    print("✓ Handler exception handling")


def test_service_returns_non_response():
    """Test that non-Response returns are wrapped."""
    def raw_handler(message: Message) -> dict:
        return {"data": "raw"}

    register_service("raw_service", raw_handler)

    msg = Message(
        source="scout",
        target="raw_service",
        action="dispatch_tool",
        payload={}
    )

    response = dispatch(msg)

    # Should be wrapped in Response
    assert isinstance(response, Response)
    print("✓ Non-Response wrapping")


def run_all_tests():
    """Run all router tests."""
    print("\n" + "="*50)
    print("Router Service Bus Tests")
    print("="*50 + "\n")

    test_dispatch_registered_service()
    test_dispatch_unknown_service()
    test_multiple_registered_services()
    test_message_fields_preserved()
    test_handler_exception_handling()
    test_service_returns_non_response()

    print("\n" + "="*50)
    print("✓ All tests passed")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()
