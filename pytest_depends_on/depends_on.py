import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureRequest
from _pytest.python import Function
from custom_python_logger import get_logger

from pytest_depends_on.consts.status import Status

test_results = {}

logger = get_logger("pytest_depends_on")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Function) -> None:
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    test_name = item.nodeid.split(".py::")[-1]
    if hasattr(report, "wasxfail"):
        if report.skipped:
            test_results[test_name] = Status.XFAILED
        elif report.passed:
            test_results[test_name] = Status.XPASS
    else:
        test_results[test_name] = report.outcome


@pytest.fixture(autouse=True)
def check_dependency(request: FixtureRequest) -> None:
    if marker := request.node.get_closest_marker("depends_on"):
        parent_result_expected = marker.kwargs.get("status", Status.PASSED)
        allowed_parent_not_run = marker.kwargs.get("allowed_not_run", False)
        for parent_test in marker.kwargs["tests"]:
            if isinstance(parent_test, dict):
                parent_test_name = parent_test.get("name")
                parent_result_expected = parent_test.get("status", parent_result_expected)
                allowed_parent_not_run = parent_test.get("allowed_not_run", allowed_parent_not_run)
            else:
                parent_test_name = parent_test

            parent_result = test_results.get(parent_test_name)

            if allowed_parent_not_run and parent_result is None:
                continue
            if not parent_result:
                pytest.skip(f"Test skipped: Dependency '{parent_test_name}' has not run yet.")
            if parent_result != parent_result_expected:
                pytest.skip(f"Test skipped: Dependency '{parent_test_name}' did not pass (status: {parent_result}).")


def pytest_configure(config: Config) -> None:
    config.addinivalue_line("markers", "depends_on(name): mark test as dependent on another test")
