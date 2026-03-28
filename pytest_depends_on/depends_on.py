import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureRequest
from _pytest.python import Function
from custom_python_logger import get_logger

from pytest_depends_on.consts.status import Status

test_results: dict[str, str] = {}

logger = get_logger("pytest_depends_on")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--depends-on",
        action="store_true",
        default=False,
        help="Enable pytest-depends-on dependency tracking and skip behaviour.",
    )
    parser.addoption(
        "--depends-on-reorder",
        action="store_true",
        default=False,
        help="Reorder collected tests so parents always run before dependents. Requires --depends-on.",
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: Function) -> None:
    outcome = yield
    if not item.config.getoption("--depends-on"):
        return

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
    if not request.config.getoption("--depends-on"):
        return

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


def _extract_parent_names(marker: pytest.Mark) -> list[str]:
    names: list[str] = []
    for parent_test in marker.kwargs.get("tests", []):
        if isinstance(parent_test, dict):
            name = parent_test.get("name")
            if name:
                names.append(name)
        else:
            names.append(parent_test)
    return names


def _topological_sort(graph: dict[str, list[str]], all_names: list[str]) -> list[str]:
    gray: set[str] = set()
    black: set[str] = set()
    order: list[str] = []

    def visit(node: str) -> None:
        if node in black:
            return
        if node in gray:
            logger.warning("pytest-depends-on: Circular dependency detected involving '%s'. Skipping edge.", node)
            return
        gray.add(node)
        for parent in graph.get(node, []):
            visit(parent)
        gray.discard(node)
        black.add(node)
        order.append(node)

    for name in all_names:
        visit(name)

    return order


def pytest_collection_modifyitems(config: Config, items: list[Function]) -> None:
    if not config.getoption("--depends-on") or not config.getoption("--depends-on-reorder"):
        return

    # Keyed by full nodeid to avoid collisions when the same function name exists across modules
    nodeid_to_item: dict[str, Function] = {item.nodeid: item for item in items}

    # Short name -> all nodeids with that name (a dependency declaration can match multiple tests)
    short_name_to_nodeids: dict[str, list[str]] = {}
    for item in items:
        short_name = item.nodeid.split(".py::")[-1]
        short_name_to_nodeids.setdefault(short_name, []).append(item.nodeid)

    graph: dict[str, list[str]] = {item.nodeid: [] for item in items}

    for item in items:
        marker = item.get_closest_marker("depends_on")
        if not marker:
            continue
        for parent_name in _extract_parent_names(marker):
            parent_nodeids = short_name_to_nodeids.get(parent_name, [])
            if not parent_nodeids:
                logger.warning(
                    "pytest-depends-on: Parent '%s' (dependency of '%s') not found in collection. Ignoring.",
                    parent_name,
                    item.nodeid,
                )
            else:
                graph[item.nodeid].extend(parent_nodeids)

    topo_order = _topological_sort(graph, [item.nodeid for item in items])
    items[:] = [nodeid_to_item[nodeid] for nodeid in topo_order if nodeid in nodeid_to_item]


def pytest_configure(config: Config) -> None:
    config.addinivalue_line("markers", "depends_on(name): mark test as dependent on another test")
