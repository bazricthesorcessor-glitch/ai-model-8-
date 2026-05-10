"""
Tool layer tests - verify all tools work correctly.
Tests tool interface, validation, execution, and registry.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import (
    REGISTRY,
    ToolSchemas,
    Tool,
    ClickElementTool,
    TypeTextTool,
    NavigateTool,
    ReadTextTool,
    MouseClickTool,
    ExecuteCommandTool,
)


def test_tool_registry():
    """Test 1: Tool registry works correctly."""
    print("\n" + "=" * 70)
    print("TEST 1: Tool Registry")
    print("=" * 70)

    # Check tools are registered
    tools = REGISTRY.list()
    print(f"\nRegistered tools: {len(tools)}")

    # Show tools by platform
    for platform in REGISTRY.get_platforms():
        platform_tools = REGISTRY.list_by_platform(platform)
        print(f"  {platform}: {len(platform_tools)} tools")
        for name in sorted(platform_tools.keys()):
            print(f"    - {name}")

    # Check registry info
    info = REGISTRY.get_info()
    print(f"\nTotal tools: {info['total_tools']}")
    print(f"Total platforms: {len(info['platforms'])}")

    assert info["total_tools"] == 15, "Should have 15 tools"
    assert len(info["platforms"]) == 5, "Should have 5 platforms"
    print("\n✓ TEST 1 PASSED")


def test_tool_interface():
    """Test 2: All tools follow consistent interface."""
    print("\n" + "=" * 70)
    print("TEST 2: Tool Interface Consistency")
    print("=" * 70)

    tools = REGISTRY.list()

    print(f"\nValidating {len(tools)} tools...")
    for tool_name, tool in tools.items():
        # Check methods exist
        assert hasattr(tool, 'validate_input'), f"{tool_name} missing validate_input"
        assert hasattr(tool, 'execute'), f"{tool_name} missing execute"
        assert hasattr(tool, 'run'), f"{tool_name} missing run"

        # Check attributes
        assert tool.name == tool_name, f"{tool_name} name mismatch"
        assert tool.platform, f"{tool_name} missing platform"
        assert tool.description, f"{tool_name} missing description"

        print(f"  ✓ {tool_name:20} [{tool.platform:8}]")

    print("\n✓ TEST 2 PASSED")


def test_tool_input_validation():
    """Test 3: Input validation works."""
    print("\n" + "=" * 70)
    print("TEST 3: Tool Input Validation")
    print("=" * 70)

    test_cases = [
        # Valid inputs
        ("click_element", {"selector": "#btn"}, True),
        ("type_text", {"text": "hello"}, True),
        ("navigate", {"url": "https://example.com"}, True),
        ("mouse_click", {"x": 100, "y": 200}, True),
        ("execute_command", {"command": "ls"}, True),
        # Invalid inputs (missing required)
        ("click_element", {}, False),
        ("type_text", {}, False),
        ("mouse_click", {"x": 100}, False),
        # Invalid types
        ("click_element", {"selector": 123}, False),
        ("mouse_click", {"x": "100", "y": 200}, False),
    ]

    passed = 0
    failed = 0

    for tool_name, data, should_pass in test_cases:
        is_valid, error = ToolSchemas.validate(tool_name, data)

        if is_valid == should_pass:
            status = "✓"
            passed += 1
        else:
            status = "✗"
            failed += 1

        expected = "✓ VALID" if should_pass else "✗ INVALID"
        actual = "✓ VALID" if is_valid else "✗ INVALID"
        match = "✓" if is_valid == should_pass else "✗"

        print(f"  {match} {tool_name:20} {str(data):30} → {actual}")

    print(f"\nValidation tests: {passed} passed, {failed} failed")
    assert failed == 0, "All validation tests should pass"
    print("\n✓ TEST 3 PASSED")


def test_tool_execution():
    """Test 4: Tools execute and return standard results."""
    print("\n" + "=" * 70)
    print("TEST 4: Tool Execution")
    print("=" * 70)

    # Test different tool executions
    test_executions = [
        ("click_element", {"selector": "#button"}),
        ("type_text", {"text": "test input"}),
        ("navigate", {"url": "https://example.com"}),
        ("read_text", {"region": (0, 0, 800, 600)}),
        ("mouse_click", {"x": 100, "y": 200}),
        ("screenshot", {}),
        ("execute_command", {"command": "echo 'hello'"}),
    ]

    for tool_name, input_data in test_executions:
        tool = REGISTRY.get(tool_name)
        assert tool, f"Tool {tool_name} not found"

        # Execute tool
        result = tool.run(input_data)

        # Validate result structure
        assert isinstance(result, dict), "Result must be dict"
        assert "success" in result, "Result missing 'success'"
        assert "tool" in result, "Result missing 'tool'"
        assert "duration_ms" in result, "Result missing 'duration_ms'"
        assert "result" in result, "Result missing 'result'"
        assert "metadata" in result, "Result missing 'metadata'"

        # Check result values
        assert isinstance(result["success"], bool), "success must be bool"
        assert result["tool"] == tool_name, "tool name mismatch"
        assert isinstance(result["duration_ms"], float), "duration_ms must be float"
        assert result["duration_ms"] >= 0, "duration_ms must be positive"

        print(f"  ✓ {tool_name:20} → success={result['success']}, duration={result['duration_ms']:.2f}ms")

    print("\n✓ TEST 4 PASSED")


def test_tool_error_handling():
    """Test 5: Tools handle errors gracefully."""
    print("\n" + "=" * 70)
    print("TEST 5: Tool Error Handling")
    print("=" * 70)

    # Test invalid inputs
    test_cases = [
        ("click_element", {}),  # Missing required field
        ("type_text", {"text": 123}),  # Wrong type
        ("mouse_click", {"x": "invalid", "y": 200}),  # Wrong type
    ]

    for tool_name, invalid_data in test_cases:
        tool = REGISTRY.get(tool_name)

        # Execute with invalid input
        result = tool.run(invalid_data)

        # Should return error result
        assert result["success"] == False, f"{tool_name} should fail with invalid input"
        assert result["error"], f"{tool_name} should have error message"
        assert "duration_ms" in result, "Even errors should have timing"

        print(f"  ✓ {tool_name:20} → error: {result['error'][:50]}...")

    print("\n✓ TEST 5 PASSED")


def test_tool_schemas():
    """Test 6: Schema validation is comprehensive."""
    print("\n" + "=" * 70)
    print("TEST 6: Tool Schemas")
    print("=" * 70)

    schemas = ToolSchemas.list_schemas()
    print(f"\nTool schemas: {len(schemas)}")

    for tool_name, schema in schemas.items():
        required = len(schema.get("required", []))
        optional = len(schema.get("optional", []))
        total = required + optional
        print(f"  {tool_name:20} → {required} required, {optional} optional")

    assert len(schemas) == 15, "Should have 15 schemas"
    print("\n✓ TEST 6 PASSED")


def test_tool_metadata():
    """Test 7: Tool metadata is accessible."""
    print("\n" + "=" * 70)
    print("TEST 7: Tool Metadata")
    print("=" * 70)

    # Get metadata for all tools
    metadata = REGISTRY.get_all_metadata()
    print(f"\nMetadata for {len(metadata)} tools:")

    for tool_name, meta in sorted(metadata.items()):
        print(f"  {meta['name']:20} [{meta['platform']:8}] {meta['description'][:40]}")

    assert len(metadata) == 15, "Should have metadata for 15 tools"
    print("\n✓ TEST 7 PASSED")


def run_all_tests():
    """Run all tool tests."""
    print("\n" + "=" * 70)
    print("TOOLS LAYER TEST SUITE")
    print("=" * 70)
    print("\nTesting:")
    print("  1. Tool registry and discovery")
    print("  2. Tool interface consistency")
    print("  3. Input validation")
    print("  4. Tool execution")
    print("  5. Error handling")
    print("  6. Schemas")
    print("  7. Metadata")

    try:
        test_tool_registry()
        test_tool_interface()
        test_tool_input_validation()
        test_tool_execution()
        test_tool_error_handling()
        test_tool_schemas()
        test_tool_metadata()

        print("\n" + "=" * 70)
        print("✓ ALL TOOL TESTS PASSED")
        print("=" * 70)
        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
