import pytest

from pytest_depends_on.consts.status import Status


def test_parent_a() -> None:
    assert True


def test_parent_b() -> None:
    assert True


@pytest.mark.skip(reason="skip")
def test_parent_c() -> None:  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(
    tests=[{"name": "test_parent_a", "status": Status.PASSED}, {"name": "test_parent_b", "status": Status.PASSED}],
    status=Status.FAILED,
)
def test_child_a() -> None:
    assert True


@pytest.mark.depends_on(
    tests=[{"name": "test_parent_a", "status": Status.PASSED}, {"name": "test_parent_b", "status": Status.FAILED}],
    status=Status.FAILED,
)
def test_child_b() -> None:  # expected to status "SKIPPED"
    assert False


@pytest.mark.depends_on(
    tests=[{"name": "test_parent_a", "status": Status.PASSED}, {"name": "test_parent_c", "status": Status.PASSED}],
    status=Status.FAILED,
)
def test_child_c() -> None:  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(
    tests=[{"name": "test_parent_a"}, {"name": "test_parent_c", "status": Status.PASSED, "allowed_not_run": True}],
    status=Status.PASSED,
)
def test_child_d() -> None:
    assert True


@pytest.mark.depends_on(
    tests=[
        {"name": "test_parent_does_not_exist", "status": Status.FAILED, "allowed_not_run": True},
        "test_parent_a",
    ],
)
def test_child_e() -> None:  # regression: a per-parent "status" override must not leak onto later parents
    assert True
