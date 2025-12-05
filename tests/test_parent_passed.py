import pytest

from pytest_depends_on.consts.status import Status


def test_parent():
    assert True


@pytest.mark.depends_on(tests=["test_parent"], status=Status.PASSED)
def test_child_a():
    assert True


@pytest.mark.depends_on(tests=["test_parent"], status=Status.FAILED)
def test_child_b():  # expected to status "SKIPPED"
    assert True
