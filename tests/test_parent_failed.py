import pytest

from pytest_depends_on.consts.status import Status


def test_parent():
    with pytest.raises(AssertionError):
        assert False


@pytest.mark.depends_on(tests=["test_parent"], status=Status.PASSED)
def test_child_a():  # expected to status "SKIPPED"
    assert True


@pytest.mark.depends_on(tests=["test_parent"], status=Status.FAILED)
def test_child_b():
    assert True
