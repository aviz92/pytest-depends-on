import pytest
from _pytest.config import Config
from _pytest.fixtures import FixtureRequest
from _pytest.python import Function
from custom_python_logger import get_logger

from pytest_depends_on import LOGGER_NAME
from pytest_depends_on.consts.status import Status

test_results: dict[str, str] = {}
parent_index: dict[str, list[str]] = {}
DEFAULT_ACCEPTED_STATUSES = (Status.PASSED, Status.XPASS)

logger = get_logger(LOGGER_NAME)


def _short_name(nodeid: str) -> str:
    return nodeid.split(".py::")[-1]


def _module_of(nodeid: str) -> str:
    return nodeid.split("::", 1)[0]


def _resolve_parent_nodeids(parent_name: str, requester_nodeid: str) -> list[str]:
    """Resolve a marker's short parent name to full nodeid(s), preferring a match in the
    same test module when the short name is ambiguous across modules."""
    candidates = parent_index.get(parent_name, [])
    if len(candidates) <= 1:
        return candidates

    if same_module := [nodeid for nodeid in candidates if _module_of(nodeid) == _module_of(requester_nodeid)]:
        return same_module

    logger.warning(
        "pytest-depends-on: Parent name '%s' (dependency of '%s') matches multiple tests across modules "
        "(%s) and none in the same module. Using all matches.",
        parent_name,
        requester_nodeid,
        ", ".join(candidates),
    )
    return candidates


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
    if report.when == "setup" and report.failed:
        test_results[item.nodeid] = Status.FAILED
        return
    if report.when != "call":
        return

    if hasattr(report, "wasxfail"):
        if report.skipped:
            test_results[item.nodeid] = Status.XFAILED
        elif report.passed:
            test_results[item.nodeid] = Status.XPASS
    else:
        test_results[item.nodeid] = report.outcome


@pytest.fixture(autouse=True)
def check_dependency(request: FixtureRequest) -> None:
    if not request.config.getoption("--depends-on"):
        return

    if marker := request.node.get_closest_marker("depends_on"):
        default_status = marker.kwargs.get("status")
        default_allowed_not_run = marker.kwargs.get("allowed_not_run", False)
        for parent_test in marker.kwargs.get("tests", []):
            if isinstance(parent_test, dict):
                parent_test_name = parent_test.get("name")
                parent_result_expected = parent_test.get("status", default_status)
                allowed_parent_not_run = parent_test.get("allowed_not_run", default_allowed_not_run)
            else:
                parent_test_name = parent_test
                parent_result_expected = default_status
                allowed_parent_not_run = default_allowed_not_run

            parent_nodeids = _resolve_parent_nodeids(parent_test_name, request.node.nodeid)
            parent_result = next((test_results[nodeid] for nodeid in parent_nodeids if nodeid in test_results), None)

            if allowed_parent_not_run and parent_result is None:
                continue
            if not parent_result:
                pytest.skip(f"Test skipped: Dependency '{parent_test_name}' has not run yet.")

            mismatch = (
                parent_result not in DEFAULT_ACCEPTED_STATUSES
                if parent_result_expected is None
                else parent_result != parent_result_expected
            )
            if mismatch:
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
    if not config.getoption("--depends-on"):
        return

    # Short name -> all nodeids with that name, used to resolve marker parent names at
    # collection and runtime alike (a dependency declaration can match multiple tests).
    parent_index.clear()
    for item in items:
        parent_index.setdefault(_short_name(item.nodeid), []).append(item.nodeid)

    if not config.getoption("--depends-on-reorder"):
        return

    nodeid_to_item: dict[str, Function] = {item.nodeid: item for item in items}
    graph: dict[str, list[str]] = {item.nodeid: [] for item in items}

    for item in items:
        marker = item.get_closest_marker("depends_on")
        if not marker:
            continue
        for parent_name in _extract_parent_names(marker):
            parent_nodeids = _resolve_parent_nodeids(parent_name, item.nodeid)
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
    config.addinivalue_line(
        "markers",
        "depends_on(tests, status=Status.PASSED, allowed_not_run=False): mark test as dependent on other tests",
    )
