import pytest

from pytest_depends_on.consts.status import Status


def test_parent_a():
    assert True


def test_parent_b():
    assert True


@pytest.mark.skip(reason="skip")
def test_parent_c():  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=[
    {"name": "test_parent_a", "status": Status.PASSED},
    {"name": "test_parent_b", "status": Status.PASSED}
], status=Status.FAILED)
def test_child_a():
    assert True


@pytest.mark.depends_on(tests=[
    {"name": "test_parent_a", "status": Status.PASSED},
    {"name": "test_parent_b", "status": Status.FAILED}
], status=Status.FAILED)
def test_child_b():  # expected to status "SKIPPED"
    assert False


@pytest.mark.depends_on(tests=[
    {"name": "test_parent_a", "status": Status.PASSED},
    {"name": "test_parent_c", "status": Status.PASSED}
], status=Status.FAILED)
def test_child_c():  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=[
    {"name": "test_parent_a"},
    {"name": "test_parent_c", "status": Status.PASSED, "allowed_not_run": True}
], status=Status.PASSED)
def test_child_d():
    assert True
