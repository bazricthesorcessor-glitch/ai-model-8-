"""
Router tests - verify routing behavior without decision logic.
Tests that routing is purely config-based and deterministic.
"""

from .message import Message, Response
from .advanced_router import AdvancedRouter


# Mock handlers for testing
def mock_brain_handler(message: Message) -> Response:
    """Mock brain handler."""
    return Response(
        success=True,
        action=message.action,
        data={"intent": "test", "input": message.data.get("input")}
    )


def mock_executor_handler(message: Message) -> Response:
    """Mock executor handler."""
    return Response(
        success=True,
        action=message.action,
        data={"executed": True, "command": message.data.get("command")}
    )


def mock_state_handler(message: Message) -> Response:
    """Mock state handler."""
    return Response(
        success=True,
        action=message.action,
        data={"state_updated": True}
    )


# Test routing table (pure config, no logic)
TEST_ROUTING_TABLE = {
    "decide": {
        "cli": mock_brain_handler,
        "gui": mock_brain_handler,
        "*": mock_brain_handler,
    },
    "execute": {
        "cli": mock_executor_handler,
        "gui": mock_executor_handler,
    },
    "record_state": {
        "*": mock_state_handler,
    },
}


def test_exact_platform_match():
    """Test routing to exact platform match."""
    router = AdvancedRouter(TEST_ROUTING_TABLE)
    
    msg = Message(
        action="decide",
        platform="cli",
        mode="visible",
        data={"input": "hello"}
    )
    
    response = router.route(msg)
    
    assert response.success == True
    assert response.action == "decide"
    assert response.data["intent"] == "test"
    print("✓ Exact platform match")


def test_wildcard_fallback():
    """Test routing to wildcard when exact platform not found."""
    router = AdvancedRouter(TEST_ROUTING_TABLE)
    
    msg = Message(
        action="decide",
        platform="web",  # Not in decide routes, uses *
        mode="visible",
        data={"input": "hello"}
    )
    
    response = router.route(msg)
    
    assert response.success == True
    assert response.action == "decide"
    print("✓ Wildcard fallback")


def test_unknown_action():
    """Test error handling for unknown action."""
    router = AdvancedRouter(TEST_ROUTING_TABLE)
    
    msg = Message(
        action="unknown_action",  # Not in routing table
        platform="cli",
        mode="visible",
        data={}
    )
    
    response = router.route(msg)
    
    assert response.success == False
    assert "No route" in response.error
    print("✓ Unknown action error handling")


def test_unknown_platform():
    """Test error handling for unknown platform."""
    router = AdvancedRouter(TEST_ROUTING_TABLE)
    
    msg = Message(
        action="execute",  # Exists, but platform not found
        platform="unknown",  # Not in execute routes, no wildcard
        mode="visible",
        data={}
    )
    
    response = router.route(msg)
    
    assert response.success == False
    assert "No route" in response.error
    print("✓ Unknown platform error handling")


def test_message_unmodified():
    """Test that message is passed unmodified to handler."""
    
    captured_message = None
    
    def capture_handler(message: Message) -> Response:
        nonlocal captured_message
        captured_message = message
        return Response(success=True, action="test", data={})
    
    router = AdvancedRouter({
        "test_action": {
            "test_platform": capture_handler
        }
    })
    
    original_msg = Message(
        action="test_action",
        platform="test_platform",
        mode="visible",
        data={"key": "value"},
        context={"prev": "data"}
    )
    
    router.route(original_msg)
    
    assert captured_message.data == original_msg.data
    assert captured_message.context == original_msg.context
    print("✓ Message unmodified")


def test_stats_tracking():
    """Test that router tracks statistics."""
    router = AdvancedRouter(TEST_ROUTING_TABLE)
    
    # Route several messages
    for i in range(3):
        msg = Message(
            action="decide",
            platform="cli",
            mode="visible",
            data={}
        )
        router.route(msg)
    
    # Route one unknown
    msg = Message(
        action="unknown",
        platform="cli",
        mode="visible",
        data={}
    )
    router.route(msg)
    
    stats = router.get_stats()
    
    assert stats["total_routed"] == 4
    assert stats["routed_by_action"]["decide"] == 3
    assert len(stats["errors"]) == 1
    print("✓ Stats tracking")


def test_routing_table_inspection():
    """Test that routing table can be inspected."""
    router = AdvancedRouter(TEST_ROUTING_TABLE)
    
    table = router.get_routing_table()
    
    assert "decide" in table
    assert "cli" in table["decide"]
    assert "execute" in table
    print("✓ Routing table inspection")


def test_add_route_dynamically():
    """Test adding routes at runtime."""
    router = AdvancedRouter(TEST_ROUTING_TABLE)
    
    def new_handler(message: Message) -> Response:
        return Response(success=True, action="custom", data={})
    
    router.add_route("custom_action", "cli", new_handler)
    
    msg = Message(
        action="custom_action",
        platform="cli",
        mode="visible",
        data={}
    )
    
    response = router.route(msg)
    
    assert response.success == True
    assert response.action == "custom"
    print("✓ Dynamic route addition")


def run_all_tests():
    """Run all router tests."""
    print("\n" + "="*50)
    print("Advanced Router Tests")
    print("="*50 + "\n")
    
    test_exact_platform_match()
    test_wildcard_fallback()
    test_unknown_action()
    test_unknown_platform()
    test_message_unmodified()
    test_stats_tracking()
    test_routing_table_inspection()
    test_add_route_dynamically()
    
    print("\n" + "="*50)
    print("✓ All tests passed")
    print("="*50 + "\n")


if __name__ == "__main__":
    run_all_tests()
