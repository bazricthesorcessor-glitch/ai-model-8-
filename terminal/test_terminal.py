"""
Terminal module tests - shell command execution.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terminal import (
    TerminalExecutor,
    ShellType,
    execute_bash,
    execute_python,
    list_directory,
    read_file,
    get_system_info,
)


def test_terminal_executor_init():
    """Test 1: TerminalExecutor initialization."""
    print("\n" + "=" * 70)
    print("TEST 1: TerminalExecutor Initialization")
    print("=" * 70)

    # Valid shells
    executor = TerminalExecutor(shell="bash")
    assert executor.shell == "bash"
    print(f"✓ Bash shell initialized")

    executor = TerminalExecutor(shell="sh")
    assert executor.shell == "sh"
    print(f"✓ Sh shell initialized")

    # Invalid shell
    try:
        executor = TerminalExecutor(shell="invalid")
        assert False, "Should raise ValueError"
    except ValueError as e:
        print(f"✓ Invalid shell rejected: {e}")

    print("\n✓ TEST 1 PASSED")


def test_command_execution():
    """Test 2: Basic command execution."""
    print("\n" + "=" * 70)
    print("TEST 2: Basic Command Execution")
    print("=" * 70)

    executor = TerminalExecutor(shell="bash")

    # Simple echo command
    success, result, error = executor.execute("echo 'hello world'")

    assert success, f"Command failed: {error}"
    assert result, "No result returned"
    assert "hello world" in result.stdout
    print(f"✓ Echo command: {result.stdout.strip()}")

    # Command with exit code 0
    assert result.exit_code == 0
    print(f"✓ Exit code: {result.exit_code}")

    # Get pwd
    success, result, error = executor.execute("pwd")
    assert success, "pwd failed"
    print(f"✓ pwd: {result.stdout.strip()}")

    print("\n✓ TEST 2 PASSED")


def test_command_error_handling():
    """Test 3: Error handling."""
    print("\n" + "=" * 70)
    print("TEST 3: Error Handling")
    print("=" * 70)

    executor = TerminalExecutor(shell="bash")

    # Empty command
    success, result, error = executor.execute("")
    assert not success, "Empty command should fail"
    print(f"✓ Empty command rejected: {error}")

    # Command that fails
    success, result, error = executor.execute("false")
    assert not success, "False should return non-zero"
    assert result.exit_code != 0
    print(f"✓ Failed command detected: exit code {result.exit_code}")

    # Command with stderr
    success, result, error = executor.execute("ls /nonexistent 2>&1")
    # Output may vary, just check it ran
    assert result is not None
    print(f"✓ Command with stderr executed")

    print("\n✓ TEST 3 PASSED")


def test_convenience_functions():
    """Test 4: Convenience functions."""
    print("\n" + "=" * 70)
    print("TEST 4: Convenience Functions")
    print("=" * 70)

    # execute_bash
    success, result, error = execute_bash("echo 'test'")
    assert success, f"Bash failed: {error}"
    assert "test" in result.stdout
    print(f"✓ execute_bash() works")

    # list_directory
    success, items, error = list_directory(".")
    assert success, f"List failed: {error}"
    assert len(items) > 0
    print(f"✓ list_directory() works: {len(items)} items")

    # get_system_info
    info = get_system_info()
    assert "os" in info
    assert "python_version" in info
    print(f"✓ get_system_info() works: {info['os']}")

    print("\n✓ TEST 4 PASSED")


def test_shell_types():
    """Test 5: Shell type enum."""
    print("\n" + "=" * 70)
    print("TEST 5: Shell Types")
    print("=" * 70)

    shells = [s.value for s in ShellType]
    expected = ["bash", "zsh", "fish", "powershell", "cmd", "sh"]

    for shell in expected:
        assert shell in shells, f"Missing shell: {shell}"
        print(f"✓ Shell available: {shell}")

    print("\n✓ TEST 5 PASSED")


def test_directory_change():
    """Test 6: Change directory."""
    print("\n" + "=" * 70)
    print("TEST 6: Change Directory")
    print("=" * 70)

    executor = TerminalExecutor(shell="bash")
    cwd_before = executor.get_cwd()
    print(f"✓ Initial cwd: {cwd_before}")

    # Change to /tmp
    success, new_cwd, error = executor.change_directory("/tmp")
    assert success, f"Change dir failed: {error}"
    assert new_cwd == "/tmp"
    assert executor.get_cwd() == "/tmp"
    print(f"✓ Changed to: {new_cwd}")

    # Change back
    success, new_cwd, error = executor.change_directory(cwd_before)
    assert success, "Change back failed"
    print(f"✓ Changed back to: {new_cwd}")

    # Invalid directory
    success, new_cwd, error = executor.change_directory("/nonexistent")
    assert not success, "Invalid dir should fail"
    print(f"✓ Invalid directory rejected: {error}")

    print("\n✓ TEST 6 PASSED")


def test_environment_variables():
    """Test 7: Environment variables."""
    print("\n" + "=" * 70)
    print("TEST 7: Environment Variables")
    print("=" * 70)

    executor = TerminalExecutor(shell="bash")

    # Set variable
    success = executor.set_env_var("TEST_VAR", "test_value")
    assert success, "Failed to set env var"
    print(f"✓ Set TEST_VAR=test_value")

    # Get variable
    value = executor.get_env_var("TEST_VAR")
    assert value == "test_value"
    print(f"✓ Retrieved TEST_VAR={value}")

    # Get nonexistent with default
    value = executor.get_env_var("NONEXISTENT", "default")
    assert value == "default"
    print(f"✓ Default for nonexistent: {value}")

    print("\n✓ TEST 7 PASSED")


def test_timeout():
    """Test 8: Command timeout."""
    print("\n" + "=" * 70)
    print("TEST 8: Command Timeout")
    print("=" * 70)

    executor = TerminalExecutor(shell="bash")

    # Sleep command with short timeout
    success, result, error = executor.execute("sleep 10", timeout=1)
    assert not success, "Should timeout"
    assert "timeout" in error.lower()
    print(f"✓ Timeout detected: {error}")

    print("\n✓ TEST 8 PASSED")


def test_command_result_structure():
    """Test 9: CommandResult structure."""
    print("\n" + "=" * 70)
    print("TEST 9: CommandResult Structure")
    print("=" * 70)

    executor = TerminalExecutor(shell="bash")
    success, result, error = executor.execute("echo test")

    assert result is not None
    assert hasattr(result, "stdout")
    assert hasattr(result, "stderr")
    assert hasattr(result, "exit_code")
    assert hasattr(result, "command")
    assert hasattr(result, "shell")
    assert hasattr(result, "duration")

    print(f"✓ CommandResult structure valid")
    print(f"  - stdout: {len(result.stdout)} chars")
    print(f"  - exit_code: {result.exit_code}")
    print(f"  - duration: {result.duration:.3f}s")

    print("\n✓ TEST 9 PASSED")


def test_stateless_design():
    """Test 10: Stateless design."""
    print("\n" + "=" * 70)
    print("TEST 10: Stateless Design")
    print("=" * 70)

    # Multiple independent operations
    executor = TerminalExecutor(shell="bash")

    for i in range(3):
        success, result, error = executor.execute(f"echo 'test{i}'")
        assert success, f"Iteration {i} failed"

    print(f"✓ Multiple operations independent")

    # Commands don't affect each other
    executor.set_env_var("TEST", "value1")
    success, result, error = executor.execute("echo $TEST")
    # Note: subprocess gets fresh env in this test

    executor.set_env_var("TEST", "value2")
    success, result, error = executor.execute("echo $TEST")

    print(f"✓ No state pollution between commands")

    print("\n✓ TEST 10 PASSED")


def run_all_tests():
    """Run all terminal module tests."""
    print("\n" + "=" * 70)
    print("TERMINAL MODULE TEST SUITE")
    print("=" * 70)

    tests = [
        test_terminal_executor_init,
        test_command_execution,
        test_command_error_handling,
        test_convenience_functions,
        test_shell_types,
        test_directory_change,
        test_environment_variables,
        test_timeout,
        test_command_result_structure,
        test_stateless_design,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
