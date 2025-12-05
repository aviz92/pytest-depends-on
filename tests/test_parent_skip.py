import pytest

from pytest_depends_on.consts.status import Status


@pytest.mark.skip(reason="skip")
def test_parent():  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=["test_parent"], status=Status.PASSED)
def test_child_a():  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=["test_parent"], status=Status.PASSED, allowed_not_run=True)
def test_child_b():
    assert True
