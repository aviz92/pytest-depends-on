import pytest

from pytest_depends_on.consts.status import Status


def test_parent_a():
    assert True


def test_parent_b():
    with pytest.raises(AssertionError):
        assert False


def test_parent_c():
    assert True


@pytest.mark.depends_on(tests=[
    {"name": "test_parent_a"},
    {"name": "test_parent_b", "status": Status.FAILED}
], status=Status.PASSED)
def test_child_a():
    assert True


@pytest.mark.depends_on(tests=[
    {"name": "test_parent_a"},
    {"name": "test_parent_b", "status": Status.FAILED}
], status=Status.FAILED)
def test_child_b():  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=[
    {"name": "test_parent_a"},
    {"name": "test_parent_b"}
], status=Status.PASSED)
def test_child_c():  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=[
    {"name": "test_parent_a"},
    {"name": "test_parent_c"}
], status=Status.PASSED)
def test_child_c():
    assert True
